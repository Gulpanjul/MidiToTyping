//! Global hotkeys (Windows-only at v1). Mirrors legacy/playSong_clean.py:15-50.

use crate::commands::AppState;
use tauri::{AppHandle, Emitter, Manager, Runtime};
use tauri_plugin_global_shortcut::{Code, GlobalShortcutExt, Shortcut, ShortcutState};

pub fn register<R: Runtime>(app: &AppHandle<R>) -> Result<(), Box<dyn std::error::Error>> {
    let gs = app.global_shortcut();

    let app_for_handler = app.clone();
    gs.on_shortcut(Shortcut::new(None, Code::Delete), move |_app, _sc, ev| {
        if ev.state() != ShortcutState::Pressed {
            return;
        }
        let h = app_for_handler.clone();
        tauri::async_runtime::spawn(async move {
            let state: tauri::State<AppState> = h.state();
            let now = state.engine.toggle().await;
            let _ = h.emit(
                "hotkey:fired",
                serde_json::json!({"which": "play_pause", "is_playing": now}),
            );
        });
    })?;

    let app_for_handler = app.clone();
    gs.on_shortcut(Shortcut::new(None, Code::Home), move |_a, _s, ev| {
        if ev.state() != ShortcutState::Pressed {
            return;
        }
        let h = app_for_handler.clone();
        tauri::async_runtime::spawn(async move {
            let state: tauri::State<AppState> = h.state();
            let _ = state.engine.seek(-(crate::playback::SEEK_STEP)).await;
            let _ = h.emit("hotkey:fired", serde_json::json!({"which": "rewind"}));
        });
    })?;

    let app_for_handler = app.clone();
    gs.on_shortcut(Shortcut::new(None, Code::End), move |_a, _s, ev| {
        if ev.state() != ShortcutState::Pressed {
            return;
        }
        let h = app_for_handler.clone();
        tauri::async_runtime::spawn(async move {
            let state: tauri::State<AppState> = h.state();
            let _ = state.engine.seek(crate::playback::SEEK_STEP).await;
            let _ = h.emit("hotkey:fired", serde_json::json!({"which": "skip"}));
        });
    })?;

    let app_for_handler = app.clone();
    gs.on_shortcut(Shortcut::new(None, Code::Insert), move |_a, _s, ev| {
        if ev.state() != ShortcutState::Pressed {
            return;
        }
        let h = app_for_handler.clone();
        tauri::async_runtime::spawn(async move {
            let state: tauri::State<AppState> = h.state();
            state.engine.restart().await;
            let _ = h.emit("hotkey:fired", serde_json::json!({"which": "restart"}));
        });
    })?;

    Ok(())
}
