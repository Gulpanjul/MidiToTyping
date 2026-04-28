//! MIDI parsing via `midly`. Output mirrors src/midi_parser.py +
//! src/playback.py:parse_info -- events carry per-note delays in seconds
//! at 1.0x speed, ready for the playback engine to scale by speed.

use crate::mapping::midi_pitch_to_key;
use midly::{MetaMessage, MidiMessage, Smf, Timing, TrackEventKind};
use serde::Serialize;
use std::path::Path;

#[derive(Debug, Serialize, Clone)]
pub struct NoteEvent {
    /// Seconds to wait *after* this event before firing the next.
    pub delay_secs: f64,
    /// Concatenated keystrokes. Prefix '~' = release; otherwise press all chars.
    pub keys: String,
}

#[derive(Debug, Serialize, Clone)]
pub struct NoteSchedule {
    pub initial_tempo_bpm: f64,
    pub events: Vec<NoteEvent>,
}

#[derive(Debug, thiserror::Error)]
pub enum MidiError {
    #[error("io: {0}")]
    Io(#[from] std::io::Error),
    #[error("parse: {0}")]
    Parse(String),
}

pub fn parse_midi(path: &Path) -> Result<NoteSchedule, MidiError> {
    let bytes = std::fs::read(path)?;
    let smf = Smf::parse(&bytes).map_err(|e| MidiError::Parse(e.to_string()))?;

    let ticks_per_beat = match smf.header.timing {
        Timing::Metrical(tpb) => u32::from(u16::from(tpb)) as f64,
        Timing::Timecode(_, _) => {
            return Err(MidiError::Parse("SMPTE timing not supported".into()));
        }
    };

    // Merge tracks by absolute tick (mirrors mido.merge_tracks).
    #[derive(Debug)]
    struct Ev {
        abs_tick: u64,
        kind: EvKind,
    }
    #[derive(Debug)]
    enum EvKind {
        Note { release: bool, key: char },
        Tempo { bpm: f64 },
    }

    let mut merged: Vec<Ev> = Vec::new();
    for track in &smf.tracks {
        let mut abs_tick: u64 = 0;
        for ev in track {
            abs_tick += u32::from(ev.delta) as u64;
            match ev.kind {
                TrackEventKind::Meta(MetaMessage::Tempo(us_per_beat)) => {
                    let bpm = 60_000_000.0 / u32::from(us_per_beat) as f64;
                    merged.push(Ev {
                        abs_tick,
                        kind: EvKind::Tempo { bpm },
                    });
                }
                TrackEventKind::Midi {
                    message: MidiMessage::NoteOn { key, vel },
                    ..
                } => {
                    let release = u8::from(vel) == 0;
                    let ch = midi_pitch_to_key(u8::from(key));
                    merged.push(Ev {
                        abs_tick,
                        kind: EvKind::Note { release, key: ch },
                    });
                }
                TrackEventKind::Midi {
                    message: MidiMessage::NoteOff { key, .. },
                    ..
                } => {
                    let ch = midi_pitch_to_key(u8::from(key));
                    merged.push(Ev {
                        abs_tick,
                        kind: EvKind::Note {
                            release: true,
                            key: ch,
                        },
                    });
                }
                _ => {}
            }
        }
    }
    merged.sort_by_key(|e| e.abs_tick);

    enum Row {
        Tempo(f64),
        Notes(u64, String),
    }
    let mut rows: Vec<Row> = Vec::new();
    let mut initial_tempo_bpm = 120.0_f64;
    let mut tempo_seen = false;

    // Group simultaneous notes (same abs_tick) into one keys string.
    let mut i = 0;
    while i < merged.len() {
        let t = merged[i].abs_tick;
        let mut group_press = String::new();
        let mut group_release = String::new();
        let mut tempo_at_t: Option<f64> = None;
        while i < merged.len() && merged[i].abs_tick == t {
            match merged[i].kind {
                EvKind::Tempo { bpm } => tempo_at_t = Some(bpm),
                EvKind::Note { release, key } => {
                    if release {
                        group_release.push(key);
                    } else {
                        group_press.push(key);
                    }
                }
            }
            i += 1;
        }
        if let Some(bpm) = tempo_at_t {
            if !tempo_seen {
                initial_tempo_bpm = bpm;
                tempo_seen = true;
            }
            rows.push(Row::Tempo(bpm));
        }
        if !group_press.is_empty() {
            rows.push(Row::Notes(t, group_press));
        }
        if !group_release.is_empty() {
            rows.push(Row::Notes(t, format!("~{group_release}")));
        }
    }

    // Replicate src/playback.py:parse_info -- convert absolute ticks to
    // per-event delays in SECONDS at 1.0x speed.
    // Note delays: (next_tick - this_tick) / ticks_per_beat * (60 / bpm)
    let mut events: Vec<NoteEvent> = Vec::new();
    let mut current_bpm = initial_tempo_bpm;
    let mut last_note: Option<usize> = None; // index into events of last note row
    let mut last_tick: Option<u64> = None;

    for row in rows {
        match row {
            Row::Tempo(bpm) => {
                current_bpm = bpm;
            }
            Row::Notes(tick, keys) => {
                if let (Some(prev_tick), Some(prev_idx)) = (last_tick, last_note) {
                    let beat_delta = (tick - prev_tick) as f64 / ticks_per_beat;
                    let secs = beat_delta * 60.0 / current_bpm;
                    events[prev_idx].delay_secs = secs;
                }
                events.push(NoteEvent {
                    delay_secs: 1.0,
                    keys,
                });
                last_note = Some(events.len() - 1);
                last_tick = Some(tick);
            }
        }
    }
    // Last event keeps default 1.0s tail (mirrors Python's note[0] = 1.0 fallback).

    Ok(NoteSchedule {
        initial_tempo_bpm,
        events,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    fn fixture() -> PathBuf {
        PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("tests")
            .join("fixtures")
            .join("sample.mid")
    }

    #[test]
    fn parses_fixture_into_nonempty_schedule() {
        let s = parse_midi(&fixture()).expect("fixture parses");
        assert!(!s.events.is_empty(), "expected at least one note event");
        assert!(s.initial_tempo_bpm > 0.0);
    }

    #[test]
    fn every_event_has_nonneg_delay() {
        let s = parse_midi(&fixture()).expect("fixture parses");
        for ev in &s.events {
            assert!(ev.delay_secs >= 0.0, "negative delay: {}", ev.delay_secs);
        }
    }

    #[test]
    fn release_events_carry_tilde_prefix() {
        let s = parse_midi(&fixture()).expect("fixture parses");
        let has_release = s.events.iter().any(|e| e.keys.starts_with('~'));
        assert!(has_release, "expected at least one release event");
    }
}
