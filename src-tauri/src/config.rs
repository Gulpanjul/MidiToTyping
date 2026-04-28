//! Persistent config. Schema mirrors src/config.py:32-40.
//! Stored at <app-data>/playSong_config.json via tauri-plugin-store.

use serde::{Deserialize, Serialize};
use tauri::{AppHandle, Runtime};
use tauri_plugin_store::StoreExt;

const STORE_FILE: &str = "playSong_config.json";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub lang: String,    // "id" | "en"
    pub theme: String,   // "dark" | "light"
    pub palette: String, // "celestial" | "grand_piano"
    pub folders: Vec<String>,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            lang: "id".into(),
            theme: "dark".into(),
            palette: "celestial".into(),
            folders: vec![],
        }
    }
}

fn validate(mut c: Config) -> Config {
    if !["id", "en"].contains(&c.lang.as_str()) {
        c.lang = "id".into();
    }
    if !["dark", "light"].contains(&c.theme.as_str()) {
        c.theme = "dark".into();
    }
    if !["celestial", "grand_piano"].contains(&c.palette.as_str()) {
        c.palette = "celestial".into();
    }
    c.folders.retain(|p| !p.is_empty());
    c
}

pub fn load<R: Runtime>(app: &AppHandle<R>) -> Config {
    let Ok(store) = app.store(STORE_FILE) else {
        return Config::default();
    };
    let lang = store
        .get("lang")
        .and_then(|v| v.as_str().map(String::from))
        .unwrap_or_else(|| "id".into());
    let theme = store
        .get("theme")
        .and_then(|v| v.as_str().map(String::from))
        .unwrap_or_else(|| "dark".into());
    let palette = store
        .get("palette")
        .and_then(|v| v.as_str().map(String::from))
        .unwrap_or_else(|| "celestial".into());
    let folders = store
        .get("folders")
        .and_then(|v| v.as_array().cloned())
        .map(|arr| {
            arr.into_iter()
                .filter_map(|x| x.as_str().map(String::from))
                .collect()
        })
        .unwrap_or_default();
    validate(Config {
        lang,
        theme,
        palette,
        folders,
    })
}

pub fn save<R: Runtime>(app: &AppHandle<R>, c: &Config) -> Result<(), String> {
    let store = app.store(STORE_FILE).map_err(|e| e.to_string())?;
    let c = validate(c.clone());
    store.set("lang", serde_json::Value::String(c.lang));
    store.set("theme", serde_json::Value::String(c.theme));
    store.set("palette", serde_json::Value::String(c.palette));
    store.set(
        "folders",
        serde_json::Value::Array(
            c.folders
                .into_iter()
                .map(serde_json::Value::String)
                .collect(),
        ),
    );
    store.save().map_err(|e| e.to_string())
}
