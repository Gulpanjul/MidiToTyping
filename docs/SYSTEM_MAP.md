# SYSTEM_MAP.md — playSong (MidiToTyping)

> Dibuat: 2026-04-22 · Entrypoint: `playSong_clean.py`

---

## Project Summary

**Tujuan:** Mengkonversi file MIDI menjadi simulasi penekanan keyboard otomatis untuk game piano berbasis keyboard (_Sky: Children of the Light_, _Piano Tiles_). User memilih file lagu via GUI, lalu aplikasi menekan tombol keyboard sesuai timing MIDI.

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

**Pola Arsitektur:** Single-file monolith (~1316 baris). Tidak ada layer terpisah — semua fungsi berada dalam satu file. State dikelola melalui variabel global. Concurrency dihandle dengan `threading.Timer` + generation counter (`_play_gen`).

---

## Core Logic Flow (Function-Level)

### Alur Startup
```
main()
  └─> load_config()             — baca playSong_config.json (lang/theme/palette/folders)
  └─> keyboard.on_press_key()   — daftarkan hotkeys global (DELETE/HOME/END/INSERT)
  └─> show_splash()             — tampilkan splash screen Tkinter ~2 detik
  └─> [loop] process_file()     — GUI picker (Tkinter mainloop)
        └─> _scan_flat()        — os.listdir non-rekursif cari .mid/.midi di folder aktif
        └─> user pilih file
        └─> return filepath
  └─> parse_song_file(filepath) — mido baca MIDI → tulis ~temp_midi_convert.txt → parse → list notes
  └─> parse_info()              — konversi timestamp absolut → delay relatif
  └─> info_tuple = hasil parse  — simpan di global
```

### Alur Playback
```
Hotkey DELETE
  └─> on_delete_press()
        └─> toggle is_playing, increment _play_gen
        └─> [jika PLAY] Thread → play_next_note(gen)
              └─> notes[stored_index] → press_letter() / release_letter()
              └─> increment stored_index
              └─> delay > 0 → threading.Timer(delay/playback_speed) → play_next_note(gen) [rekursi]
              └─> delay == 0 → daemon Thread → play_next_note(gen)
              └─> gen != _play_gen → return (stale timer guard)
```

### Alur Hotkey Navigasi
```
HOME  → on_home_press()   → stored_index -= 10 (rewind)
END   → on_end_press()    → stored_index += 10, atau reset jika melebihi akhir
INSERT→ on_insert_press() → reset stored_index=0, restart playback
```

### Alur Lang/Theme Toggle (Reload Mechanism)
```
Klik toggle 🌐 / ☀️🌙 / 🌌🎹 di GUI
  └─> update global LANG / THEME / PALETTE
  └─> selected_path[0] = '__RELOAD__'
  └─> _close_window() → window tutup
  └─> process_file() return '__RELOAD__'
  └─> main() loop continue → process_file() dipanggil ulang
  └─> folder_history tetap (tidak hilang)
  * Catatan: perubahan tema/palet bisa terjadi live via repaint() tanpa reload penuh
```

---

## Clean Tree

```
MidiToTyping/
├── playSong_clean.py          # Entrypoint + seluruh logika aplikasi
├── playSong_clean.spec        # Konfigurasi build PyInstaller
├── CLAUDE.md                  # Panduan Claude Code
├── README.md                  # Dokumentasi publik
├── .env                       # Hanya berisi: /docs (gitignore pointer)
│
├── docs/
│   ├── SYSTEM_MAP.md                    # (file ini) — navigasi utama proyek + indeks docs
│   ├── LSH_FRONTEND_STANDARDS.md        # Standar LSH Group untuk proyek frontend
│   ├── QUICK_REFERENCE.md               # Cheat sheet ringkas dari LSH_FRONTEND_STANDARDS
│   ├── DELEGATION_PROMPT.md             # Template prompt untuk membuat proyek frontend baru
│   ├── PROJECT_TEMPLATE.md              # Panduan setup proyek baru step-by-step
│   ├── PORTABILITY_ANALYSIS.md          # Analisis portabilitas standar ke framework lain
│   └── CLAUDE_CODE_TOKEN_AUDIT_RECIPE.md # Tool audit token Claude Code (portable, standalone)
│
└── tests/
    ├── test_playSong.py       # Unit test logika inti (7 test, tanpa admin)
    ├── test_midi.py           # Script debug manual MIDI parsing
    ├── simulasi_play.py       # Script debug manual simulasi playback
    ├── test.mid               # MIDI fixture test
    ├── test_delay.mid         # MIDI fixture test delay
    └── test_songs/            # Folder sampel file lagu
```

> **Diabaikan dari tree:** `archive/`, `dist/`, `dist_nuitka/`, `__pycache__/`

---

## Module Map (The Chapters)

### `playSong_clean.py`

| Fungsi/Konstanta | Baris | Peran |
|---|---|---|
| `LANG`, `THEME`, `PALETTE` | 42–44 | Global state bahasa, tema, palet warna aktif |
| `is_playing`, `stored_index`, `_play_gen` | 45–49 | Global state playback + concurrency guard |
| `folder_history` | 50 | Daftar folder yang ditambahkan user (persisten via config) |
| `CONVERSION_CASES` | 52–55 | Mapping karakter simbol ke tombol numerik (e.g. `#` → `3`) |
| `STRINGS` | 62–143 | Semua teks UI dalam 2 bahasa (`id`/`en`) |
| `THEMES` | 148–197 | Dua palet warna (`celestial`/`grand_piano`) × dua mode (`dark`/`light`) |
| `_config_path()` | 203 | Resolusi path `playSong_config.json` (mendukung frozen/exe) |
| `load_config()` | 211 | Baca `playSong_config.json` → update global lang/theme/palette/folders |
| `save_config()` | 228 | Tulis state saat ini ke `playSong_config.json` |
| `is_shifted(char)` | 244 | Cek apakah karakter butuh Shift saat ditekan |
| `press_letter(letter)` | 256 | Simulasi tekan satu karakter keyboard (handle Shift) |
| `release_letter(letter)` | 270 | Simulasi lepas satu karakter keyboard |
| `parse_song_file(filepath)` | 283 | MIDI/txt → list `[[timestamp, keys], ...]`; tulis temp file jika MIDI |
| `show_splash()` | 376 | Splash screen Tkinter borderless + progress bar animasi ~2 detik |
| `process_file()` | 437 | GUI Tkinter lengkap: folder picker, file list, speed slider; return `info_tuple` / `'__RELOAD__'` / `None` |
| `floor_to_zero(value)` | 1145 | Helper: return `None` jika value ≤ 0 |
| `parse_info()` | 1149 | Konversi timestamp absolut → delay relatif; handle `tempo=` marker mid-song |
| `play_next_note(gen)` | 1174 | Playback engine rekursif: tekan tombol → jadwal note berikutnya via Timer |
| `on_delete_press(event)` | 1214 | Hotkey DELETE: toggle play/pause, increment `_play_gen` |
| `on_home_press(event)` | 1227 | Hotkey HOME: rewind 10 note |
| `on_end_press(event)` | 1233 | Hotkey END: skip 10 note atau reset jika melebihi akhir |
| `on_insert_press(event)` | 1246 | Hotkey INSERT: restart playback dari awal |
| `main()` | 1259 | Entrypoint: `load_config` → daftar hotkeys → `show_splash` → loop `process_file` → `parse_info` → playback siap |

### `tests/test_playSong.py`

| Fungsi | Peran |
|---|---|
| Stub `keyboard` | Replace modul `keyboard` dengan dummy agar bisa jalan tanpa admin |
| 7 fungsi `check()` | Test: `CONVERSION_CASES`, `parse_info`, generation counter, toggle play/pause, skip/reset logic, `is_shifted()` |

### `tests/test_midi.py`

Script satu-kali untuk debug manual: buat `test.mid` → baca → print mapping MIDI note → karakter keyboard.

### `tests/simulasi_play.py`

Script satu-kali untuk debug manual alur playback tanpa keyboard fisik.

### `playSong_clean.spec`

Konfigurasi PyInstaller: bundle `mido` (semua submodule via `collect_submodules`), `keyboard` sebagai hiddenimport, exclude library berat (numpy/pandas/matplotlib/dll), `optimize=2`, `console=False`.

---

## Data & Config

**Config file:** `playSong_config.json` — dibuat otomatis di direktori yang sama dengan `playSong_clean.py` (atau direktori exe jika frozen).

**Skema config:**
```json
{
  "lang"    : "id" | "en",
  "theme"   : "dark" | "light",
  "palette" : "celestial" | "grand_piano",
  "folders" : ["path/ke/folder1", "path/ke/folder2"]
}
```

**File temp runtime:** `~temp_midi_convert.txt` — dibuat sementara di direktori exe/script saat parsing MIDI, tidak dihapus setelah selesai.

**File input lagu:**
- `.mid` / `.midi` — diparse via `mido`, dikonversi ke format teks internal
- `.txt` (format internal) — `<timestamp_beat>  <karakter>` per baris; prefix `~` = note_off; `tempo=<bpm>` = ubah tempo

**Folder output build:**
- `dist/` — output PyInstaller (`playSong_clean.exe` ~10 MB)
- `dist_nuitka/` — output Nuitka (`playSong_clean.exe` ~8.5 MB)

**Tidak ada database** — semua state in-memory atau di config JSON.

---

## External Integrations

| Library | Versi | Peran | Dipanggil di |
|---|---|---|---|
| `keyboard` | - | Global keyboard hook + simulasi tekan tombol | `press_letter()`, `release_letter()`, `main()` (lazy import) |
| `mido` | - | Baca dan parse file MIDI | `parse_song_file()` (lazy import) |
| `tkinter` | stdlib | GUI: window, widget, dialog | `show_splash()`, `process_file()` |
| `threading` | stdlib | Timer rekursif untuk playback + daemon thread | `play_next_note()`, hotkey handlers |
| `json` | stdlib | Baca/tulis `playSong_config.json` | `load_config()`, `save_config()` |

**Tidak ada koneksi internet / API eksternal.**

---

## Risks / Blind Spots

| Risiko | Detail |
|---|---|
| **Global state tanpa lock** | `stored_index`, `is_playing`, `_play_gen` diakses dari GUI thread dan daemon thread tanpa `threading.Lock`. `_play_gen` increment berfungsi sebagai guard tetapi bukan atomic di CPython tanpa GIL (Python 3.13+). |
| **Akurasi timer Windows** | `threading.Timer` di Windows memiliki jitter ~10–15ms. Tidak ada kompensasi drift — delay bisa akumulasi pada lagu panjang. |
| **process_file() terlalu panjang** | Fungsi `process_file()` (~700 baris) berisi semua logika GUI termasuk nested function definitions. Sulit di-trace tanpa membaca keseluruhan. |
| **`_scan_flat()` non-rekursif** | Fungsi `_scan_flat()` hanya scan satu level folder (non-rekursif). Navigasi ke subfolder dilakukan via folder pane, bukan scan otomatis. |
| **Tidak ada logging ke file** | Semua output via `print()` ke stdout. Tidak ada log file — debug di exe (console=False) tidak bisa dilakukan tanpa rebuild. |
| **`folder_history` tidak dibersihkan** | Folder yang sudah dihapus dari disk tetap tersimpan di config dan bisa muncul kembali saat reload. |

---

## Docs Index

Panduan cepat untuk semua dokumen di folder ini:

| File | Untuk Siapa | Gunakan Ketika |
|---|---|---|
| [SYSTEM_MAP.md](SYSTEM_MAP.md) | Semua kontributor | Mulai sesi baru — kompas utama arsitektur playSong |
| [LSH_FRONTEND_STANDARDS.md](LSH_FRONTEND_STANDARDS.md) | Tim IT LSH Group | Referensi standar lengkap clean code & AI workflow untuk proyek frontend |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Developer aktif | Cheat sheet harian — template komponen, naming, do/don't |
| [DELEGATION_PROMPT.md](DELEGATION_PROMPT.md) | Tech lead / PM | Copy-paste prompt untuk mendelegasikan pembuatan proyek frontend baru ke AI |
| [PROJECT_TEMPLATE.md](PROJECT_TEMPLATE.md) | Developer setup | Panduan setup proyek Next.js baru step-by-step |
| [PORTABILITY_ANALYSIS.md](PORTABILITY_ANALYSIS.md) | Arsitek / pengambil keputusan | Mempertimbangkan adopsi struktur LSH ke stack non-React |
| [CLAUDE_CODE_TOKEN_AUDIT_RECIPE.md](CLAUDE_CODE_TOKEN_AUDIT_RECIPE.md) | Semua pengguna Claude Code | Install `/token-audit` command untuk memantau konsumsi token di workspace manapun |

**Hierarki dependensi docs LSH:**
```
LSH_FRONTEND_STANDARDS.md  ← source of truth
    ├── QUICK_REFERENCE.md          (subset ringkas)
    ├── DELEGATION_PROMPT.md        (template penggunaan)
    ├── PROJECT_TEMPLATE.md         (panduan setup)
    └── PORTABILITY_ANALYSIS.md     (analisis eksternal)

SYSTEM_MAP.md               ← spesifik proyek playSong (file ini)
CLAUDE_CODE_TOKEN_AUDIT_RECIPE.md  ← standalone tool, independen
```
