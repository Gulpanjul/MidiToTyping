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
    Convert MIDI files into automated keyboard-press simulation for piano games.
    <br />
    <br />
    <a href="https://github.com/Gulpanjul/MidiToTyping/issues/new?labels=bug">Report Bug</a>
    &middot;
    <a href="https://github.com/Gulpanjul/MidiToTyping/issues/new?labels=enhancement">Request Feature</a>
  </p>
</div>



> **Tauri rewrite (v0.2.x) is the current build.** Vite + React 19 +
> TypeScript frontend with a Rust backend. Drops the Administrator
> requirement, ~5 MB exe, custom title bar, no UAC. The old Python
> implementation moved to [`legacy/`](legacy/) for reference.

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
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

**playSong** converts MIDI files into automated keyboard-press simulation — a fit for keyboard-based piano games like **Sky: Children of the Light** and **Piano Tiles**. The user picks a MIDI file via the GUI, then the app presses keyboard keys automatically per the MIDI timing.

Key features:
* Multi-folder picker with real-time filtering
* Playback speed slider 0.25× – 3.00× with a difficulty label (Beginner → Master)
* Global hotkeys: Play/Pause (DELETE), Rewind (HOME), Skip (END), Restart (INSERT)
* Custom title bar without the standard Windows chrome
* Scrolling note log in the player popup
* Two themes (dark/light), two color palettes (**Zinc** & **Slate**), two languages (ID/EN)
* **No Administrator required** — uses standard Win32 APIs (`SetWindowsHookEx`, `SendInput`)
* Small bundle: ~5.36 MB exe / ~2.62 MB MSI / ~1.82 MB NSIS

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

* Windows 10/11 (Linux/macOS will compile but playback is disabled — Windows-only)
* [Node.js 20+](https://nodejs.org/)
* [Rust toolchain](https://www.rust-lang.org/tools/install)
* (Optional) [Tauri CLI](https://tauri.app/start/prerequisites/) for dev/build

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

Or download the MSI/NSIS installer from [Releases](https://github.com/Gulpanjul/MidiToTyping/releases).

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE -->
## Usage

1. Open the app → the window opens with no UAC prompt
2. Click **➕** to add a folder of `.mid` / `.midi` files (1-level / non-recursive scan — add subfolders separately if needed)
3. Pick a song, set the speed with the slider (difficulty label updates in real time)
4. Click **▶ Play This File** → the player popup opens in the **paused** state
5. Alt-tab to the target game window and focus it
6. Press **DELETE** to start playback (or click the Play button in the popup)

### Hotkey Playback (global)

| Key | Function |
|--------|--------|
| `DELETE` | Play / Pause toggle |
| `HOME` | Rewind — back 10 notes |
| `END` | Skip — forward 10 notes (or reset if near the end) |
| `INSERT` | Restart from the beginning |

### Known Limitations

1. **The game window must have focus** — `SendInput` does not target a specific HWND
2. **Games with DirectInput/Raw Input** may bypass it — certain modern games (Unreal/Unity) don't accept synthetic input
3. **MIDI multi-channel flatten** — all tracks are merged; notes outside the 61-key range are folded to the nearest octave
4. **65% keyboards (no nav cluster)** — HOME/END/INSERT are physically absent; the user must use an Fn-layer or remap. Note: in-app rewind/skip/restart buttons were added in v0.2.
5. **Default speed 0.95×** — compensation because Rust `tokio::sleep` is more precise than Python's `threading.Timer`. Users upgrading from the Python build feel the same tempo at 0.95× Tauri vs 1.0× Python.

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
│       ├── PlayerSheet.tsx       — Dialog with progress + Play/Pause + Pick Another Song + Exit + note log
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

legacy/                           — Python implementation (reference-only, see below)
```

**Domain truths** (verbatim port from Python — do not re-derive):

| Concept | Tauri | Python source |
|---|---|---|
| `_SCALE` mapping | `src-tauri/src/mapping.rs` | `legacy/src/midi_parser.py:7` |
| `_ALLOWED` whitelist | `src-tauri/src/injector.rs` | `legacy/src/keyboard_sim.py:3-8` |
| `CONVERSION_CASES` shift map | `src-tauri/src/injector.rs::shifted_to_base` | `legacy/src/constants.py:12-15` |
| Hotkey magnitude (10 notes) | `src-tauri/src/playback.rs::SEEK_STEP` | `legacy/playSong_clean.py:28,40` |
| Config schema | `src-tauri/src/config.rs` | `legacy/src/config.py` |

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- FILE FORMAT -->
## File Format

Standard `.mid` / `.midi` files are supported. The program automatically converts MIDI notes to the 61-key piano mapping (C2–C7).

**Key scale** (61 keys):
```
1!2@34$5%6^78*9(0qQwWeErtTyYuiIoOpPasSdDfgGhHjJklLzZxcCvVbBnm
```

Notes outside the C2–C7 range are folded to the nearest octave. Multi-channel MIDI is flattened (all tracks merged).

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

- `cargo` is usually in `C:\Users\<user>\.cargo\bin\` — prepend it to PATH if needed
- `npm` is in `C:\Program Files\nodejs\` — use `& "C:\Program Files\nodejs\npm.cmd"` in PowerShell to bypass the execution policy

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LEGACY -->
## Legacy Python build

The original Python implementation is kept in [`legacy/`](legacy/) for reference and parity verification. **Not actively maintained** — bug fixes and new features go only into the Tauri build.

### Run legacy

```bash
cd legacy
pip install keyboard mido
# Requires Administrator
python playSong_clean.py
```

### Build legacy .exe

PyInstaller (~11 MB):
```bash
cd legacy
%USERPROFILE%\.local\bin\pyinstaller.exe playSong_clean.spec --noconfirm
# Output: legacy/dist/playSong_clean.exe
```

Nuitka (~8.5 MB, requires Python 3.12):
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

- Requires Administrator (driver-style hook via the `keyboard` library)
- ~10–15ms timer jitter from `threading.Timer`
- Bundle size 11 MB+ (vs 5.36 MB Tauri exe)
- No custom title bar / modern shadcn UI

The Tauri rewrite solves all of the above without compromising feature parity.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
## Roadmap

**v0.1**
- [x] Tauri v2 + Vite + React 19 + TypeScript stack
- [x] Verbatim port of domain truths from Python (mapping, whitelist, shift, seek)
- [x] Custom title bar without Windows chrome
- [x] Hotkey global (DELETE/HOME/END/INSERT)
- [x] Multi-folder picker, search, speed slider, theme/palette/lang toggle
- [x] Player popup with note log, Pick Another Song, Exit
- [x] Default speed 0.95× for parity feel with the Python build
- [x] Persistent config via tauri-plugin-store
- [x] Bundle ≤ 8 MB (achieved 5.36 MB exe)

**v0.2 (current)**
- [x] In-app rewind/skip/restart buttons in PlayerSheet (for 65% keyboards)
- [ ] Mid-song tempo change (currently only reads the initial tempo)
- [ ] CI: GH Actions Windows runner (cargo test + clippy + tauri build)
- [ ] Integration test for the command→sink→event chain

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTRIBUTING -->
## Contributing

An LSH internal project. Contributions from team members are very welcome — every improvement makes this build better. Bug fixes & new features go **only** into the Tauri build (`app/` + `src-tauri/`); `legacy/` is a reference archive.

1. Create a feature branch (`git checkout -b feat/AmazingFeature`)
2. Pass the quality gates before committing: `cargo test`, `npm run typecheck`, `npm run build`
3. Commit your changes (`git commit -m 'feat: Add AmazingFeature'`)
4. Push the branch (`git push origin feat/AmazingFeature`) and open a Pull Request

Read [SYSTEM_MAP.md](SYSTEM_MAP.md) as the architecture compass before you start.

### Top contributors

<a href="https://github.com/Gulpanjul/MidiToTyping/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=Gulpanjul/MidiToTyping" alt="contrib.rocks image" />
</a>

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Internal project. Not for external distribution without permission.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Gulpanjul — [gulpa.andhikac@gmail.com](mailto:gulpa.andhikac@gmail.com)

Project Link: [https://github.com/Gulpanjul/MidiToTyping](https://github.com/Gulpanjul/MidiToTyping)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Resources & libraries that made this project possible:

* [Best-README-Template](https://github.com/othneildrew/Best-README-Template) — this README's template
* [Tauri](https://tauri.app/)
* [midly](https://crates.io/crates/midly) — zero-copy MIDI parser
* [enigo](https://crates.io/crates/enigo) — synthetic keyboard injection
* [tokio](https://tokio.rs/) — async runtime playback engine
* [Lucide Icons](https://lucide.dev/)
* [Tailwind CSS](https://tailwindcss.com/)
* [Shields.io](https://shields.io/)

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
