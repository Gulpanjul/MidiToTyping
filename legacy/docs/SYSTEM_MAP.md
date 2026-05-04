# SYSTEM_MAP.md — playSong (MidiToTyping)

> Dibuat: 2026-04-22 · Direfactor: 2026-04-23 (monolith → modular) · Entrypoint: `playSong_clean.py`

---

## Project Summary

**Tujuan:** Mengkonversi file MIDI menjadi simulasi penekanan keyboard otomatis untuk game piano berbasis keyboard (_Sky: Children of the Light_, _Piano Tiles_).

**Tech Stack Utama:**

| Komponen | Detail |
|---|---|
| Runtime | Python 3.12 (3.13+ tidak didukung untuk build Nuitka) |
| GUI | Tkinter (stdlib) + ttk |
| MIDI Parser | `mido` (lazy import) |
| Keyboard Sim | `keyboard` library (lazy import, butuh admin) |
| Config | JSON flat file (`playSong_config.json`) |
| Build | PyInstaller (`.spec`) atau Nuitka (`--mingw64`) |
| Platform | Windows-only (global keyboard hook) |

**Pola Arsitektur:** **Modular package** — 18 file Python di `src/`, masing-masing ≤ 100 baris. State GUI di-pass antar modul via **context dict** (`ctx`). Concurrency playback dihandle dengan `threading.Timer` + generation counter (`_play_gen`).

---

## Clean Tree

```
MidiToTyping/
├── playSong_clean.py            # entry point: main() + hotkey handlers
├── playSong_clean.spec          # PyInstaller build config
├── CLAUDE.md
├── README.md
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── constants.py             # global state + APP_VERSION/APP_DATE/APP_AUTHOR
│   ├── strings.py               # STRINGS bilingual dict (id / en)
│   ├── themes.py                # THEMES: Zinc + Slate (dark/light) shadcn
│   ├── config.py                # load/save playSong_config.json
│   ├── keyboard_sim.py          # press/release/is_shifted + whitelist
│   ├── midi_parser.py           # MIDI → beat/key array (raises MidoNotAvailable)
│   ├── playback.py              # parse_info + play_next_note engine
│   └── gui/
│       ├── __init__.py
│       ├── splash.py            # splash screen (pertama yang render)
│       ├── widgets.py           # make_btn, make_seg_btn, rebuild_seg
│       ├── info_popup.py        # popup ℹ (About)
│       ├── header.py            # title + theme/palette/lang seg buttons
│       ├── folder_nav.py        # folder navigation state & handlers
│       ├── folder_pane.py       # left panel widgets + speed slider
│       ├── music_pane.py        # right panel widgets + refresh/sort
│       ├── bottom.py            # bottom buttons + event bindings
│       ├── repaint.py           # live theme/palette update
│       ├── process_file.py      # GUI orchestrator (lazy-loaded)
│       ├── player_popup.py      # in-app player popup (buttons + note history)
│       └── _parse_handler.py    # safe_parse wrapper with error dialog
│
├── docs/
│   ├── SYSTEM_MAP.md            # file ini
│   └── CLAUDE_CODE_TOKEN_AUDIT_RECIPE.md
│
└── tests/
    ├── test_playSong.py         # 7 test groups × 17 assertions
    ├── test_midi.py
    ├── simulasi_play.py
    ├── test.mid, test_delay.mid
    └── test_songs/
```

> **Diabaikan dari tree:** `dist/`, `dist_nuitka/`, `build/`, `__pycache__/`, `archive/`, `.claude/`

---

## Core Logic Flow

### Alur Startup
```
main()  [playSong_clean.py]
  ├─ load_config()                        # src.config
  ├─ keyboard.on_press_key() × 4          # DELETE/HOME/END/INSERT (lazy import)
  ├─ show_splash()                        # src.gui.splash — user sees splash
  │
  └─ (lazy) from src.gui.process_file import process_file
     └─ process_file() loop
         ├─ build ctx (C, S, state lists)
         ├─ build_header(ctx)             # header + info button
         ├─ init_folder_nav(ctx)
         ├─ build_folder_pane(ctx)
         ├─ init_music_logic(ctx)
         ├─ build_music_pane(ctx)
         ├─ build_bottom(ctx)
         └─ root.mainloop()
```

### Alur Playback (hotkey DELETE)
```
on_delete_press()  [playSong_clean.py]
  └─ toggle state.is_playing, increment _play_gen
     └─ Thread → play_next_note(gen)      # src.playback
           ├─ if gen != _play_gen: return (stale timer guard)
           ├─ press_letter / release_letter
           │    └─ _safe(letter) → whitelist check
           ├─ stored_index += 1
           ├─ delay > 0: threading.Timer → play_next_note(gen)
           └─ delay == 0: daemon Thread → play_next_note(gen)
```

### Alur Reload (Language toggle)
```
Klik 'ID' / 'EN' → set_lang(lang)
  ├─ state.LANG = lang; save_config()
  ├─ ctx['selected_path'][0] = '__RELOAD__'
  └─ root.after_idle(close_window)
       └─ process_file() return '__RELOAD__'
            └─ main() loop continue → re-enter process_file
```

### Alur Repaint (Theme/Palette — tanpa reload)
```
Klik 'Dark'/'Light' atau 'Zinc'/'Slate' → set_theme/set_palette
  ├─ state.THEME/PALETTE = new; save_config()
  └─ repaint(ctx)                         # src.gui.repaint
       ├─ C.clear(); C.update(THEMES[...])  # in-place (lambda bindings auto-follow)
       ├─ ttk.Style reconfigure
       └─ 25+ widgets .configure(bg, fg, ...)
```

---

## Context Dict (`ctx`)

Setelah refactor, `process_file()` tidak lagi closure raksasa. Shared state dipass via dict:

| Key group | Contoh | Diisi oleh | Dipakai oleh |
|---|---|---|---|
| Tk objects | `root`, `C`, `S`, `style` | `process_file` | semua |
| Widgets (25+) | `frm_top`, `btn_play`, `tree`, `folder_lb`, dll | builder functions | `repaint` |
| State lists | `nav_folder`, `nav_stack`, `active_folder`, `music_files`, `sort_key_music` | `process_file` init | folder_nav / music_pane |
| Tk vars | `search_var`, `speed_var` | music_pane / folder_pane | bottom |
| Callbacks | `set_lang`, `set_theme`, `close_window`, `repaint`, `refresh_music`, `load_folder_pane`, `confirm_select` | sub-init functions | seluruh GUI |

**Invariant penting:** `ctx['C']` harus dict object yang sama sepanjang sesi — di-mutate in-place oleh `repaint()` agar lambda hover bindings yang capture `C` by reference otomatis melihat warna baru.

---

## Key Modules

| File | Fungsi utama | Peran |
|---|---|---|
| `playSong_clean.py` | `main()`, hotkey handlers | Entry + global hotkey registration |
| `src/constants.py` | konstanta + `APP_*` metadata | Single source of truth |
| `src/config.py` | `load_config()`, `save_config()` | Persist LANG/THEME/PALETTE/folders |
| `src/keyboard_sim.py` | `press_letter`, `release_letter`, `_safe()` | Keyboard sim + whitelist |
| `src/midi_parser.py` | `parse_song_file()`, `MidoNotAvailable` | MIDI → note list |
| `src/playback.py` | `parse_info()`, `play_next_note()` | Playback engine + gen-counter safe |
| `src/gui/process_file.py` | `process_file()` | GUI orchestrator (lazy-loaded) |
| `src/gui/repaint.py` | `repaint(ctx)` | Live theme/palette update |
| `src/gui/info_popup.py` | `show_info_popup(root, C, S)` | About dialog |

---

## Data & Config

**Config file:** `playSong_config.json` di direktori exe/script.

```json
{
  "lang":    "id" | "en",
  "theme":   "dark" | "light",
  "palette": "celestial" | "grand_piano",
  "folders": ["C:/path/to/songs", ...]
}
```

> **Label UI:** palette `celestial` → **Zinc**, `grand_piano` → **Slate** (shadcn). Nama kunci lama dipertahankan untuk kompatibilitas config.

**Temp file runtime:** `~midi_<random>.txt` via `tempfile.mkstemp(prefix='~midi_')`, dihapus di `try/finally`.

**Format teks internal:** `<timestamp_beat>  <karakter>`. Prefix `~` = note_off. `tempo=<bpm>` = ubah tempo mid-song.

---

## Performance (after 2026-04-23 optimization)

Lazy-import strategy pindahkan heavy modules dari startup-path ke on-demand:

| Modul | Di-defer dari | Saved |
|---|---|---|
| `src.gui.process_file` (+ transitif) | top-level `playSong_clean.py` → `main()` | ~16 ms |
| `tempfile` | `midi_parser` top → `_convert_midi_to_txt` | 7.4 ms |
| `webbrowser` | `info_popup` top → click handler | 4.4 ms |
| `tkinter.filedialog` | `folder_nav` top → `on_add_folder` | 1.4 ms |
| `datetime` | `bottom` top → `on_tree_select` | 0.4 ms |
| `tkinter.messagebox` | `bottom` top → error handlers | ~0.3 ms |

Net: **~25–30% lebih cepat** time-to-visible-splash (Python module-load 85 ms → ~60 ms).

**PyInstaller excludes (diperluas):** numpy/pandas/matplotlib/scipy/PIL/pytest/email/html/http/urllib/xml/bz2/lzma/sqlite3/argparse/logging.handlers/distutils.

---

## Security Posture

| Attack surface | Mitigasi |
|---|---|
| Malicious MIDI → arbitrary keystrokes (admin privilege) | Whitelist `_ALLOWED` di `keyboard_sim._safe()` — hanya alfanumerik + symbol piano |
| Temp file race (hardcoded name) | `tempfile.mkstemp(prefix='~midi_')` random + `try/finally` cleanup |
| `sys.exit(1)` dari parser library | Diganti `raise MidoNotAvailable` — caller GUI yang decide |
| URL injection via f-string | `info_popup._GITHUB_URL` hardcoded literal |
| Config JSON trust | `isinstance(p, str)` validation di `load_config` |

---

## Risks / Blind Spots

| Risiko | Detail |
|---|---|
| **Global state tanpa lock** | `state.stored_index`, `is_playing`, `_play_gen` diakses lintas-thread; guard = generation counter |
| **Timer jitter Windows** | `threading.Timer` ±10–15 ms; tidak ada drift compensation |
| **Reload full window (bahasa)** | Toggle bahasa close + buka window; kecil flicker. Theme/palette pakai repaint live. |
| **`_scan_flat` non-rekursif** | Scan per-folder; subfolder via navigator bukan scan otomatis |
| **`print()` saat `console=False`** | Debug output tidak visible di exe — perlu rebuild dengan `console=True` |
| **`input()` saat `console=False`** | `sys.stdin` None → `RuntimeError: lost sys.stdin`. Dimitigasi: diganti **player popup** (`src/gui/player_popup.py`) — blocking via `root.mainloop()`, stdout di-tap ke Text widget untuk note history |

---

## Test Coverage

`tests/test_playSong.py` — 17 assertion lintas 7 test group. Stub module `keyboard` agar test jalan tanpa admin. Import dari `src.*` setelah refactor.

**Jalankan:** `PYTHONIOENCODING=utf-8 python tests/test_playSong.py`

---

## Docs Index

| File | Untuk |
|---|---|
| [SYSTEM_MAP.md](SYSTEM_MAP.md) | File ini — kompas arsitektur |
| [../README.md](../README.md) | User-facing documentation |
| [../CLAUDE.md](../CLAUDE.md) | Panduan Claude Code AI assistant |
| [CLAUDE_CODE_TOKEN_AUDIT_RECIPE.md](CLAUDE_CODE_TOKEN_AUDIT_RECIPE.md) | Tool audit token (standalone) |
