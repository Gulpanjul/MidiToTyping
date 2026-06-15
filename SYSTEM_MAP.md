<!--
Tujuan: Kompas arsitektur one-shot untuk build Tauri (primary) — navigasi utama tanpa blind scan.
Caller: Claude Code / developer di awal sesi (Mandatory Map Check).
Dependensi: app/ (React 19 + Vite), src-tauri/ (Rust + Tauri v2).
Cakupan: build Tauri aktif. Legacy Python (legacy/) punya map sendiri.
Sinkron: update bagian terkait saat menambah/hapus file atau ubah flow utama.
-->

# SYSTEM_MAP.md — playSong (build Tauri)

> Dibuat: 2026-06-15 · Versi app: `0.2.0` (Cargo.toml + tauri.conf.json) · Entry: `src-tauri/src/main.rs` → `lib::run()` · Frontend entry: `app/src/main.tsx`
> Catatan: `legacy/` (Python, arsip referensi) punya peta terpisah di [legacy/docs/SYSTEM_MAP.md](legacy/docs/SYSTEM_MAP.md) — tidak dipetakan di sini.

---

# Project Summary

**Tujuan aplikasi:** Mengkonversi file MIDI menjadi simulasi penekanan keyboard otomatis untuk game piano berbasis keyboard (_Sky: Children of the Light_, _Piano Tiles_). User memilih folder berisi `.mid`/`.midi`, pilih lagu, atur kecepatan, lalu engine menekan tombol sesuai timing MIDI ke window game yang sedang fokus.

**Tech stack utama:**

| Lapis | Detail |
|---|---|
| Desktop shell | Tauri v2 (Rust `2.10.3` resolved; `tauri-build`, plugin dialog/fs/store/global-shortcut/os/shell) |
| Frontend | React 19 + TypeScript (strict) + Vite 6 + Tailwind v4 |
| Backend async | tokio (rt-multi-thread) — engine playback satu task |
| MIDI parse | `midly` 0.5 (zero-copy) |
| Keyboard inject | `enigo` 0.3 (`SendInput`, standard user, no admin) |
| Hotkey global | `tauri-plugin-global-shortcut` (`SetWindowsHookEx WH_KEYBOARD_LL`) |
| Persist config | `tauri-plugin-store` → `playSong_config.json` |
| Platform timing | `windows` crate `timeBeginPeriod(1)` (Windows-only) |
| DB / queue / API eksternal | Not found (aplikasi lokal, tanpa backend jaringan) |

**Pola arsitektur:** Desktop 2-lapis. **UI React** (state via 2 Context: Config + Playback) ↔ **core Rust** via Tauri IPC (`invoke` command + `emit` event). Core memakai **trait abstraction** (`Injector`, `StateSink`) sehingga `PlaybackEngine` testable tanpa OS asli. Tidak ada layer Controller/Service/Repo klasik → padanan: **Tauri command = handler**, **PlaybackEngine/midi/injector = service**, **config.rs + fs = data access**, **store JSON + filesystem + OS input = storage/sink**.

---

# Core Logic Flow (Function-Level Flowchart)

**Startup (Rust → Frontend)**
`main()[main.rs] -> playsong_lib::run()[lib.rs] -> platform::begin_high_resolution_timer() -> tauri::Builder(+6 plugin) -> setup[lib.rs]{ AppState::new()[commands.rs] -> EnigoInjector::new()[injector.rs] + TauriSink ; app.manage(state) ; hotkeys::register()[hotkeys.rs] }`
`main.tsx -> App -> ConfigProvider(api.getConfig -> get_config[commands.rs] -> config::load) + PlaybackProvider(api.getState) -> Shell(useTheme->applyTheme, api.isPlaybackSupported) -> Splash auto-hide saat ready`

**Pilih folder & list lagu**
`FolderPane.handleAdd()[dialog open] -> ConfigContext.setConfig(folders) -> api.setConfig -> set_config[commands.rs] -> config::save -> store.save() ; onSelectFolder -> MusicPane.effect -> api.listMidisInFolder -> list_midis_in_folder[commands.rs] -> fs::read_dir (1 level, filter .mid/.midi, sort) -> render tabel`

**Load & arm lagu (inti)**
`MusicPane.onPlayFile / BottomBar.onPlay -> App.onPlay() -> PlaybackContext.loadSong -> api.loadSong -> load_song[commands.rs] -> midi::parse_midi()[midi.rs] (midly Smf::parse -> merge track per abs_tick -> group nada simultan -> hitung delay detik) -> engine.load()[playback.rs] (arm, is_playing=false, index=0) -> PlaybackState -> PlayerSheet terbuka (paused)`

**Jalankan playback (loop)**
`DELETE hotkey / tombol Play -> engine.toggle()|play()[playback.rs] -> spawn_task() tokio loop { baca (idx,total,speed) -> ambil event -> injector.press()|release()[injector.rs] -> enigo.key() -> OS SendInput ; sink.emit_tick("playback:tick") -> PlaybackProvider rAF-coalesce index + PlayerSheet log O(1) ; index+=1 ; sleep(delay/speed) } -> selesai: emit "playback:done"`

**Hotkey global (Windows)**
`OS key DELETE/HOME/END/INSERT -> global-shortcut -> hotkeys::on_shortcut[hotkeys.rs] -> engine.toggle|seek(±SEEK_STEP)|restart -> emit "hotkey:fired" + event playback`

**Ganti theme/palette/bahasa**
`Header.SegToggle.onChange -> ConfigContext.setConfig(patch) -> api.setConfig -> set_config -> config::save ; useTheme.effect -> applyTheme(palette,theme)[themes.ts] -> set CSS var di :root`

---

# Clean Tree

> Dikecualikan (sesuai rule): `node_modules/`, `target/`, `gen/`, `dist/`, `dist_nuitka/`, `build/`, `.git/`, `__pycache__/`, `archive/`, `legacy/` (punya map sendiri), `*.log`, `*.lock`, `*.map`.

```
MidiToTyping/
├── app/                              # Frontend Vite + React 19 + TS
│   ├── index.html
│   ├── package.json · vite.config.ts · tsconfig*.json
│   ├── playwright.config.ts · e2e/    # E2E Playwright
│   ├── public/playsong-icon.png
│   └── src/
│       ├── main.tsx                  # ReactDOM bootstrap (StrictMode)
│       ├── App.tsx                   # Shell + provider + orkestrasi state
│       ├── types.ts                  # Mirror TS dari struct Rust
│       ├── lib/tauri.ts              # Wrapper invoke/listen (seam IPC)
│       ├── lib/difficulty.ts         # speed -> label difficulty
│       ├── contexts/{ConfigContext,PlaybackContext}.tsx
│       ├── hooks/{useConfig,usePlayback,useTheme}.ts
│       ├── i18n/strings.ts           # Bundle id/en + fmt()
│       ├── theme/themes.ts           # THEMES (2 palette × 2 mode) + applyTheme
│       └── components/
│           ├── TitleBar.tsx · Header.tsx · FolderPane.tsx
│           ├── MusicPane.tsx · BottomBar.tsx · PlayerSheet.tsx
│           ├── InfoPopup.tsx · Splash.tsx · UnsupportedBanner.tsx
│           └── ui/{Button,Dialog,Slider,Input,MarqueeText}.tsx
│
├── src-tauri/                        # Backend Tauri v2 (Rust)
│   ├── Cargo.toml · build.rs · tauri.conf.json
│   ├── capabilities/default.json     # Whitelist permission jendela main
│   ├── icons/
│   ├── tests/                        # fixtures + test integrasi
│   └── src/
│       ├── main.rs                   # Entry tipis -> lib::run()
│       ├── lib.rs                    # Builder, registrasi plugin + command
│       ├── commands.rs               # 13 #[tauri::command] + TauriSink
│       ├── playback.rs               # PlaybackEngine + trait StateSink
│       ├── injector.rs               # trait Injector + Enigo/Mock + whitelist
│       ├── midi.rs                   # parse_midi() midly -> NoteSchedule
│       ├── mapping.rs                # SCALE 61-key + midi_pitch_to_key()
│       ├── config.rs                 # load/save/validate Config (store)
│       ├── platform.rs               # timer resolution + is_playback_supported
│       └── hotkeys.rs                # daftar DELETE/HOME/END/INSERT
│
├── docs/                             # Doc project (superpowers/plans)
├── CLAUDE.md · README.md · .gitignore
└── SYSTEM_MAP.md                     # file ini
```

---

# Module Map (The Chapters)

### Backend — `src-tauri/src/`

| Path | Fungsi/struct publik utama | Peran |
|---|---|---|
| `main.rs` | `main()` | Entry biner; panggil `playsong_lib::run()`. |
| `lib.rs` | `run()` | Bangun Tauri builder, daftar 6 plugin + 13 command, setup state & hotkey. |
| `commands.rs` | 13 `#[command]` (`list_midis_in_folder`, `parse_midi`, `load_song`, `play`, `pause`, `toggle`, `seek`, `restart`, `set_speed`, `get_state`, `get_config`, `set_config`, `is_playback_supported`), `AppState`, `TauriSink` | Permukaan IPC; jembatan command→engine dan engine→event (`playback:state/tick/done`). |
| `playback.rs` | `PlaybackEngine` (`load/play/pause/toggle/seek/restart/set_speed/snapshot`), trait `StateSink`, `NullSink`, `PlaybackState`, `DEFAULT_SPEED=0.95`, `SEEK_STEP=10` | Engine inti: 1 tokio task, cancel via `JoinHandle::abort`, scale delay by speed. |
| `injector.rs` | trait `Injector`, `EnigoInjector`, `MockInjector`, `is_allowed/is_shifted/shifted_to_base`, `ALLOWED` | Sintesis keypress ke OS + whitelist & shift-map (port verbatim Python). |
| `midi.rs` | `parse_midi()`, `NoteSchedule`, `NoteEvent`, `MidiError` | Parse MIDI: merge track, group nada simultan per tick, hitung delay detik @1.0×. |
| `mapping.rs` | `midi_pitch_to_key()`, `SCALE` | Map pitch MIDI → 1 char keyboard 61-key, fold oktaf ke range. |
| `config.rs` | `Config`, `load()`, `save()`, `validate()` | Persist & validasi `{lang,theme,palette,folders}` via store JSON. |
| `platform.rs` | `begin/end_high_resolution_timer()`, `is_playback_supported()` | `timeBeginPeriod(1)` Windows; gate dukungan playback. |
| `hotkeys.rs` | `register()` | Daftar 4 shortcut global → aksi engine + emit `hotkey:fired`. |

### Frontend — `app/src/`

| Path | Fungsi/komponen publik utama | Peran |
|---|---|---|
| `main.tsx` | bootstrap | Mount `<App/>` ke `#root`. |
| `App.tsx` | `App`, `Shell` | Bungkus provider; orkestrasi folder/file/showPlayer; lazy-load PlayerSheet. |
| `lib/tauri.ts` | `api` (15 method), `onPlaybackState/Tick/Done`, `onHotkey` | Satu-satunya seam IPC bertipe (`invoke`/`listen`). |
| `lib/difficulty.ts` | `difficultyFor()` | Map speed → band difficulty (dipakai FolderPane & PlayerSheet). |
| `types.ts` | `Config`, `NoteSchedule`, `PlaybackState`, `MidiFile`, dst | Mirror TS dari shape struct Rust. |
| `contexts/ConfigContext.tsx` | `ConfigProvider`, `ConfigContext` | State config + write-through ke `set_config`. |
| `contexts/PlaybackContext.tsx` | `PlaybackProvider`, state+actions context | Subscribe event playback; rAF-coalesce tick→index; aksi stabil. |
| `hooks/{useConfig,usePlayback,useTheme}.ts` | `useConfig`, `usePlaybackState/Actions`, `useTheme` | Akses context + apply theme reaktif. |
| `i18n/strings.ts` | `STRINGS`, `fmt`, `StringsBundle` | Teks bilingual id/en (≈67 key) + interpolasi. |
| `theme/themes.ts` | `THEMES`, `applyTheme`, `ColorSet` | 2 palette × 2 mode → set CSS var. |
| `components/TitleBar.tsx` | `TitleBar` | Chrome Win32 kustom (drag, min/max/close). |
| `components/Header.tsx` | `Header`, `SegToggle` | Judul + 3 segmented toggle (theme/palette/lang) + Info. |
| `components/FolderPane.tsx` | `FolderPane` | List folder, add/remove, slider speed + label difficulty. |
| `components/MusicPane.tsx` | `MusicPane` | Tabel lagu, search debounce 200ms, nav panah/Enter. |
| `components/BottomBar.tsx` | `BottomBar` | Status file terpilih + tombol Play utama. |
| `components/PlayerSheet.tsx` | `PlayerSheet` | Dialog player: progress, speed, log note O(1), transport (lazy-loaded). |
| `components/InfoPopup.tsx` | `InfoPopup` | Dialog About (identitas/metadata/hotkey legend) (lazy). |
| `components/Splash.tsx` | `Splash` | Splash min-visible 1100ms, fade saat config ready. |
| `components/UnsupportedBanner.tsx` | `UnsupportedBanner` | Banner non-Windows (playback disabled). |
| `components/ui/{Button,Dialog,Slider,Input,MarqueeText}.tsx` | primitive | Komponen UI generik prop-driven (variant/size). |

---

# Data & Config

**Config utama:** `playSong_config.json` di direktori app-data OS (via `tauri-plugin-store`, lihat `config.rs`). Skema:

```json
{ "lang": "id|en", "theme": "dark|light", "palette": "celestial|grand_piano", "folders": ["C:/path", ...] }
```
> `validate()` paksa nilai legal + buang folder kosong. Label UI: `celestial`→"Zinc", `grand_piano`→"Slate".

**`.env`:** **Not found** — file `.env` nyasar (berisi `/docs`, tak dibaca source mana pun) dihapus 2026-06-15. Konfigurasi build via `tauri.conf.json` (window 1100×720, `decorations:false`, target bundle `msi`+`nsis`, `csp:null`) dan `capabilities/default.json` (whitelist permission).

**Skema data (entity inti):** Tidak ada DB. Struktur in-memory: `NoteSchedule { initial_tempo_bpm, events: NoteEvent[] }`, `NoteEvent { delay_secs, keys }` (prefix `~` = release), `PlaybackState { is_playing, index, total, speed, song_path }`.

**Migration/seed:** Not found (tanpa database).

**Output / runtime artifacts:** `src-tauri/target/release/playsong.exe` + `bundle/msi/*.msi` + `bundle/nsis/*-setup.exe`; build frontend di `app/dist/`. Semua di-gitignore.

---

# External Integrations

> Aplikasi lokal — **tidak ada API/service jaringan eksternal**. Integrasi yang ada bersifat OS-level lewat Tauri:

| Integrasi | Modul pemanggil | Catatan |
|---|---|---|
| OS keyboard input (`SendInput`) | `injector.rs` (`EnigoInjector`) via `enigo` | Output keypress; butuh window target fokus. |
| OS global hotkey hook | `hotkeys.rs` via `tauri-plugin-global-shortcut` | DELETE/HOME/END/INSERT. |
| Filesystem (read-only) | `commands.rs::list_midis_in_folder`, `midi.rs::parse_midi` | Scan folder + baca byte MIDI. |
| App-data store | `config.rs` via `tauri-plugin-store` | Persist config JSON. |
| Native file dialog | `FolderPane.tsx` via `tauri-plugin-dialog` | Picker folder. |
| Link GitHub (`https://github.com/Gulpanjul/MidiToTyping`) | `InfoPopup.tsx`, dibuka via `shell:allow-open` | Hanya tautan About, bukan API. |

---

# Risks / Blind Spots

| Area | Detail |
|---|---|
| **Scan non-rekursif (by design)** | `list_midis_in_folder` ([commands.rs:51](src-tauri/src/commands.rs#L51)) `read_dir` 1 level — disengaja (sesuai legacy); README dikoreksi 2026-06-15 agar konsisten. |
| **Fokus window** | `enigo` `SendInput` tidak target HWND spesifik; game DirectInput/RawInput mungkin abaikan synthetic input. |
| **Windows-only playback** | `is_playback_supported()` = `cfg!(windows)`; di non-Windows UI jalan tapi Play disabled. |
| **Dynamic import** | `PlayerSheet` & `InfoPopup` di-`lazy()` (code-split) — tidak tampak di graf import statik. |
| **Error ditelan** | Beberapa `.catch(()=>{})` di frontend (ConfigContext, MusicPane, TitleBar) menelan error diam-diam — sulit didiagnosis saat runtime Tauri belum siap. |
| **State lintas-thread** | `PlaybackState` di `Arc<Mutex>`; konsistensi seek dijaga single-lock, tapi beberapa `lock().await` terpisah per iterasi loop. |
| **`legacy/` tak dipetakan** | Sengaja dikecualikan; lihat [legacy/docs/SYSTEM_MAP.md](legacy/docs/SYSTEM_MAP.md) bila perlu parity Python. |
