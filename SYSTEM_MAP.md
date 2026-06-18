<!--
Purpose: One-shot architecture compass for the Tauri build (primary) — main navigation without a blind scan.
Caller: Claude Code / developer at session start (Mandatory Map Check).
Dependencies: app/ (React 19 + Vite), src-tauri/ (Rust + Tauri v2).
Scope: the active Tauri build. Legacy Python (legacy/) has its own map.
Sync: update the relevant section whenever files are added/removed or a main flow changes.
-->

# SYSTEM_MAP.md — playSong (Tauri build)

> Created: 2026-06-15 · App version: `0.2.0` (Cargo.toml + tauri.conf.json) · Entry: `src-tauri/src/main.rs` → `lib::run()` · Frontend entry: `app/src/main.tsx`
> Note: `legacy/` (Python, reference archive) has a separate map at [legacy/docs/SYSTEM_MAP.md](legacy/docs/SYSTEM_MAP.md) — not mapped here.

---

# Project Summary

**Purpose:** Convert MIDI files into automated keyboard-press simulation for keyboard-based piano games (_Sky: Children of the Light_, _Piano Tiles_). The user picks a folder of `.mid`/`.midi` files, selects a song, sets the speed, then the engine presses keys per the MIDI timing into the currently focused game window.

**Main tech stack:**

| Layer | Detail |
|---|---|
| Desktop shell | Tauri v2 (Rust `2.10.3` resolved; `tauri-build`, plugins dialog/fs/store/global-shortcut/os/shell) |
| Frontend | React 19 + TypeScript (strict) + Vite 6 + Tailwind v4 |
| Async backend | tokio (rt-multi-thread) — single-task playback engine |
| MIDI parse | `midly` 0.5 (zero-copy) |
| Keyboard inject | `enigo` 0.3 (`SendInput`, standard user, no admin) |
| Global hotkeys | `tauri-plugin-global-shortcut` (`SetWindowsHookEx WH_KEYBOARD_LL`) |
| Persist config | `tauri-plugin-store` → `playSong_config.json` |
| Platform timing | `windows` crate `timeBeginPeriod(1)` (Windows-only) |
| DB / queue / external API | Not found (local app, no network backend) |

**Architecture pattern:** Two-layer desktop. **React UI** (state via 2 Contexts: Config + Playback) ↔ **Rust core** over Tauri IPC (`invoke` commands + `emit` events). The core uses **trait abstractions** (`Injector`, `StateSink`) so `PlaybackEngine` is testable without the real OS. No classic Controller/Service/Repo layers → closest mapping: **Tauri command = handler**, **PlaybackEngine/midi/injector = service**, **config.rs + fs = data access**, **store JSON + filesystem + OS input = storage/sink**.

---

# Core Logic Flow (Function-Level Flowchart)

**Startup (Rust → Frontend)**
`main()[main.rs] -> playsong_lib::run()[lib.rs] -> platform::begin_high_resolution_timer() -> tauri::Builder(+6 plugins) -> setup[lib.rs]{ AppState::new()[commands.rs] -> EnigoInjector::new()[injector.rs] + TauriSink ; app.manage(state) ; hotkeys::register()[hotkeys.rs] }`
`main.tsx -> App -> ConfigProvider(api.getConfig -> get_config[commands.rs] -> config::load) + PlaybackProvider(api.getState) -> Shell(useTheme->applyTheme, api.isPlaybackSupported) -> Splash auto-hides when ready`

**Pick folder & list songs**
`FolderPane.handleAdd()[dialog open] -> ConfigContext.setConfig(folders) -> api.setConfig -> set_config[commands.rs] -> config::save -> store.save() ; onSelectFolder -> MusicPane.effect -> api.listMidisInFolder -> list_midis_in_folder[commands.rs] -> fs::read_dir (1 level, filter .mid/.midi, sort) -> render table`

**Load & arm a song (core)**
`MusicPane.onPlayFile / BottomBar.onPlay -> App.onPlay() -> PlaybackContext.loadSong -> api.loadSong -> load_song[commands.rs] -> midi::parse_midi()[midi.rs] (midly Smf::parse -> merge tracks by abs_tick -> group simultaneous notes -> compute per-event delay in seconds) -> engine.load()[playback.rs] (arm, is_playing=false, index=0) -> PlaybackState -> PlayerSheet opens (paused)`

**Run playback (loop)**
`DELETE hotkey / Play button -> engine.toggle()|play()[playback.rs] -> spawn_task() tokio loop { read (idx,total,speed) -> take event -> injector.press()|release()[injector.rs] -> enigo.key() -> OS SendInput ; sink.emit_tick("playback:tick") -> PlaybackProvider rAF-coalesces index + PlayerSheet log O(1) ; index+=1 ; sleep(delay/speed) } -> done: emit "playback:done"`

**Global hotkeys (Windows)**
`OS key DELETE/HOME/END/INSERT -> global-shortcut -> hotkeys::on_shortcut[hotkeys.rs] -> engine.toggle|seek(±SEEK_STEP)|restart -> emit "hotkey:fired" + playback event`

**Change theme/palette/language**
`Header.SegToggle.onChange -> ConfigContext.setConfig(patch) -> api.setConfig -> set_config -> config::save ; useTheme.effect -> applyTheme(palette,theme)[themes.ts] -> set CSS vars on :root`

---

# Clean Tree

> Excluded (per rule): `node_modules/`, `target/`, `gen/`, `dist/`, `dist_nuitka/`, `build/`, `.git/`, `__pycache__/`, `archive/`, `legacy/` (has its own map), `*.log`, `*.lock`, `*.map`.

```
MidiToTyping/
├── app/                              # Frontend Vite + React 19 + TS
│   ├── index.html
│   ├── package.json · vite.config.ts · tsconfig*.json
│   ├── playwright.config.ts · e2e/    # Playwright E2E
│   ├── public/playsong-icon.png
│   └── src/
│       ├── main.tsx                  # ReactDOM bootstrap (StrictMode)
│       ├── App.tsx                   # Shell + providers + state orchestration
│       ├── types.ts                  # TS mirror of Rust structs
│       ├── lib/tauri.ts              # invoke/listen wrappers (IPC seam)
│       ├── lib/difficulty.ts         # speed -> difficulty label
│       ├── contexts/{ConfigContext,PlaybackContext}.tsx
│       ├── hooks/{useConfig,usePlayback,useTheme}.ts
│       ├── i18n/strings.ts           # id/en bundle + fmt()
│       ├── theme/themes.ts           # THEMES (2 palettes × 2 modes) + applyTheme
│       └── components/
│           ├── TitleBar.tsx · Header.tsx · FolderPane.tsx
│           ├── MusicPane.tsx · BottomBar.tsx · PlayerSheet.tsx
│           ├── InfoPopup.tsx · Splash.tsx · UnsupportedBanner.tsx
│           └── ui/{Button,Dialog,Slider,Input,MarqueeText}.tsx
│
├── src-tauri/                        # Backend Tauri v2 (Rust)
│   ├── Cargo.toml · build.rs · tauri.conf.json
│   ├── capabilities/default.json     # Main-window permission whitelist
│   ├── icons/
│   ├── tests/                        # fixtures + integration tests
│   └── src/
│       ├── main.rs                   # Thin entry -> lib::run()
│       ├── lib.rs                    # Builder, plugin + command registration
│       ├── commands.rs               # 13 #[tauri::command] + TauriSink
│       ├── playback.rs               # PlaybackEngine + StateSink trait
│       ├── injector.rs               # Injector trait + Enigo/Mock + whitelist
│       ├── midi.rs                   # parse_midi() midly -> NoteSchedule
│       ├── mapping.rs                # SCALE 61-key + midi_pitch_to_key()
│       ├── config.rs                 # load/save/validate Config (store)
│       ├── platform.rs               # timer resolution + is_playback_supported
│       └── hotkeys.rs                # register DELETE/HOME/END/INSERT
│
├── docs/                             # Project docs (superpowers/plans)
├── CLAUDE.md · README.md · .gitignore
└── SYSTEM_MAP.md                     # this file
```

---

# Module Map (The Chapters)

### Backend — `src-tauri/src/`

| Path | Main public functions/structs | Role |
|---|---|---|
| `main.rs` | `main()` | Binary entry; calls `playsong_lib::run()`. |
| `lib.rs` | `run()` | Build the Tauri builder, register 6 plugins + 13 commands, set up state & hotkeys. |
| `commands.rs` | 13 `#[command]` (`list_midis_in_folder`, `parse_midi`, `load_song`, `play`, `pause`, `toggle`, `seek`, `restart`, `set_speed`, `get_state`, `get_config`, `set_config`, `is_playback_supported`), `AppState`, `TauriSink` | IPC surface; bridges command→engine and engine→event (`playback:state/tick/done`). |
| `playback.rs` | `PlaybackEngine` (`load/play/pause/toggle/seek/restart/set_speed/snapshot`), `StateSink` trait, `NullSink`, `PlaybackState`, `DEFAULT_SPEED=0.95`, `SEEK_STEP=10` | Core engine: single tokio task, cancel via `JoinHandle::abort`, scale delay by speed. |
| `injector.rs` | `Injector` trait, `EnigoInjector`, `MockInjector`, `is_allowed/is_shifted/shifted_to_base`, `ALLOWED` | Synthesize keypresses to the OS + whitelist & shift-map (verbatim port from Python). |
| `midi.rs` | `parse_midi()`, `NoteSchedule`, `NoteEvent`, `MidiError` | Parse MIDI: merge tracks, group simultaneous notes per tick, compute per-event delay in seconds @1.0×. |
| `mapping.rs` | `midi_pitch_to_key()`, `SCALE` | Map MIDI pitch → 1 keyboard char of the 61-key scale, folding octaves into range. |
| `config.rs` | `Config`, `load()`, `save()`, `validate()` | Persist & validate `{lang,theme,palette,folders}` via the JSON store. |
| `platform.rs` | `begin/end_high_resolution_timer()`, `is_playback_supported()` | Windows `timeBeginPeriod(1)`; gates playback support. |
| `hotkeys.rs` | `register()` | Register 4 global shortcuts → engine actions + emit `hotkey:fired`. |

### Frontend — `app/src/`

| Path | Main public functions/components | Role |
|---|---|---|
| `main.tsx` | bootstrap | Mount `<App/>` into `#root`. |
| `App.tsx` | `App`, `Shell` | Wrap providers; orchestrate folder/file/showPlayer; lazy-load PlayerSheet. |
| `lib/tauri.ts` | `api` (15 methods), `onPlaybackState/Tick/Done`, `onHotkey` | The single typed IPC seam (`invoke`/`listen`). |
| `lib/difficulty.ts` | `difficultyFor()` | Map speed → difficulty band (used by FolderPane & PlayerSheet). |
| `types.ts` | `Config`, `NoteSchedule`, `PlaybackState`, `MidiFile`, etc. | TS mirror of the Rust struct shapes. |
| `contexts/ConfigContext.tsx` | `ConfigProvider`, `ConfigContext` | Config state + write-through to `set_config`. |
| `contexts/PlaybackContext.tsx` | `PlaybackProvider`, state+actions contexts | Subscribe to playback events; rAF-coalesce tick→index; stable actions. |
| `hooks/{useConfig,usePlayback,useTheme}.ts` | `useConfig`, `usePlaybackState/Actions`, `useTheme` | Context access + reactive theme apply. |
| `i18n/strings.ts` | `STRINGS`, `fmt`, `StringsBundle` | Bilingual id/en text (≈67 keys) + interpolation. |
| `theme/themes.ts` | `THEMES`, `applyTheme`, `ColorSet` | 2 palettes × 2 modes → set CSS vars. |
| `components/TitleBar.tsx` | `TitleBar` | Custom Win32 chrome (drag, min/max/close). |
| `components/Header.tsx` | `Header`, `SegToggle` | Title + 3 segmented toggles (theme/palette/lang) + Info. |
| `components/FolderPane.tsx` | `FolderPane` | Folder list, add/remove, speed slider + difficulty label. |
| `components/MusicPane.tsx` | `MusicPane` | Song table, 200ms debounced search, arrow/Enter nav. |
| `components/BottomBar.tsx` | `BottomBar` | Selected-file status + main Play button. |
| `components/PlayerSheet.tsx` | `PlayerSheet` | Player dialog: progress, speed, O(1) note log, transport (lazy-loaded). |
| `components/InfoPopup.tsx` | `InfoPopup` | About dialog (identity/metadata/hotkey legend) (lazy). |
| `components/Splash.tsx` | `Splash` | Splash min-visible 1100ms, fades when config ready. |
| `components/UnsupportedBanner.tsx` | `UnsupportedBanner` | Non-Windows banner (playback disabled). |
| `components/ui/{Button,Dialog,Slider,Input,MarqueeText}.tsx` | primitives | Generic prop-driven UI components (variant/size). |

---

# Data & Config

**Main config:** `playSong_config.json` in the OS app-data directory (via `tauri-plugin-store`, see `config.rs`). Schema:

```json
{ "lang": "id|en", "theme": "dark|light", "palette": "celestial|grand_piano", "folders": ["C:/path", ...] }
```
> `validate()` forces legal values + drops empty folders. UI labels: `celestial`→"Zinc", `grand_piano`→"Slate".

**`.env`:** **Not found** — the stray `.env` file (content `/docs`, read by no source) was deleted 2026-06-15. Build configuration lives in `tauri.conf.json` (window 1100×720, `decorations:false`, bundle targets `msi`+`nsis`, `csp:null`) and `capabilities/default.json` (permission whitelist).

**Data schema (core entities):** No DB. In-memory structures: `NoteSchedule { initial_tempo_bpm, events: NoteEvent[] }`, `NoteEvent { delay_secs, keys }` (prefix `~` = release), `PlaybackState { is_playing, index, total, speed, song_path }`.

**Migration/seed:** Not found (no database).

**Output / runtime artifacts:** `src-tauri/target/release/playsong.exe` + `bundle/msi/*.msi` + `bundle/nsis/*-setup.exe`; frontend build in `app/dist/`. All gitignored.

---

# External Integrations

> Local app — **no external network API/service**. The integrations present are OS-level via Tauri:

| Integration | Calling module | Note |
|---|---|---|
| OS keyboard input (`SendInput`) | `injector.rs` (`EnigoInjector`) via `enigo` | Emits keypresses; requires the target window to be focused. |
| OS global hotkey hook | `hotkeys.rs` via `tauri-plugin-global-shortcut` | DELETE/HOME/END/INSERT. |
| Filesystem (read-only) | `commands.rs::list_midis_in_folder`, `midi.rs::parse_midi` | Scan folder + read MIDI bytes. |
| App-data store | `config.rs` via `tauri-plugin-store` | Persist config JSON. |
| Native file dialog | `FolderPane.tsx` via `tauri-plugin-dialog` | Folder picker. |
| GitHub link (`https://github.com/Gulpanjul/MidiToTyping`) | `InfoPopup.tsx`, opened via `shell:allow-open` | Just an About link, not an API. |

---

# Risks / Blind Spots

| Area | Detail |
|---|---|
| **Non-recursive scan (by design)** | `list_midis_in_folder` ([commands.rs:51](src-tauri/src/commands.rs#L51)) does a 1-level `read_dir` — intentional (matches legacy); README corrected 2026-06-15 for consistency. |
| **Window focus** | `enigo` `SendInput` does not target a specific HWND; DirectInput/RawInput games may ignore synthetic input. |
| **Windows-only playback** | `is_playback_supported()` = `cfg!(windows)`; on non-Windows the UI runs but Play is disabled. |
| **Dynamic imports** | `PlayerSheet` & `InfoPopup` are `lazy()` (code-split) — not visible in the static import graph. |
| **Swallowed errors** | Several `.catch(()=>{})` in the frontend (ConfigContext, MusicPane, TitleBar) silently swallow errors — hard to diagnose when the Tauri runtime isn't ready. |
| **Cross-thread state** | `PlaybackState` is behind `Arc<Mutex>`; seek consistency is held by a single lock, but a few `lock().await` calls are separate per loop iteration. |
| **`legacy/` not mapped** | Intentionally excluded; see [legacy/docs/SYSTEM_MAP.md](legacy/docs/SYSTEM_MAP.md) for Python parity. |
