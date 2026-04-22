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
python tests/test_playSong.py
python tests/test_midi.py
```

**Build ke .exe (PyInstaller — rekomendasi):**
```bash
# Install pyinstaller + dependencies ke tool environment (sekali saja)
uv tool install pyinstaller --with keyboard --with mido

# Build
%USERPROFILE%\.local\bin\pyinstaller.exe playSong_clean.spec --noconfirm
# Output: dist/playSong_clean.exe (~10 MB, no console window)
```

> **Catatan build:** `keyboard` dan `mido` harus ada di environment PyInstaller. Jika lupa: `uv tool install pyinstaller --with keyboard --with mido --force`.

**Build ke .exe (Nuitka — lebih kecil & startup lebih cepat):**

Nuitka mengkompilasi Python ke C native. Membutuhkan **Python 3.12** (bukan 3.13+) karena `--mingw64` tidak support Python 3.13+. Output: **~8.5 MB** vs PyInstaller ~10.3 MB.

```bash
# Install Python 3.12 dan Nuitka (sekali saja)
uv python install 3.12
uv tool install nuitka --python 3.12 --with keyboard --with mido --with zstandard --force

# Build (MinGW64 di-download otomatis ~100MB pertama kali)
%USERPROFILE%\AppData\Roaming\uv\tools\nuitka\Scripts\python.exe -m nuitka ^
  --standalone --onefile --windows-console-mode=disable ^
  --enable-plugin=tk-inter --include-module=keyboard --include-package=mido ^
  --mingw64 --lto=yes --assume-yes-for-downloads ^
  --output-filename=playSong_clean.exe --output-dir=dist_nuitka playSong_clean.py
# Output: dist_nuitka/playSong_clean.exe (~8.5 MB, no console window)
```

> **Catatan:** Gunakan Python 3.12, bukan 3.13+. MSVC tidak diperlukan — MinGW64 (GCC 14.2) di-download otomatis oleh Nuitka.

## Startup Optimizations (applied)

| Teknik | Detail |
|--------|--------|
| **Lazy `import keyboard`** | Hanya diimport saat `press_letter()`, `release_letter()`, `main()` dipanggil — bukan saat module load |
| **`optimize=2` di spec** | PyInstaller strip docstrings & assertions → bundle lebih kecil |
| **`excludes` di spec** | Numpy, pandas, matplotlib, scipy, PIL, pytest, asyncio, dll tidak dibundle |
| **`OrderedDict` tidak diimport ulang** | Dipindah ke top `process_file()`, bukan di dalam `refresh()` yang dipanggil berulang |

## Skalabilitas (catatan ke depan)

- **1000+ file MIDI**: `refresh()` sort + rebuild tree tiap keystroke; tambah debounce 200ms pada `search_var.trace_add` jika lag
- **Scan folder besar**: `os.walk()` sudah lazy; untuk >10.000 file pertimbangkan background thread + progress bar
- **MIDI besar**: `mido.merge_tracks()` load seluruh file ke memori; untuk file >50 MB pertimbangkan streaming parser
- **Multi-lagu sekaligus**: arsitektur saat ini serial (satu lagu); paralel playback butuh refactor state menjadi class

## Architecture

Proyek ini adalah **single-file monolith** (`playSong_clean.py`, ~1060 baris) dengan alur data sebagai berikut:

```
main() → show_splash() [splash screen 2 detik]
       → process_file() [GUI Tkinter — loop jika '__RELOAD__']
           ↓ scan_folders() → rekursif cari .mid/.midi
           ↓ user pilih lagu
         parse_song_file() → mido → beat/key array
           ↓ on_delete_press() → toggle play/pause
         play_next_note(gen) → tekan keyboard → threading.Timer → rekursi
```

### Komponen Utama

**Keyboard Simulation** — `press_letter()` / `release_letter()` / `is_shifted()`: Menangani penekanan tombol biasa dan yang butuh Shift (e.g., `!`, `@`, `#`). Mapping ada di konstanta `CONVERSION_CASES` dan `scale` (61 tuts piano).

**MIDI Parser** — `parse_song_file()`: Menggunakan `mido` untuk membaca file `.mid`, memetakan MIDI note ke karakter keyboard. Note di luar range 61 tuts di-fold ke oktaf terdekat. Semua track di-flatten menjadi satu sequence.

**Splash Screen** — `show_splash()`: Window borderless terpusat dengan animasi progress bar selama ~2 detik. Dipanggil sekali di awal `main()`. Menggunakan `THEMES[THEME]` sehingga warnanya mengikuti tema aktif.

**GUI** — `process_file()` (~550 baris Tkinter): Picker multi-folder dengan filter real-time, sort kolom, speed slider (0.25× – 3.0×), navigasi keyboard, toggle bahasa, dan toggle tema. State folder tersimpan di `folder_history`. Mengembalikan `'__RELOAD__'` saat toggle bahasa/tema agar `main()` memanggil ulang tanpa kehilangan state.

**Localization** — `STRINGS: dict`: Dictionary dua bahasa (`'id'` / `'en'`) berisi semua teks UI. Diakses via `STRINGS[LANG]`. Global `LANG` diubah oleh tombol 🌐 di header.

**Theme** — `THEMES: dict`: Dua palette warna (`'dark'` / `'light'`). Diakses via `THEMES[THEME]`. Global `THEME` diubah oleh tombol ☀️/🌙 di header.

**Playback Engine** — `play_next_note(gen)` + `parse_info()`: `parse_info()` mengkonversi timestamp absolut ke delay relatif. `play_next_note()` rekursif menjadwalkan note berikutnya via `threading.Timer(delay / playback_speed)`. Note dengan delay nol dijalankan di daemon thread.

**Generation Counter** (`_play_gen`): Solusi concurrency — setiap pause/resume/reset menginkremen `_play_gen`. Timer yang stale (gen != _play_gen) langsung return, mencegah double-press.

**Hotkeys** (global, via `keyboard` library):
- `DELETE` — Play/Pause toggle
- `HOME` — Rewind 10 note
- `END` — Skip 10 note (atau reset jika hampir selesai)
- `INSERT` — Restart dari awal

### Global State

```python
LANG            # str   — bahasa aktif: 'id' | 'en'
THEME           # str   — tema aktif: 'dark' | 'light'
is_playing      # bool  — apakah sedang playback
stored_index    # int   — posisi note saat ini
playback_speed  # float — multiplier kecepatan
info_tuple      # (tempo, None, [[timestamp, [keys]], ...])
_play_gen       # int   — generation counter untuk concurrency
folder_history  # list  — folder yang ditambahkan user
```

### Reload Mechanism (Lang/Theme Toggle)

Ketika user klik toggle bahasa atau tema di header:
1. Global `LANG` atau `THEME` diupdate
2. `selected_path[0]` diset ke `'__RELOAD__'`
3. Window ditutup via `_close_window()`
4. `process_file()` return `'__RELOAD__'`
5. `main()` loop `continue` → buka kembali `process_file()` dengan setting baru
6. `folder_history` tetap tersimpan di global → pilihan folder tidak hilang

## Testing Strategy

Test di `tests/test_playSong.py` meng-stub modul `keyboard` agar bisa berjalan tanpa admin:
```python
keyboard_stub = types.ModuleType('keyboard')
sys.modules['keyboard'] = keyboard_stub
import playSong_clean  # safe import
```

7 test mencakup: CONVERSION_CASES, tempo marker removal, delay calculation, generation counter, play/pause toggle, skip/reset logic, dan `is_shifted()`.

## Known Constraints

- **Windows-only** — `keyboard` library hanya support Windows untuk global hook
- **Admin required** — global keyboard hook butuh elevated privilege
- **~10-15ms timer jitter** — akurasi `threading.Timer` di Windows
- **61-tuts limit** — note di luar range C2–C7 di-fold, bukan dipotong
- **Multi-channel flatten** — semua track MIDI digabung; instrumen non-piano ikut terpetakan
- **Slow .exe startup (PyInstaller)** — single-file bundle mengekstrak ke temp setiap run (~3-5 detik normal); Nuitka jauh lebih cepat
- **Nuitka butuh Python 3.12** — `--mingw64` tidak support Python 3.13+; gunakan `uv tool install nuitka --python 3.12 ...`
- **console=False di spec** — exe tidak munculkan CMD window; jika butuh debug ganti ke `True`
- **keyboard + mido wajib di env PyInstaller** — harus `uv tool install pyinstaller --with keyboard --with mido`
