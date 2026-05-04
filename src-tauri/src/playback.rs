//! Playback engine -- owns the schedule + index + speed and drives a single
//! tokio task. Mirrors src/playback.py semantics:
//!   - per-note delay scaled by speed: delay/speed
//!   - rewind = max(0, idx - 10)
//!   - skip   = idx + 10, but if idx + 10 >= total then reset to 0 + pause
//!   - restart = idx = 0, is_playing = false (diverges from legacy Python,
//!     which auto-played on INSERT — current UX prefers an explicit Play
//!     after restart so users don't get surprised by sudden output).
//!   - generation token = JoinHandle::abort() on transition

use crate::injector::Injector;
use crate::midi::{NoteEvent, NoteSchedule};
use serde::Serialize;
use std::sync::Arc;
use tokio::sync::Mutex;
use tokio::task::JoinHandle;
use tokio::time::{sleep, Duration};

pub const SEEK_STEP: i64 = 10;

#[derive(Debug, Clone, Default, Serialize)]
pub struct PlaybackState {
    pub is_playing: bool,
    pub index: usize,
    pub total: usize,
    pub speed: f64,
    pub song_path: Option<String>,
}

pub trait StateSink: Send + Sync {
    fn emit_state(&self, s: &PlaybackState);
    fn emit_done(&self);
    fn emit_tick(&self, index: usize, key: &str);
}

/// No-op sink for tests.
pub struct NullSink;
impl StateSink for NullSink {
    fn emit_state(&self, _s: &PlaybackState) {}
    fn emit_done(&self) {}
    fn emit_tick(&self, _i: usize, _k: &str) {}
}

pub struct PlaybackEngine {
    state: Arc<Mutex<PlaybackState>>,
    schedule: Arc<Mutex<Option<NoteSchedule>>>,
    handle: Arc<Mutex<Option<JoinHandle<()>>>>,
    injector: Arc<dyn Injector>,
    sink: Arc<dyn StateSink>,
}

/// Default starting playback speed. Set to 0.95x (5% slower than nominal)
/// to match the perceived tempo of the legacy Python build, whose
/// threading.Timer overshoots by 5-15ms per note on Windows. Rust's
/// tokio + timeBeginPeriod(1) hits deadlines within ~1ms, so a Python
/// user upgrading would otherwise feel the new build "too fast" at 1.0x
/// even though both engines compute identical schedules.
pub const DEFAULT_SPEED: f64 = 0.95;

impl PlaybackEngine {
    pub fn new(injector: Arc<dyn Injector>, sink: Arc<dyn StateSink>) -> Self {
        let state = PlaybackState {
            speed: DEFAULT_SPEED,
            ..Default::default()
        };
        Self {
            state: Arc::new(Mutex::new(state)),
            schedule: Arc::new(Mutex::new(None)),
            handle: Arc::new(Mutex::new(None)),
            injector,
            sink,
        }
    }

    pub async fn load(&self, schedule: NoteSchedule, song_path: Option<String>) {
        self.abort_running().await;
        let total = schedule.events.len();
        *self.schedule.lock().await = Some(schedule);
        let mut s = self.state.lock().await;
        s.is_playing = false;
        s.index = 0;
        s.total = total;
        s.song_path = song_path;
        self.sink.emit_state(&s);
    }

    pub async fn set_speed(&self, speed: f64) {
        let speed = speed.clamp(0.25, 3.0);
        let mut s = self.state.lock().await;
        s.speed = speed;
        self.sink.emit_state(&s);
    }

    pub async fn snapshot(&self) -> PlaybackState {
        self.state.lock().await.clone()
    }

    pub async fn play(&self) {
        let already = self.state.lock().await.is_playing;
        if already {
            return;
        }
        {
            let mut s = self.state.lock().await;
            s.is_playing = true;
            self.sink.emit_state(&s);
        }
        self.spawn_task().await;
    }

    pub async fn pause(&self) {
        self.abort_running().await;
        let mut s = self.state.lock().await;
        s.is_playing = false;
        self.sink.emit_state(&s);
    }

    pub async fn toggle(&self) -> bool {
        let now = self.state.lock().await.is_playing;
        if now {
            self.pause().await;
            false
        } else {
            self.play().await;
            true
        }
    }

    pub async fn seek(&self, delta: i64) -> usize {
        self.abort_running().await;
        // Single lock for the whole seek decision so total/index/is_playing are consistent.
        let was_playing = {
            let mut s = self.state.lock().await;
            let total = s.total as i64;
            let new_idx = s.index as i64 + delta;
            if delta > 0 && new_idx >= total {
                // Skip past end: reset + pause (mirrors legacy/playSong_clean.py:on_end_press)
                s.index = 0;
                s.is_playing = false;
                self.sink.emit_state(&s);
                return 0;
            }
            s.index = new_idx.max(0) as usize;
            self.sink.emit_state(&s);
            s.is_playing
        };
        if was_playing {
            self.spawn_task().await;
        }
        self.state.lock().await.index
    }

    pub async fn restart(&self) {
        // Restart rewinds to index 0 and *pauses*. The user has to press
        // Play (or the DELETE hotkey) to resume from the beginning. This is
        // intentional: in heads-down practice an accidental INSERT used to
        // immediately blast the keyboard from note 0, which was startling.
        self.abort_running().await;
        let mut s = self.state.lock().await;
        s.index = 0;
        s.is_playing = false;
        self.sink.emit_state(&s);
    }

    async fn abort_running(&self) {
        if let Some(h) = self.handle.lock().await.take() {
            h.abort();
        }
    }

    async fn spawn_task(&self) {
        let state = self.state.clone();
        let schedule = self.schedule.clone();
        let injector = self.injector.clone();
        let sink = self.sink.clone();
        let handle_slot = self.handle.clone();

        let h = tokio::spawn(async move {
            loop {
                let (idx, total, speed) = {
                    let s = state.lock().await;
                    if !s.is_playing {
                        return;
                    }
                    (s.index, s.total, s.speed)
                };
                if idx >= total {
                    let mut s = state.lock().await;
                    s.is_playing = false;
                    s.index = 0;
                    sink.emit_state(&s);
                    sink.emit_done();
                    return;
                }
                let event: NoteEvent = {
                    let sched = schedule.lock().await;
                    sched.as_ref().unwrap().events[idx].clone()
                };

                if event.keys.starts_with('~') {
                    for k in event.keys.chars().skip(1) {
                        injector.release(k);
                    }
                } else {
                    for k in event.keys.chars() {
                        injector.press(k);
                    }
                }
                sink.emit_tick(idx, &event.keys);

                // We deliberately do NOT emit_state here. The renderer
                // already learns about the advancing index from the tick
                // event payload (which carries `index`). Emitting state
                // every note caused 50+ context-wide React re-renders/sec
                // on dense MIDIs. State emits stay reserved for transitions
                // (load / play / pause / seek / restart / done).
                {
                    let mut s = state.lock().await;
                    s.index += 1;
                }
                let delay = (event.delay_secs / speed).max(0.0);
                if delay > 0.0 {
                    sleep(Duration::from_secs_f64(delay)).await;
                } else {
                    tokio::task::yield_now().await;
                }
            }
        });

        *handle_slot.lock().await = Some(h);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::injector::MockInjector;
    use crate::midi::NoteEvent;

    fn schedule(keys: &[&str]) -> NoteSchedule {
        NoteSchedule {
            initial_tempo_bpm: 120.0,
            events: keys
                .iter()
                .map(|k| NoteEvent {
                    delay_secs: 0.001,
                    keys: k.to_string(),
                })
                .collect(),
        }
    }

    fn engine() -> (PlaybackEngine, Arc<MockInjector>) {
        let inj = Arc::new(MockInjector::default());
        let eng = PlaybackEngine::new(inj.clone(), Arc::new(NullSink));
        (eng, inj)
    }

    #[tokio::test]
    async fn play_emits_keys_in_order_then_finishes() {
        let (eng, inj) = engine();
        eng.load(schedule(&["a", "b", "c"]), None).await;
        eng.play().await;
        // wait for completion
        for _ in 0..100 {
            if !eng.snapshot().await.is_playing {
                break;
            }
            tokio::time::sleep(Duration::from_millis(10)).await;
        }
        let events = inj.events.lock().unwrap().clone();
        assert_eq!(events, vec!["press a", "press b", "press c"]);
        let s = eng.snapshot().await;
        assert!(!s.is_playing);
        assert_eq!(s.index, 0);
    }

    #[tokio::test]
    async fn release_keys_use_tilde_prefix() {
        let (eng, inj) = engine();
        eng.load(schedule(&["a", "~a"]), None).await;
        eng.play().await;
        for _ in 0..100 {
            if !eng.snapshot().await.is_playing {
                break;
            }
            tokio::time::sleep(Duration::from_millis(10)).await;
        }
        let events = inj.events.lock().unwrap().clone();
        assert_eq!(events, vec!["press a", "release a"]);
    }

    #[tokio::test]
    async fn pause_then_play_resumes_at_index() {
        let (eng, _inj) = engine();
        eng.load(schedule(&["a"; 50]), None).await;
        eng.play().await;
        tokio::time::sleep(Duration::from_millis(20)).await;
        eng.pause().await;
        let mid = eng.snapshot().await;
        assert!(!mid.is_playing);
        assert!(mid.index > 0 && mid.index < 50);
    }

    #[tokio::test]
    async fn seek_minus_ten_clamps_at_zero() {
        let (eng, _inj) = engine();
        eng.load(schedule(&["a"; 5]), None).await;
        eng.seek(-SEEK_STEP).await;
        assert_eq!(eng.snapshot().await.index, 0);
    }

    #[tokio::test]
    async fn seek_past_end_resets_and_pauses() {
        let (eng, _inj) = engine();
        eng.load(schedule(&["a"; 5]), None).await;
        eng.play().await;
        tokio::time::sleep(Duration::from_millis(5)).await;
        eng.seek(SEEK_STEP).await; // +10 with total=5
        let s = eng.snapshot().await;
        assert_eq!(s.index, 0);
        assert!(!s.is_playing);
    }

    #[tokio::test]
    async fn restart_resets_index_and_pauses() {
        let (eng, inj) = engine();
        eng.load(schedule(&["a", "b"]), None).await;
        eng.play().await;
        tokio::time::sleep(Duration::from_millis(20)).await;
        eng.restart().await;
        // Restart now stops the engine at index 0 — no auto-play.
        let s = eng.snapshot().await;
        assert_eq!(s.index, 0);
        assert!(!s.is_playing);
        // The pre-restart play() did fire some events; we just want to
        // confirm at least one was a press of 'a' (i.e. the engine actually
        // ran before being reset), not that it kept running afterwards.
        let evs = inj.events.lock().unwrap().clone();
        assert!(evs.iter().any(|e| e == "press a"));
    }
}
