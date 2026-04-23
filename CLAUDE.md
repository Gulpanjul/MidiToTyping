# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**playSong** adalah aplikasi Python yang mengkonversi file MIDI menjadi simulasi penekanan keyboard otomatis, untuk digunakan pada game piano seperti *Sky: Children of the Light* dan *Piano Tiles*. Aplikasi ini membutuhkan **hak administrator Windows** karena menggunakan global keyboard hook.

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
