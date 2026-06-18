# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status (2026-04-29)

**playSong** mengkonversi file MIDI menjadi simulasi penekanan keyboard otomatis untuk game piano (*Sky: Children of the Light*, *Piano Tiles*, dst).

Repo ini menampung **dua implementasi**:

| | Path | Status | Admin? |
|---|---|---|---|
| **Tauri rewrite (current)** | `app/` + `src-tauri/` | v0.2.x — primary build | ❌ Tidak butuh |
| **Legacy Python** | `legacy/` | Reference-only, archived | ✅ Wajib |

Bug fix dan fitur baru → **Tauri side saja**. Python tree disimpan untuk verifikasi parity dan referensi historis. Jangan edit `legacy/` kecuali user eksplisit minta.

## Tauri rewrite (primary)

### Layout

```
app/src/
├── App.tsx                      — Shell wrapped in ConfigProvider + PlaybackProvider
├── types.ts                     — TS mirror of Rust struct shapes
├── i18n/strings.ts              — port of legacy/src/strings.py (id + en, 45 keys)
├── theme/themes.ts              — port of legacy/src/themes.py (4 combos × 11 keys)
├── lib/tauri.ts                 — typed invoke/listen wrappers
├── contexts/                    — ConfigProvider, PlaybackProvider
├── hooks/                       — useConfig, usePlayback, useTheme
└── components/
    ├── ui/                      — Button, Slider, Input, Dialog (hand-rolled)
    ├── TitleBar.tsx             — custom Win32 chrome (drag, min/max/close)
    ├── Header.tsx               — title + 3 segmented toggles + Info button
    ├── FolderPane.tsx           — folder list, +/- buttons, speed slider w/ difficulty label
    ├── MusicPane.tsx            — song table with debounced search
    ├── BottomBar.tsx            — Play button only
    ├── PlayerSheet.tsx          — Dialog with progress bar + Play/Pause + Pilih Lagu Lain + Keluar + note log
    ├── InfoPopup.tsx            — About modal (sectioned: identity / metadata / hotkey legend)
    └── UnsupportedBanner.tsx    — non-Windows guard banner
```

```
src-tauri/src/
├── main.rs          — thin entry, calls lib::run()
├── lib.rs           — Tauri builder, plugin registration, command exports
├── mapping.rs       — _SCALE table + midi_pitch_to_key()
├── injector.rs      — Injector trait + EnigoInjector + whitelist + shift handling
├── midi.rs          — parse_midi() via midly -> NoteSchedule
├── playback.rs      — PlaybackEngine (Arc<Mutex>, JoinHandle::abort cancellation, DEFAULT_SPEED = 0.95)
├── config.rs        — typed wrapper over tauri-plugin-store
├── platform.rs      — Windows timeBeginPeriod(1) + is_playback_supported()
├── commands.rs      — 13 #[tauri::command]s + TauriSink that emits events
└── hotkeys.rs       — register DELETE/HOME/END/INSERT via global-shortcut plugin
```

### Dev / build

```bash
cd src-tauri && cargo tauri dev    # hot-reload dev (spawns Vite, opens Tauri window)
cd src-tauri && cargo tauri build  # production .exe + MSI + NSIS in target/release/
```

### Tests

```bash
cd src-tauri && cargo test         # 17 unit tests (mapping/injector/midi/playback)
cd app && npm run typecheck        # TS strict-mode check
```

### Toolchain notes (Windows dev box)

- `cargo` ada di `C:\Users\<user>\.cargo\bin\cargo.exe` — biasanya tidak di PATH default. PowerShell: `$env:Path = "C:\Users\<user>\.cargo\bin;" + $env:Path`.
- `npm` ada di `C:\Program Files\nodejs\npm.cmd` — biasanya tidak di PATH default. PowerShell: prepend nodejs dir, lalu call `& "C:\Program Files\nodejs\npm.cmd"` untuk bypass execution-policy block di `npm.ps1`.

### Domain truths (port verbatim — jangan re-derive)

Byte-for-byte ports dari Python build. Jangan redesign:

- **`_SCALE` mapping** ([src-tauri/src/mapping.rs](src-tauri/src/mapping.rs)) ← [legacy/src/midi_parser.py:7](legacy/src/midi_parser.py#L7)
- **`_ALLOWED` whitelist** ([src-tauri/src/injector.rs](src-tauri/src/injector.rs)) ← [legacy/src/keyboard_sim.py:3-8](legacy/src/keyboard_sim.py#L3-L8)
- **`CONVERSION_CASES` shift map** ([src-tauri/src/injector.rs](src-tauri/src/injector.rs)) ← [legacy/src/constants.py:12-15](legacy/src/constants.py#L12-L15)
- **Hotkey magnitudes (rewind/skip = 10 notes)** ([src-tauri/src/playback.rs](src-tauri/src/playback.rs)) ← [legacy/playSong_clean.py:28,40](legacy/playSong_clean.py#L28-L40)
- **Config schema (`{lang, theme, palette, folders}`)** ([src-tauri/src/config.rs](src-tauri/src/config.rs)) ← [legacy/src/config.py](legacy/src/config.py)

### Hotkeys (global)

- `DELETE` — Play/Pause toggle
- `HOME` — Rewind 10 note
- `END` — Skip 10 note (atau reset jika dekat akhir)
- `INSERT` — Restart dari awal

User dengan keyboard 65% (no nav cluster) tidak punya akses fisik ke HOME/END/INSERT — diatasi dengan tombol rewind/skip/restart in-app di PlayerSheet (v0.2).

### Default speed 0.95×

Engine menset `DEFAULT_SPEED = 0.95` di [src-tauri/src/playback.rs](src-tauri/src/playback.rs#L56). Alasan: Python `threading.Timer` overshoot 5–15ms per note di Windows, sedangkan Rust `tokio::sleep` + `timeBeginPeriod(1)` hit deadline ~1ms. Tanpa kompensasi 0.95×, user upgrading dari Python akan rasa Tauri build "terlalu cepat" di 1.0×.

### Why no Administrator?

Python pakai library [`keyboard`](https://github.com/boppreh/keyboard) yang installs driver-style hook → butuh admin. Tauri rewrite pakai Win32 API standar (`SetWindowsHookEx WH_KEYBOARD_LL` via tauri-plugin-global-shortcut, `SendInput` via enigo) yang run sebagai standard user. MSI installer juga tidak show UAC shield.

### Build artifacts

```
src-tauri/target/release/playsong.exe                              — 5.36 MB
src-tauri/target/release/bundle/msi/playSong_0.2.0_x64_en-US.msi   — 2.62 MB
src-tauri/target/release/bundle/nsis/playSong_0.2.0_x64-setup.exe  — 1.82 MB
```

## Legacy Python (reference-only)

Python tree dipindah ke `legacy/` di 2026-04-29 setelah Tauri rewrite v0.1 lulus smoke test. Tetap di repo untuk:
- Verifikasi parity (compare schedule output, key timing)
- Referensi domain truths saat port fitur baru
- Fallback kalau ada user yang masih butuh build legacy

**Jangan edit kecuali user eksplisit minta.**

### Run legacy Python

```bash
cd legacy
pip install keyboard mido
# Wajib Administrator
python playSong_clean.py
```

### Build legacy .exe (PyInstaller)

```bash
cd legacy
%USERPROFILE%\.local\bin\pyinstaller.exe playSong_clean.spec --noconfirm
# Output: legacy/dist/playSong_clean.exe (~11 MB)
```

### Legacy tests

```bash
cd legacy
PYTHONIOENCODING=utf-8 python tests/test_playSong.py
```

### Legacy architecture (singkat)

- `legacy/playSong_clean.py` — entry: `main()` + 4 hotkey handlers
- `legacy/src/` — 18 modul Python (constants/strings/themes/config/keyboard_sim/midi_parser/playback + `gui/`)
- Pattern: shared state via `ctx` dict, mutable color dict diupdate in-place oleh `repaint()`
- Hotkeys via `keyboard.on_press_key()` (driver-level)
- `legacy/tests/test_playSong.py` — 7 test groups × 17 assertions, stub `keyboard` module supaya tidak butuh admin

## Shared Dev Standards

Standar dev lintas-project ada di `~/.claude/docs/` (PROJECT_TEMPLATE, QUICK_REFERENCE, LSH_FRONTEND_STANDARDS, DELEGATION_PROMPT, frameworks/, dst). Project-specific docs di `docs/`.
