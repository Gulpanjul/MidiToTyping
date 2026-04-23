<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">playSong — MIDI to Keyboard Auto-Player</h3>

  <p align="center">
    Konversi file MIDI menjadi simulasi penekanan keyboard otomatis untuk game piano.
    <br />
    <a href="docs/SYSTEM_MAP.md"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Gulpanjul/MidiToTyping/issues/new?labels=bug">Report Bug</a>
    &middot;
    <a href="https://github.com/Gulpanjul/MidiToTyping/issues/new?labels=enhancement">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#architecture">Architecture</a></li>
    <li><a href="#file-format">File Format</a></li>
    <li><a href="#build">Build ke .exe</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

**playSong** adalah aplikasi Python yang mengkonversi file MIDI menjadi simulasi penekanan keyboard otomatis — cocok untuk game piano berbasis keyboard seperti **Sky: Children of the Light** dan **Piano Tiles**. User memilih file lagu via GUI, lalu aplikasi menekan tombol keyboard sesuai timing MIDI secara otomatis.

Fitur utama:
* Multi-folder picker dengan filter real-time, sort kolom, dan navigasi keyboard
* Slider kecepatan playback 0.25× – 3.00×
* Hotkey global: Play/Pause, Rewind, Skip, Restart
* Dukungan tempo marker in-song (`tempo=120`)
* UI ber-style **shadcn**: dua tema (dark/light), dua palet warna (**Zinc** & **Slate**), dua bahasa (ID/EN)
* Tombol **Info (ℹ)** di header — popup berisi versi, author, hotkey cheat-sheet, link GitHub
* **Arsitektur modular** — 18 file Python, masing-masing ≤ 100 baris, dengan shared context dict
* **Startup cepat** — lazy-import strategi: splash muncul sebelum modul berat di-load

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Python][Python-badge]][Python-url]
* [![Tkinter][Tkinter-badge]][Tkinter-url]
* [![mido][mido-badge]][mido-url]
* [![keyboard][keyboard-badge]][keyboard-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

* Python 3.10+ (disarankan 3.12 untuk build Nuitka)
* Windows (global keyboard hook tidak tersedia di Linux/macOS)
* **Hak administrator Windows** — dibutuhkan oleh `keyboard` library untuk global hook

### Installation

1. Clone repo
   ```sh
   git clone https://github.com/Gulpanjul/MidiToTyping.git
   cd MidiToTyping
   ```

2. Install dependencies
   ```sh
   pip install keyboard mido
   ```

3. Jalankan sebagai Administrator
   ```sh
   python playSong_clean.py
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE -->
## Usage

1. Jalankan program → splash screen muncul ~2 detik, lalu GUI pemilih lagu terbuka
2. Klik **➕ Tambah** untuk menambahkan folder berisi file `.mid` / `.midi`
3. Program scan rekursif semua subfolder secara otomatis
4. Filter dengan search bar, pilih lagu, set kecepatan dengan slider
5. Klik **▶ Mainkan File Ini** (atau double-click / tekan Enter)
6. Fokuskan window game target, lalu gunakan hotkey berikut:

### Hotkey Playback

| Tombol | Fungsi |
|--------|--------|
| `DELETE` | Play / Pause toggle |
| `HOME` | Rewind — mundur 10 nada |
| `END` | Skip — maju 10 nada (atau reset jika mendekati akhir) |
| `INSERT` | Restart dari awal |

### Known Limitations

1. **Window game harus punya fokus** — `keyboard` library mensimulasikan penekanan tombol fisik secara global; mengetik di aplikasi lain saat lagu main akan ter-interrupt.
2. **Tidak bisa target HWND spesifik** — game modern (Unity/Unreal) menggunakan DirectInput/Raw Input yang mem-bypass Windows message queue.
3. **Butuh admin di Windows** — global keyboard hook memerlukan elevated privileges.
4. **MIDI multi-channel flattened** — semua track digabung; not di luar range 61-tombol di-fold ke oktaf terdekat.
5. **Timer jitter ~10–15ms** — `threading.Timer` di Windows tidak presisi sempurna; lagu BPM sangat tinggi mungkin terasa sedikit off.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ARCHITECTURE -->
## Architecture

Proyek ini di-refactor dari monolith ~1400 baris menjadi package modular `src/` — tiap file ≤ 100 baris, state shared via context dict (`ctx`) yang dipass antar modul GUI.

```
playSong_clean.py            # entry point: main() + hotkey handlers
src/
├── constants.py             # global state + APP_VERSION metadata
├── strings.py               # STRINGS bilingual dict (id / en)
├── themes.py                # palet warna shadcn: Zinc + Slate (dark/light)
├── config.py                # load/save playSong_config.json
├── keyboard_sim.py          # press/release/is_shifted + whitelist
├── midi_parser.py           # MIDI → beat/key array
├── playback.py              # parse_info + play_next_note engine
└── gui/
    ├── splash.py            # splash screen (rendered first)
    ├── widgets.py           # make_btn, rebuild_seg factories
    ├── info_popup.py        # tombol ℹ popup (About)
    ├── header.py            # title + theme/palette/lang seg controls
    ├── folder_nav.py        # folder navigation logic
    ├── folder_pane.py       # left panel: folder list + speed slider
    ├── music_pane.py        # right panel: file list + search
    ├── bottom.py            # bottom buttons + event bindings
    ├── repaint.py           # live theme/palette update
    ├── process_file.py      # GUI orchestrator (lazy-loaded)
    └── _parse_handler.py    # safe_parse() wrapper with error dialog
```

**Design principles applied:**
* Context-dict pattern menggantikan monolith closure
* Lazy imports untuk `process_file`, `tempfile`, `webbrowser`, `filedialog`, `datetime` → time-to-splash ~25–30% lebih cepat
* Whitelist karakter di `keyboard_sim.press_letter` → defense-in-depth saat running as admin
* shadcn-inspired palette, border-b 1px separator, consistent font weight di seg controls
* Temp file via `tempfile.mkstemp` + `try/finally` cleanup (tidak lagi hardcoded name)

Lihat [docs/SYSTEM_MAP.md](docs/SYSTEM_MAP.md) untuk detail per-fungsi.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- FILE FORMAT -->
## File Format

### MIDI (direkomendasikan)

File `.mid` / `.midi` langsung didukung. Program otomatis mengonversi not MIDI ke mapping piano 61-tombol (C2–C7).

### Text Format (internal)

Saat memproses MIDI, program menghasilkan file temp (di-generate via `tempfile.mkstemp` dengan prefix `~midi_`, dihapus otomatis setelah parse selesai):

```
<timestamp_beat>  <tombol>
0.0000   q         ← tekan tombol 'q'
0.5000   we        ← tekan 'w' dan 'e' bersamaan
1.0000   ~q        ← lepaskan tombol 'q' (prefix ~)
1.5000   tempo=120 ← ubah BPM di tengah lagu
```

**Key scale** (61 tombol, C2 ke atas):
```
1!2@34$5%6^78*9(0qQwWeErtTyYuiIoOpPasSdDfgGhHjJklLzZxcCvVbBnm
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- BUILD -->
## Build ke .exe

### PyInstaller (direkomendasikan, ~10 MB)

```sh
uv tool install pyinstaller --with keyboard --with mido
%USERPROFILE%\.local\bin\pyinstaller.exe playSong_clean.spec --noconfirm
```

Output: `dist/playSong_clean.exe`

### Nuitka (lebih kecil & startup lebih cepat, ~8.5 MB)

Membutuhkan Python 3.12 (`--mingw64` tidak support Python 3.13+).

```sh
uv python install 3.12
uv tool install nuitka --python 3.12 --with keyboard --with mido --with zstandard --force

%USERPROFILE%\AppData\Roaming\uv\tools\nuitka\Scripts\python.exe -m nuitka ^
  --standalone --onefile --windows-console-mode=disable ^
  --enable-plugin=tk-inter --include-module=keyboard --include-package=mido ^
  --mingw64 --lto=yes --assume-yes-for-downloads ^
  --output-filename=playSong_clean.exe --output-dir=dist_nuitka playSong_clean.py
```

Output: `dist_nuitka/playSong_clean.exe`

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

- [x] MIDI auto-player dengan GUI multi-folder
- [x] Hotkey global (Play/Pause/Rewind/Skip/Restart)
- [x] Speed slider 0.25× – 3.00×
- [x] Tema dark/light + palet warna + bilingual UI
- [x] Build ke `.exe` (PyInstaller & Nuitka)
- [x] Arsitektur modular (18 file × ≤100 baris)
- [x] UI shadcn (palet Zinc + Slate, border 1px, font konsisten)
- [x] Info popup (versi, author, hotkey cheat-sheet)
- [x] Lazy imports (startup ~25–30% lebih cepat)
- [x] Keystroke whitelist (defense-in-depth)
- [ ] Kompensasi drift timer untuk lagu panjang
- [ ] Background thread untuk scan folder besar (>10.000 file)
- [ ] Debounce pada search bar untuk 1000+ file MIDI

Lihat [open issues](https://github.com/Gulpanjul/MidiToTyping/issues) untuk daftar fitur yang diusulkan dan known issues.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

Kontribusi sangat diapresiasi. Jika punya saran, silakan fork repo ini dan buat pull request, atau buka issue dengan tag `enhancement`.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Internal project. Tidak untuk distribusi eksternal tanpa izin.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Gulpanjul — [gulpa.andhikac@gmail.com](mailto:gulpa.andhikac@gmail.com)

Project Link: [https://github.com/Gulpanjul/MidiToTyping](https://github.com/Gulpanjul/MidiToTyping)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [mido — MIDI Objects for Python](https://mido.readthedocs.io/)
* [keyboard — Hook and simulate keyboard events](https://github.com/boppreh/keyboard)
* [Best-README-Template](https://github.com/othneildrew/Best-README-Template)
* [Img Shields](https://shields.io)
* [PyInstaller](https://pyinstaller.org/)
* [Nuitka](https://nuitka.net/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
[contributors-shield]: https://img.shields.io/github/contributors/Gulpanjul/MidiToTyping.svg?style=for-the-badge
[contributors-url]: https://github.com/Gulpanjul/MidiToTyping/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Gulpanjul/MidiToTyping.svg?style=for-the-badge
[forks-url]: https://github.com/Gulpanjul/MidiToTyping/network/members
[stars-shield]: https://img.shields.io/github/stars/Gulpanjul/MidiToTyping.svg?style=for-the-badge
[stars-url]: https://github.com/Gulpanjul/MidiToTyping/stargazers
[issues-shield]: https://img.shields.io/github/issues/Gulpanjul/MidiToTyping.svg?style=for-the-badge
[issues-url]: https://github.com/Gulpanjul/MidiToTyping/issues
[license-shield]: https://img.shields.io/badge/license-internal-lightgrey?style=for-the-badge
[license-url]: #license
[Python-badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://python.org/
[Tkinter-badge]: https://img.shields.io/badge/Tkinter-GUI-blue?style=for-the-badge
[Tkinter-url]: https://docs.python.org/3/library/tkinter.html
[mido-badge]: https://img.shields.io/badge/mido-MIDI-green?style=for-the-badge
[mido-url]: https://mido.readthedocs.io/
[keyboard-badge]: https://img.shields.io/badge/keyboard-hook-orange?style=for-the-badge
[keyboard-url]: https://github.com/boppreh/keyboard
