# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Two implementations live in this repo

1. **Tauri rewrite (current focus, v0.1.x)** — `app/` (Vite + React 19 + TS) and `src-tauri/` (Rust). No admin required. See [Tauri rewrite layout](#tauri-rewrite-layout) below.
2. **Legacy Python implementation** — `playSong_clean.py` + `src/`. Preserved for reference until parity verified. Requires Administrator.

When fixing bugs in **the Tauri build**, do NOT modify `playSong_clean.py` or `src/*.py`. The Python tree is reference-only.

## Project Overview

**playSong** adalah aplikasi Python yang mengkonversi file MIDI menjadi simulasi penekanan keyboard otomatis, untuk digunakan pada game piano seperti *Sky: Children of the Light* dan *Piano Tiles*. Aplikasi ini membutuhkan **hak administrator Windows** karena menggunakan global keyboard hook.

## Post-Fix Workflow (WAJIB)

**Setiap selesai melakukan perbaikan kode (bugfix / feature change / refactor):**

1. Jalankan test suite:
   ```bash
   PYTHONIOENCODING=utf-8 python tests/test_playSong.py
   ```
2. **Rebuild .exe (WAJIB)** — pastikan fix benar-benar bekerja di build windowed:
   ```bash
   %USERPROFILE%\.local\bin\pyinstaller.exe playSong_clean.spec --noconfirm
   ```
3. Verifikasi `dist/playSong_clean.exe` berhasil ter-build dan size wajar (~11 MB).
4. Jika perubahan mempengaruhi startup / hotkey / GUI: lakukan smoke test manual pada exe (jalankan, pilih lagu, test hotkey).

> Alasan: `input()`, `sys.stdin`, `sys.stdout`, dan lazy-import bisa berbeda perilakunya antara `python script.py` (console=True) vs .exe bundle (`console=False`). Test suite tidak mendeteksi ini. Build + smoke test exe adalah satu-satunya verifikasi akhir.

## Commands

**Install dependencies:**
```bash
pip install keyboard mido
```

**Run (wajib sebagai Administrator):**
```bash
python playSong_clean.py
```

**Run tests (tidak butuh admin):**
```bash
PYTHONIOENCODING=utf-8 python tests/test_playSong.py
```

**Build ke .exe (PyInstaller — rekomendasi):**
```bash
uv tool install pyinstaller --with keyboard --with mido
%USERPROFILE%\.local\bin\pyinstaller.exe playSong_clean.spec --noconfirm
# Output: dist/playSong_clean.exe (~11 MB, no console window)
```

**Build ke .exe (Nuitka — lebih kecil):**

Membutuhkan **Python 3.12** (bukan 3.13+). Output: **~8.5 MB**.

```bash
uv python install 3.12
uv tool install nuitka --python 3.12 --with keyboard --with mido --with zstandard --force

%USERPROFILE%\AppData\Roaming\uv\tools\nuitka\Scripts\python.exe -m nuitka ^
  --standalone --onefile --windows-console-mode=disable ^
  --enable-plugin=tk-inter --include-module=keyboard --include-package=mido ^
  --mingw64 --lto=yes --assume-yes-for-downloads ^
  --output-filename=playSong_clean.exe --output-dir=dist_nuitka playSong_clean.py
```

## Architecture

Proyek di-refactor dari single-file monolith (~1400 baris) menjadi **modular package**: 18 file Python di `src/`, masing-masing ≤ 100 baris.

### Struktur Modul

```
playSong_clean.py            # entry: main() + 4 hotkey handlers (~100 baris)
src/
├── constants.py             # global state + APP_VERSION/DATE/AUTHOR
├── strings.py               # STRINGS bilingual (id/en)
├── themes.py                # THEMES: Zinc + Slate (dark/light) — shadcn palette
├── config.py                # load_config / save_config (JSON)
├── keyboard_sim.py          # press/release/is_shifted + whitelist guard
├── midi_parser.py           # parse_song_file → raises MidoNotAvailable
├── playback.py              # parse_info + play_next_note engine
└── gui/
    ├── splash.py            # splash screen (pertama render)
    ├── widgets.py           # make_btn, make_seg_btn, rebuild_seg
    ├── info_popup.py        # tombol ℹ popup (About/versi/hotkey)
    ├── header.py            # title + seg controls (theme/palette/lang)
    ├── folder_nav.py        # folder navigation logic
    ├── folder_pane.py       # left panel widgets + speed slider
    ├── music_pane.py        # right panel widgets + refresh/sort
    ├── bottom.py            # bottom buttons + event bindings
    ├── repaint.py           # live theme/palette update
    ├── process_file.py      # GUI orchestrator (lazy-loaded dari main)
    └── _parse_handler.py    # safe_parse() wrapper
```

### Alur Data

```
main()
  ├─ load_config()                 # src.config
  ├─ keyboard.on_press_key() × 4   # DELETE/HOME/END/INSERT
  ├─ show_splash()                 # src.gui.splash — user sees splash first
  └─ (lazy) process_file()         # src.gui.process_file
       └─ build ctx → builders → root.mainloop()
           └─ user pilih lagu → parse_song_file() → play_next_note(gen)
```

### Context Dict (`ctx`) Pattern

Karena `process_file()` dipecah ke banyak file, shared state dipass via dict `ctx` berisi:
- Tk objects: `root`, `C` (mutable color dict), `S` (strings), `style`
- 25+ widget references (frm_top, btn_play, tree, folder_lb, dll)
- State lists (mutable-by-reference): `nav_folder`, `nav_stack`, `active_folder`, `music_files`
- Tk vars: `search_var`, `speed_var`, `selected_path`
- Callbacks: `set_lang`, `set_theme`, `set_palette`, `repaint`, `refresh_music`, `close_window`, `confirm_select`, `load_folder_pane`

**Invariant:** `ctx['C']` adalah dict object yang sama sepanjang sesi — di-mutate in-place oleh `repaint()` agar lambda hover bindings yang capture `C` by reference auto-update.

### Global State (`src.constants`)

```python
LANG            # 'id' | 'en'
THEME           # 'dark' | 'light'
PALETTE         # 'celestial' (Zinc) | 'grand_piano' (Slate)
is_playing      # bool
stored_index    # int
playback_speed  # float
info_tuple      # (tempo, None, [[timestamp, keys], ...])
_play_gen       # concurrency generation counter
folder_history  # list[str]
APP_VERSION     # '1.0.0'
APP_DATE        # '2026-04-21'
APP_AUTHOR      # 'Gulpanjul'
APP_GITHUB      # 'github.com/Gulpanjul/MidiToTyping'
```

Pattern akses dari modul lain: `import src.constants as state; state.LANG = 'en'`.

### Hotkeys (global, via `keyboard` library)

- `DELETE` — Play/Pause toggle
- `HOME` — Rewind 10 note
- `END` — Skip 10 note (atau reset jika mendekati akhir)
- `INSERT` — Restart dari awal

> Pilih lagu lain / keluar: lewat tombol di **player popup** (`src/gui/player_popup.py`) — bukan via stdin/hotkey. Console mode juga pakai popup yang sama (popup meng-tap `sys.stdout`, sehingga output `print()` tetap visible di CLI + popup).

### Reload vs Repaint

| Toggle | Mechanism | Efek |
|---|---|---|
| Language (ID/EN) | `'__RELOAD__'` sentinel → close+reopen window | Full re-render, folder_history tetap |
| Theme (Dark/Light) | `repaint(ctx)` in-place | Tidak close window — live update |
| Palette (Zinc/Slate) | `repaint(ctx)` in-place | Tidak close window — live update |

## Startup Optimizations (applied 2026-04-23)

Lazy-import strategy: splash muncul sebelum heavy imports di-load.

| Modul | Di-defer ke | Saved |
|---|---|---|
| `src.gui.process_file` (+transitif) | lazy di `main()` setelah splash | ~16 ms |
| `tempfile` | `midi_parser._convert_midi_to_txt` | 7.4 ms |
| `webbrowser` | `info_popup` click handler | 4.4 ms |
| `tkinter.filedialog` | `folder_nav.on_add_folder` | 1.4 ms |
| `datetime` | `bottom.on_tree_select` | 0.4 ms |
| `tkinter.messagebox` | error handlers | ~0.3 ms |

Net: **~25–30% lebih cepat** time-to-visible-splash (Python module-load 85ms → ~60ms).

## Security Mitigations

| Attack surface | Mitigasi |
|---|---|
| Malicious MIDI → arbitrary keystrokes (app runs as admin) | Whitelist `_ALLOWED` di `keyboard_sim._safe()` |
| Temp file race (hardcoded name) | `tempfile.mkstemp(prefix='~midi_')` random + `try/finally` |
| `sys.exit(1)` dari parser | Diganti `raise MidoNotAvailable` — caller GUI yang decide |
| URL injection via f-string | URL GitHub hardcoded literal di `info_popup._GITHUB_URL` |

## Testing Strategy

`tests/test_playSong.py` — 7 test groups × 17 assertions. Stub module `keyboard` agar test jalan tanpa admin. Import dari `src.*` path setelah refactor.

```bash
PYTHONIOENCODING=utf-8 python tests/test_playSong.py
```

## Skalabilitas (catatan ke depan)

- **1000+ file MIDI**: `refresh_music()` sort + rebuild tree tiap keystroke; tambah debounce 200ms pada `search_var.trace_add` jika lag
- **MIDI besar**: `mido.merge_tracks()` load seluruh file ke memori; untuk file >50 MB pertimbangkan streaming
- **Multi-lagu paralel**: arsitektur saat ini serial; paralel butuh refactor state menjadi class

## Known Constraints

- **Windows-only** — `keyboard` library hanya support Windows untuk global hook
- **Admin required** — global keyboard hook butuh elevated privilege
- **~10-15ms timer jitter** — akurasi `threading.Timer` di Windows
- **61-tuts limit** — note di luar range C2–C7 di-fold
- **Multi-channel flatten** — semua track MIDI digabung
- **Slow .exe startup (PyInstaller)** — single-file bundle extract ke temp; Nuitka jauh lebih cepat
- **Nuitka butuh Python 3.12** — `--mingw64` tidak support 3.13+
- **`console=False`** — exe tidak munculkan CMD; `print()` tidak visible
- **Max 100 baris per file** — aturan yang diterapkan saat refactor; preservasi untuk maintainability

## Modifikasi Workflow

Saat menambah fitur GUI, tambahkan state ke `ctx` bukan ke closure. Urutan build:
1. `build_header(ctx)` → set widgets ke ctx
2. `init_folder_nav(ctx)` → set callbacks ke ctx
3. `build_folder_pane(ctx)` → gunakan callbacks dari ctx
4. `init_music_logic(ctx)` + `build_music_pane(ctx)`
5. `build_bottom(ctx)` → event bindings terakhir
6. `repaint(ctx)` menyentuh semua widget — update saat menambah widget baru

Selalu verify semua file ≤ 100 baris setelah perubahan.

---

## Tauri rewrite layout

The Tauri rewrite (v0.1.x) lives in two new top-level directories:

- `app/` — Vite + React 19 + TypeScript frontend (one window, no SSR)
- `src-tauri/` — Tauri v2 Rust backend (MIDI parser, key injector, playback engine, hotkeys, config)

The legacy Python tree is **untouched** by Tauri work — fix bugs in the rewrite, not in `src/*.py` or `playSong_clean.py`.

### Tauri dev / build

```bash
cd src-tauri && cargo tauri dev    # hot-reload dev (spawns Vite, opens Tauri window)
cd src-tauri && cargo tauri build  # production MSI in target/release/bundle/msi/
```

### Tauri tests

```bash
cd src-tauri && cargo test         # 17 unit tests (mapping/injector/midi/playback)
cd app && npm run typecheck        # TS strict-mode check
```

### Toolchain notes (Windows dev box)

- `cargo` is at `C:\Users\<user>\.cargo\bin\cargo.exe` — usually not on default PATH. PowerShell prepend: `$env:Path = "C:\Users\<user>\.cargo\bin;" + $env:Path`.
- `npm` is at `C:\Program Files\nodejs\npm.cmd` — usually not on default PATH. PowerShell prepend nodejs dir, and call `& "C:\Program Files\nodejs\npm.cmd"` to bypass execution-policy block on `npm.ps1`.

### Domain truths (never re-derive — port verbatim)

These are byte-for-byte ports of the working Python app. Don't redesign:

- **`_SCALE` mapping** ([src-tauri/src/mapping.rs](src-tauri/src/mapping.rs)) ← [src/midi_parser.py:7](src/midi_parser.py#L7)
- **`_ALLOWED` whitelist** ([src-tauri/src/injector.rs](src-tauri/src/injector.rs)) ← [src/keyboard_sim.py:3-8](src/keyboard_sim.py#L3-L8)
- **`CONVERSION_CASES` shift map** ([src-tauri/src/injector.rs `shifted_to_base`](src-tauri/src/injector.rs)) ← [src/constants.py:12-15](src/constants.py#L12-L15)
- **Hotkey magnitudes (rewind/skip = 10 notes)** ([src-tauri/src/playback.rs `SEEK_STEP`](src-tauri/src/playback.rs)) ← [playSong_clean.py:28,40](playSong_clean.py#L28-L40)
- **Config schema (`{lang, theme, palette, folders}`)** ([src-tauri/src/config.rs](src-tauri/src/config.rs)) ← [src/config.py](src/config.py)

### Architecture (Tauri side)

```
src-tauri/src/
├── main.rs          — thin entry, calls lib::run()
├── lib.rs           — Tauri builder, plugin registration, command exports
├── mapping.rs       — _SCALE table + midi_pitch_to_key()
├── injector.rs      — Injector trait + EnigoInjector + whitelist + shift handling
├── midi.rs          — parse_midi() via midly -> NoteSchedule
├── playback.rs      — PlaybackEngine (Arc<Mutex>, JoinHandle::abort cancellation)
├── config.rs        — typed wrapper over tauri-plugin-store
├── platform.rs      — Windows timeBeginPeriod(1) + is_playback_supported()
├── commands.rs      — 13 #[tauri::command]s + TauriSink that emits events
└── hotkeys.rs       — register DELETE/HOME/END/INSERT via global-shortcut plugin
```

```
app/src/
├── App.tsx                      — Shell wrapped in providers
├── types.ts                     — TS mirror of Rust struct shapes
├── i18n/strings.ts              — port of src/strings.py (id + en, 45 keys)
├── theme/themes.ts              — port of src/themes.py (4 combos × 11 keys)
├── lib/tauri.ts                 — typed invoke/listen wrappers
├── contexts/                    — ConfigProvider, PlaybackProvider
├── hooks/                       — useConfig, usePlayback, useTheme
└── components/
    ├── ui/                      — Button, Slider, Input, Dialog (hand-rolled)
    ├── Header.tsx               — title + 3 segmented toggles + Info button
    ├── FolderPane.tsx           — folder list, +/- buttons, speed slider
    ├── MusicPane.tsx            — song table with debounced search
    ├── BottomBar.tsx            — Play/Cancel
    ├── PlayerSheet.tsx          — Dialog with progress bar + play/pause
    ├── InfoPopup.tsx            — About modal
    └── UnsupportedBanner.tsx    — non-Windows guard banner
```

### Why no Administrator?

The legacy Python app needs admin because the [`keyboard`](https://github.com/boppreh/keyboard) library uses a driver-style hook. The Tauri rewrite uses standard Win32 APIs (`SetWindowsHookEx WH_KEYBOARD_LL` via Tauri's plugin, `SendInput` via enigo) which run as a standard user. The MSI installer also does not show a UAC shield.
