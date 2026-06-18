//! Global hotkeys (Windows-only at v1). Mirrors legacy/playSong_clean.py:15-50.

use crate::commands::AppState;
use crate::playback::SEEK_STEP;
use tauri::{AppHandle, Emitter, Manager, Runtime};
use tauri_plugin_global_shortcut::{Code, GlobalShortcutExt, Shortcut, ShortcutState};

/// Register one global shortcut. On key-press it runs `body` against the
/// playback engine (bound in scope as `engine`) and emits the JSON the body
/// returns as `hotkey:fired`. Collapses four near-identical handlers; the
/// Play/Pause case keeps its extra `is_playing` field in the payload.
macro_rules! hotkey {
    ($gs:expr, $app:expr, $code:expr, |$engine:ident| $body:block) => {{
        let app_for_handler = $app.clone();
        $gs.on_shortcut(Shortcut::new(None, $code), move |_a, _s, ev| {
            if ev.state() != ShortcutState::Pressed {
                return;
            }
            let h = app_for_handler.clone();
            tauri::async_runtime::spawn(async move {
                let state: tauri::State<AppState> = h.state();
                let $engine = &state.engine;
                let payload = $body;
                let _ = h.emit("hotkey:fired", payload);
            });
        })?;
    }};
}

pub fn register<R: Runtime>(app: &AppHandle<R>) -> Result<(), Box<dyn std::error::Error>> {
    let gs = app.global_shortcut();

    hotkey!(gs, app, Code::Delete, |engine| {
        let now = engine.toggle().await;
        serde_json::json!({"which": "play_pause", "is_playing": now})
    });
    hotkey!(gs, app, Code::Home, |engine| {
        engine.seek(-SEEK_STEP).await;
        serde_json::json!({"which": "rewind"})
    });
    hotkey!(gs, app, Code::End, |engine| {
        engine.seek(SEEK_STEP).await;
        serde_json::json!({"which": "skip"})
    });
    hotkey!(gs, app, Code::Insert, |engine| {
        engine.restart().await;
        serde_json::json!({"which": "restart"})
    });

    Ok(())
}
