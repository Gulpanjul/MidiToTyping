mod mapping;
mod injector;
mod midi;
mod playback;
mod config;
mod platform;
mod commands;
mod hotkeys;

use commands::AppState;
use tauri::Manager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    platform::begin_high_resolution_timer();
    let result = tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_store::Builder::new().build())
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .plugin(tauri_plugin_os::init())
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let handle = app.handle().clone();
            let state = AppState::new(handle.clone())?;
            app.manage(state);
            #[cfg(windows)]
            hotkeys::register(&handle)?;
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::list_midis_in_folder,
            commands::parse_midi,
            commands::load_song,
            commands::play,
            commands::pause,
            commands::toggle,
            commands::seek,
            commands::restart,
            commands::set_speed,
            commands::get_state,
            commands::get_config,
            commands::set_config,
            commands::is_playback_supported,
        ])
        .run(tauri::generate_context!());
    platform::end_high_resolution_timer();
    result.expect("error while running playSong");
}
