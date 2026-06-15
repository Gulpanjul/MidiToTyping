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
    <br />
    <a href="https://github.com/Gulpanjul/MidiToTyping/issues/new?labels=bug">Report Bug</a>
    &middot;
    <a href="https://github.com/Gulpanjul/MidiToTyping/issues/new?labels=enhancement">Request Feature</a>
  </p>
</div>



> **Tauri rewrite (v0.2.x) is the current build.** Vite + React 19 +
> TypeScript frontend dengan Rust backend. Drop the Administrator
> requirement, ~5 MB exe, custom title bar, no UAC. Implementasi Python
> lama dipindah ke [`legacy/`](legacy/) sebagai referensi.

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#install--run">Install & Run</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#architecture">Architecture</a></li>
    <li><a href="#file-format">File Format</a></li>
    <li><a href="#build">Build</a></li>
    <li><a href="#legacy-python-build">Legacy Python build</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

**playSong** mengkonversi file MIDI menjadi simulasi penekanan keyboard otomatis — cocok untuk game piano berbasis keyboard seperti **Sky: Children of the Light** dan **Piano Tiles**. User memilih file MIDI via GUI, lalu aplikasi menekan tombol keyboard sesuai timing MIDI secara otomatis.

Fitur utama:
* Multi-folder picker dengan filter real-time
* Slider kecepatan playback 0.25× – 3.00× dengan label difficulty (Beginner → Master)
* Hotkey global: Play/Pause (DELETE), Rewind (HOME), Skip (END), Restart (INSERT)
* Custom title bar tanpa Windows chrome standar
* Note log scrolling di player popup
* Dua tema (dark/light), dua palet warna (**Zinc** & **Slate**), dua bahasa (ID/EN)
* **Tidak butuh Administrator** — pakai Win32 API standar (`SetWindowsHookEx`, `SendInput`)
* Bundle kecil: ~5.36 MB exe / ~2.62 MB MSI / ~1.82 MB NSIS

### Built With

* [![Tauri][Tauri-badge]][Tauri-url]
* [![Rust][Rust-badge]][Rust-url]
* [![React][React-badge]][React-url]
* [![TypeScript][TypeScript-badge]][TypeScript-url]
* [![Vite][Vite-badge]][Vite-url]
* [![Tailwind][Tailwind-badge]][Tailwind-url]

Backend: [midly](https://crates.io/crates/midly) (zero-copy MIDI parser), [enigo](https://crates.io/crates/enigo) (synthetic keyboard injection), [tauri-plugin-global-shortcut](https://docs.rs/tauri-plugin-global-shortcut/) (global hotkey registration), [tokio](https://tokio.rs/) (async playback engine).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

* Windows 10/11 (Linux/macOS akan compile tapi playback di-disable — Windows-only)
* [Node.js 20+](https://nodejs.org/)
* [Rust toolchain](https://www.rust-lang.org/tools/install)
* (Opsional) [Tauri CLI](https://tauri.app/start/prerequisites/) untuk dev/build

### Install & Run

```bash
# 1. Clone
git clone https://github.com/Gulpanjul/MidiToTyping.git
cd MidiToTyping

# 2. Install frontend deps
cd app && npm install && cd ..

# 3. Hot-reload dev (spawns Vite + opens Tauri window)
cd src-tauri && cargo tauri dev
```

Atau download MSI/NSIS installer dari [Releases](https://github.com/Gulpanjul/MidiToTyping/releases).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE -->
## Usage

1. Buka aplikasi → window terbuka tanpa UAC prompt
2. Klik **➕** untuk menambah folder berisi file `.mid` / `.midi` (scan 1 level / non-rekursif — tambahkan subfolder secara terpisah bila perlu)
3. Pilih lagu, set kecepatan dengan slider (label difficulty update real-time)
4. Klik **▶ Mainkan File Ini** → player popup terbuka di state **paused**
5. Alt-tab ke window game target, fokus di sana
6. Tekan **DELETE** untuk mulai playback (atau klik tombol Mainkan di popup)

### Hotkey Playback (global)

| Tombol | Fungsi |
|--------|--------|
| `DELETE` | Play / Pause toggle |
| `HOME` | Rewind — mundur 10 nada |
| `END` | Skip — maju 10 nada (atau reset jika dekat akhir) |
| `INSERT` | Restart dari awal |

### Known Limitations

1. **Window game harus punya fokus** — `SendInput` tidak menargetkan HWND spesifik
2. **Game dengan DirectInput/Raw Input** mungkin bypass — game modern tertentu (Unreal/Unity) tidak menerima synthetic input
3. **MIDI multi-channel flatten** — semua track digabung, not di luar range 61-tombol di-fold ke oktaf terdekat
4. **Keyboard 65% (no nav cluster)** — HOME/END/INSERT secara fisik tidak ada; user harus pakai Fn-layer atau remap. Kandidat untuk in-app rewind/skip/restart buttons di v0.2.
5. **Default speed 0.95×** — kompensasi karena Rust `tokio::sleep` lebih presisi dari Python `threading.Timer`. User upgrading dari Python build akan merasakan tempo yang sama di 0.95× Tauri vs 1.0× Python.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ARCHITECTURE -->
## Architecture

```
app/                              — Vite + React 19 + TypeScript frontend
├── src/
│   ├── App.tsx                   — Shell wrapped in ConfigProvider + PlaybackProvider
│   ├── i18n/strings.ts           — port of legacy strings.py (id + en, 45 keys)
│   ├── theme/themes.ts           — port of legacy themes.py (4 combos × 11 keys)
│   ├── lib/tauri.ts              — typed invoke/listen wrappers
│   ├── contexts/                 — ConfigProvider, PlaybackProvider
│   ├── hooks/                    — useConfig, usePlayback, useTheme
│   └── components/
│       ├── ui/                   — Button, Slider, Input, Dialog (hand-rolled)
│       ├── TitleBar.tsx          — custom Win32 chrome
│       ├── Header.tsx            — title + theme/palette/lang toggles + Info button
│       ├── FolderPane.tsx        — folder list + speed slider w/ difficulty label
│       ├── MusicPane.tsx         — song table with debounced search
│       ├── BottomBar.tsx         — Play button
│       ├── PlayerSheet.tsx       — Dialog with progress + Play/Pause + Pilih Lagu Lain + Keluar + note log
│       ├── InfoPopup.tsx         — About modal (sectioned)
│       └── UnsupportedBanner.tsx — non-Windows guard banner
└── public/playsong-icon.png      — 32×32 title bar logo

src-tauri/                        — Tauri v2 Rust backend
├── src/
│   ├── main.rs                   — thin entry, calls lib::run()
│   ├── lib.rs                    — Tauri builder, plugin registration, command exports
│   ├── mapping.rs                — _SCALE table + midi_pitch_to_key()
│   ├── injector.rs               — Injector trait + EnigoInjector + whitelist + shift handling
│   ├── midi.rs                   — parse_midi() via midly -> NoteSchedule
│   ├── playback.rs               — PlaybackEngine (Arc<Mutex>, JoinHandle::abort, DEFAULT_SPEED 0.95)
│   ├── config.rs                 — typed wrapper over tauri-plugin-store
│   ├── platform.rs               — Windows timeBeginPeriod(1) + is_playback_supported()
│   ├── commands.rs               — 13 #[tauri::command]s + TauriSink event emitter
│   └── hotkeys.rs                — register DELETE/HOME/END/INSERT
├── capabilities/default.json     — Tauri v2 capability whitelist
└── tauri.conf.json               — window config (decorations: false, transparent: false)

legacy/                           — Python implementation (reference-only, lihat di bawah)
```

**Domain truths** (port verbatim dari Python — jangan re-derive):

| Konsep | Tauri | Python source |
|---|---|---|
| `_SCALE` mapping | `src-tauri/src/mapping.rs` | `legacy/src/midi_parser.py:7` |
| `_ALLOWED` whitelist | `src-tauri/src/injector.rs` | `legacy/src/keyboard_sim.py:3-8` |
| `CONVERSION_CASES` shift map | `src-tauri/src/injector.rs::shifted_to_base` | `legacy/src/constants.py:12-15` |
| Hotkey magnitude (10 notes) | `src-tauri/src/playback.rs::SEEK_STEP` | `legacy/playSong_clean.py:28,40` |
| Config schema | `src-tauri/src/config.rs` | `legacy/src/config.py` |

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- FILE FORMAT -->
## File Format

File `.mid` / `.midi` standar didukung. Program otomatis mengonversi not MIDI ke mapping piano 61-tombol (C2–C7).

**Key scale** (61 tombol):
```
1!2@34$5%6^78*9(0qQwWeErtTyYuiIoOpPasSdDfgGhHjJklLzZxcCvVbBnm
```

Note di luar range C2–C7 di-fold ke oktaf terdekat. Multi-channel MIDI di-flatten (semua track digabung).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- BUILD -->
## Build

### Production build (recommended)

```bash
cd src-tauri
cargo tauri build
```

Output:
```
src-tauri/target/release/playsong.exe                              ~5.36 MB
src-tauri/target/release/bundle/msi/playSong_0.2.0_x64_en-US.msi   ~2.62 MB
src-tauri/target/release/bundle/nsis/playSong_0.2.0_x64-setup.exe  ~1.82 MB
```

### Tests

```bash
cd src-tauri && cargo test         # 17 unit tests (mapping/injector/midi/playback)
cd app && npm run typecheck        # TS strict-mode check
```

### Toolchain notes

- `cargo` biasanya di `C:\Users\<user>\.cargo\bin\` — prepend ke PATH kalau perlu
- `npm` di `C:\Program Files\nodejs\` — pakai `& "C:\Program Files\nodejs\npm.cmd"` di PowerShell untuk bypass execution-policy

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LEGACY -->
## Legacy Python build

Implementasi Python original disimpan di [`legacy/`](legacy/) untuk referensi dan verifikasi parity. **Tidak di-maintain aktif** — bug fix dan fitur baru hanya masuk ke build Tauri.

### Run legacy

```bash
cd legacy
pip install keyboard mido
# Wajib Administrator
python playSong_clean.py
```

### Build legacy .exe

PyInstaller (~11 MB):
```bash
cd legacy
%USERPROFILE%\.local\bin\pyinstaller.exe playSong_clean.spec --noconfirm
# Output: legacy/dist/playSong_clean.exe
```

Nuitka (~8.5 MB, butuh Python 3.12):
```bash
cd legacy
uv python install 3.12
uv tool install nuitka --python 3.12 --with keyboard --with mido --with zstandard --force
%USERPROFILE%\AppData\Roaming\uv\tools\nuitka\Scripts\python.exe -m nuitka ^
  --standalone --onefile --windows-console-mode=disable ^
  --enable-plugin=tk-inter --include-module=keyboard --include-package=mido ^
  --mingw64 --lto=yes --assume-yes-for-downloads ^
  --output-filename=playSong_clean.exe --output-dir=dist_nuitka playSong_clean.py
```

### Legacy tests

```bash
cd legacy
PYTHONIOENCODING=utf-8 python tests/test_playSong.py
```

### Why was Python archived?

- Butuh Administrator (driver-style hook via `keyboard` library)
- ~10–15ms timer jitter dari `threading.Timer`
- Bundle size 11 MB+ (vs 5.36 MB Tauri exe)
- Tidak punya custom title bar / modern shadcn UI

Tauri rewrite mengatasi semua di atas tanpa kompromi pada feature parity.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

**v0.1**
- [x] Tauri v2 + Vite + React 19 + TypeScript stack
- [x] Verbatim port domain truths dari Python (mapping, whitelist, shift, seek)
- [x] Custom title bar tanpa Windows chrome
- [x] Hotkey global (DELETE/HOME/END/INSERT)
- [x] Multi-folder picker, search, speed slider, theme/palette/lang toggle
- [x] Player popup dengan note log, Pilih Lagu Lain, Keluar
- [x] Default speed 0.95× untuk parity feel dengan Python build
- [x] Persistent config via tauri-plugin-store
- [x] Bundle ≤ 8 MB (achieved 5.36 MB exe)

**v0.2 (current)**
- [x] In-app rewind/skip/restart buttons di PlayerSheet (untuk keyboard 65%)
- [ ] Tempo change mid-song (saat ini hanya read initial tempo)
- [ ] CI: GH Actions Windows runner (cargo test + clippy + tauri build)
- [ ] Integration test untuk command→sink→event chain

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

[Tauri-badge]: https://img.shields.io/badge/Tauri-v2-FFC131?style=for-the-badge&logo=tauri&logoColor=black
[Tauri-url]: https://tauri.app/
[Rust-badge]: https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white
[Rust-url]: https://www.rust-lang.org/
[React-badge]: https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black
[React-url]: https://react.dev/
[TypeScript-badge]: https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white
[TypeScript-url]: https://www.typescriptlang.org/
[Vite-badge]: https://img.shields.io/badge/Vite-6-646CFF?style=for-the-badge&logo=vite&logoColor=white
[Vite-url]: https://vitejs.dev/
[Tailwind-badge]: https://img.shields.io/badge/Tailwind-v4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white
[Tailwind-url]: https://tailwindcss.com/
