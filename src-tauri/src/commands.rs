use crate::config::{self, Config};
use crate::injector::EnigoInjector;
use crate::midi::{self, NoteSchedule};
use crate::platform;
use crate::playback::{PlaybackEngine, PlaybackState, StateSink};
use serde::Serialize;
use std::path::{Path, PathBuf};
use std::sync::Arc;
use tauri::{AppHandle, Emitter, Runtime, State};

pub struct TauriSink<R: Runtime> {
    handle: AppHandle<R>,
}
impl<R: Runtime> StateSink for TauriSink<R> {
    fn emit_state(&self, s: &PlaybackState) {
        let _ = self.handle.emit("playback:state", s);
    }
    fn emit_done(&self) {
        let _ = self.handle.emit("playback:done", ());
    }
    fn emit_tick(&self, index: usize, key: &str) {
        let _ = self.handle.emit(
            "playback:tick",
            serde_json::json!({"index": index, "key": key}),
        );
    }
}

pub struct AppState {
    pub engine: PlaybackEngine,
}

impl AppState {
    pub fn new<R: Runtime>(handle: AppHandle<R>) -> Result<Self, String> {
        let inj = Arc::new(EnigoInjector::new()?);
        let sink = Arc::new(TauriSink { handle });
        Ok(Self {
            engine: PlaybackEngine::new(inj, sink),
        })
    }
}

#[derive(Serialize)]
pub struct MidiFile {
    pub name: String,
    pub size: u64,
    pub path: String,
}

#[tauri::command]
pub fn list_midis_in_folder(path: String) -> Result<Vec<MidiFile>, String> {
    let p = Path::new(&path);
    let rd = std::fs::read_dir(p).map_err(|e| e.to_string())?;
    let mut out = Vec::new();
    for entry in rd.flatten() {
        let name = entry.file_name().to_string_lossy().to_string();
        let lower = name.to_lowercase();
        if !(lower.ends_with(".mid") || lower.ends_with(".midi")) {
            continue;
        }
        let meta = entry.metadata().map_err(|e| e.to_string())?;
        out.push(MidiFile {
            name,
            size: meta.len(),
            path: entry.path().to_string_lossy().to_string(),
        });
    }
    out.sort_by(|a, b| a.name.to_lowercase().cmp(&b.name.to_lowercase()));
    Ok(out)
}

#[tauri::command]
pub fn parse_midi(path: String) -> Result<NoteSchedule, String> {
    midi::parse_midi(&PathBuf::from(path)).map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn load_song(
    state: State<'_, AppState>,
    path: String,
) -> Result<PlaybackState, String> {
    let sched = midi::parse_midi(&PathBuf::from(&path)).map_err(|e| e.to_string())?;
    state.engine.load(sched, Some(path)).await;
    Ok(state.engine.snapshot().await)
}

#[tauri::command]
pub async fn play(state: State<'_, AppState>) -> Result<(), ()> {
    state.engine.play().await;
    Ok(())
}

#[tauri::command]
pub async fn pause(state: State<'_, AppState>) -> Result<(), ()> {
    state.engine.pause().await;
    Ok(())
}

#[tauri::command]
pub async fn toggle(state: State<'_, AppState>) -> Result<bool, ()> {
    Ok(state.engine.toggle().await)
}

#[tauri::command]
pub async fn seek(state: State<'_, AppState>, delta: i64) -> Result<usize, ()> {
    Ok(state.engine.seek(delta).await)
}

#[tauri::command]
pub async fn restart(state: State<'_, AppState>) -> Result<(), ()> {
    state.engine.restart().await;
    Ok(())
}

#[tauri::command]
pub async fn set_speed(state: State<'_, AppState>, speed: f64) -> Result<(), ()> {
    state.engine.set_speed(speed).await;
    Ok(())
}

#[tauri::command]
pub async fn get_state(state: State<'_, AppState>) -> Result<PlaybackState, ()> {
    Ok(state.engine.snapshot().await)
}

#[tauri::command]
pub fn get_config<R: Runtime>(app: AppHandle<R>) -> Config {
    config::load(&app)
}

#[tauri::command]
pub fn set_config<R: Runtime>(app: AppHandle<R>, cfg: Config) -> Result<(), String> {
    config::save(&app, &cfg)
}

#[tauri::command]
pub fn is_playback_supported() -> bool {
    platform::is_playback_supported()
}
