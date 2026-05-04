# playSong Tauri Rewrite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the existing Python/Tkinter Windows app **playSong** into a Tauri v2 desktop app with a Vite + React 19 + TypeScript frontend and a Rust backend, preserving feature parity, dropping the admin requirement, and shrinking the bundle from ~11 MB to ~3–5 MB.

**Architecture:** Rust backend owns all OS-touching logic (MIDI parsing via `midly`, synthetic key injection via `enigo`, global hotkeys via `tauri-plugin-global-shortcut`, persistent config via `tauri-plugin-store`, Windows timer resolution via `windows-rs`). React frontend is a thin UI: it talks to Rust through typed `invoke` commands and listens to engine events. Cross-platform shell compiles on macOS/Linux but only Windows registers hotkeys / runs the injector at v1.

**Tech Stack:** Tauri 2.1, tauri-build 2.0, Vite 6, React 19, TypeScript 5.7, Tailwind v4 (CSS-first config), shadcn/ui (Vite preset, copy-pasted into `app/src/components/ui`), midly 0.5, enigo 0.3, tokio 1, tauri-plugin-{dialog,fs,store,global-shortcut,os,shell} 2.0, windows-rs 0.58 (Windows-only crate).

**Reference:** Design doc at `C:\Users\andhika.gulpa\.claude\plans\let-s-try-c-quizzical-newell.md`. Source-of-truth for verbatim ports lives in `src/midi_parser.py`, `src/keyboard_sim.py`, `src/playback.py`, `src/constants.py`, `src/strings.py`, `src/themes.py`, `src/config.py`, `playSong_clean.py`.

---

## File Structure

**Frontend (`app/`)** — created in Task 1:
- `app/index.html`, `app/vite.config.ts`, `app/tsconfig.json`, `app/tsconfig.node.json`, `app/package.json`
- `app/src/main.tsx` — React entry, mounts `<App/>` to `#root`
- `app/src/App.tsx` — root layout, providers (config, theme, playback)
- `app/src/styles/globals.css` — Tailwind v4 directives + `@theme` CSS-variable block (4 palette/theme combos)
- `app/src/types.ts` — `NoteSchedule`, `NoteEvent`, `Config`, `PlaybackState`, `Lang`, `Theme`, `Palette`
- `app/src/lib/tauri.ts` — typed `invoke`/`listen` wrappers; one function per command/event
- `app/src/lib/platform.ts` — `isPlaybackSupported()` helper (calls Rust `is_playback_supported`)
- `app/src/i18n/strings.ts` — direct port of `src/strings.py` STRINGS dict (28 keys × 2 langs)
- `app/src/theme/themes.ts` — direct port of `src/themes.py` (4 palette/theme combos × 11 color keys)
- `app/src/contexts/ConfigContext.tsx`, `ThemeContext.tsx`, `PlaybackContext.tsx` — providers
- `app/src/hooks/useConfig.ts`, `useTheme.ts`, `usePlayback.ts` — hooks consumers use
- `app/src/components/ui/*` — shadcn primitives (Button, Slider, Dialog, Input, Table, Tabs)
- `app/src/components/Header.tsx`, `FolderPane.tsx`, `MusicPane.tsx`, `BottomBar.tsx`, `PlayerSheet.tsx`, `InfoPopup.tsx`, `SplashScreen.tsx`, `UnsupportedBanner.tsx`

**Backend (`src-tauri/`)** — created in Task 2:
- `src-tauri/Cargo.toml`, `src-tauri/build.rs`, `src-tauri/tauri.conf.json`
- `src-tauri/capabilities/default.json` — perms for fs/dialog/store/global-shortcut/shell
- `src-tauri/icons/*` (placeholder PNG/ICO copied from existing repo)
- `src-tauri/src/main.rs` — thin (`fn main() { playsong_lib::run() }`)
- `src-tauri/src/lib.rs` — Tauri builder, plugin registration, command exports
- `src-tauri/src/mapping.rs` — `_SCALE` table + `midi_pitch_to_key()` with octave wrap
- `src-tauri/src/injector.rs` — `Injector` trait + `EnigoInjector` impl + whitelist + shift map
- `src-tauri/src/midi.rs` — `parse_midi()` via `midly` → `NoteSchedule`
- `src-tauri/src/playback.rs` — `PlaybackEngine` (Arc<Mutex<State>>, tokio task, abort handle)
- `src-tauri/src/hotkeys.rs` — register/unregister 4 global shortcuts via `tauri-plugin-global-shortcut`
- `src-tauri/src/config.rs` — typed wrapper over `tauri-plugin-store`
- `src-tauri/src/platform.rs` — Windows `timeBeginPeriod`/`timeEndPeriod` + `is_playback_supported()`
- `src-tauri/src/commands.rs` — Tauri commands (`#[tauri::command]` exports)
- `src-tauri/tests/fixtures/` — copy 1 small `.mid` file from repo for parser tests

**Repo-root modifications:**
- `.gitignore` — add `app/node_modules/`, `app/dist/`, `src-tauri/target/`
- `README.md` — add Tauri build/run section (Python section preserved during transition)
- `CLAUDE.md` — add a "Tauri rewrite" section describing the new tree

The existing Python tree (`src/`, `playSong_clean.py`, `tests/`) is **not modified** by this plan; it's archived in a follow-up commit only after feature parity is verified.

---

## Task Order Rationale

We build domain truths first (mapping, injector, midi), then the engine that uses them, then the Tauri command surface, then the UI on top. Each task ends with a green test (where one applies) and a commit. We avoid touching the OS until late — the injector is unit-tested behind a trait so most tests don't actually press keys.

---

### Task 1: Scaffold the frontend

**Goal:** A minimal Vite + React 19 + TS + Tailwind v4 app that builds, type-checks, and renders "Hello playSong" — no Tauri yet.

**Files:**
- Create: `app/package.json`
- Create: `app/vite.config.ts`
- Create: `app/tsconfig.json`
- Create: `app/tsconfig.node.json`
- Create: `app/index.html`
- Create: `app/src/main.tsx`
- Create: `app/src/App.tsx`
- Create: `app/src/styles/globals.css`
- Create: `app/src/vite-env.d.ts`
- Modify: `.gitignore`

- [ ] **Step 1: Create `app/package.json`**

```json
{
  "name": "playsong-app",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "typecheck": "tsc --noEmit",
    "tauri": "tauri"
  },
  "dependencies": {
    "react": "19.0.0",
    "react-dom": "19.0.0"
  },
  "devDependencies": {
    "@tauri-apps/cli": "2.1.0",
    "@types/react": "19.0.0",
    "@types/react-dom": "19.0.0",
    "@vitejs/plugin-react": "4.3.4",
    "@tailwindcss/vite": "4.0.0",
    "tailwindcss": "4.0.0",
    "typescript": "5.7.3",
    "vite": "6.0.7"
  }
}
```

- [ ] **Step 2: Create `app/vite.config.ts`**

```ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'node:path';

const host = process.env.TAURI_DEV_HOST;

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') },
  },
  clearScreen: false,
  server: {
    port: 1420,
    strictPort: true,
    host: host || false,
    hmr: host ? { protocol: 'ws', host, port: 1421 } : undefined,
    watch: { ignored: ['**/src-tauri/**'] },
  },
});
```

- [ ] **Step 3: Create `app/tsconfig.json`**

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": false,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": { "@/*": ["src/*"] }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 4: Create `app/tsconfig.node.json`**

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "noEmit": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 5: Create `app/index.html`**

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>playSong</title>
  </head>
  <body class="bg-[var(--bg)] text-[var(--text)]">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 6: Create `app/src/main.tsx`**

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/globals.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

- [ ] **Step 7: Create `app/src/App.tsx`**

```tsx
export default function App() {
  return (
    <main className="min-h-screen p-8 font-sans">
      <h1 className="text-2xl font-semibold">playSong</h1>
      <p className="text-sm opacity-70">Tauri rewrite scaffold.</p>
    </main>
  );
}
```

- [ ] **Step 8: Create `app/src/styles/globals.css`**

```css
@import "tailwindcss";

@theme {
  --color-bg: #09090B;
  --color-panel: #18181B;
  --color-accent: #FAFAFA;
  --color-text: #FAFAFA;
  --color-subtext: #71717A;
  --color-border: #27272A;
  --color-row-alt: #111113;
  --color-sel-bg: #3F3F46;
  --color-entry-bg: #27272A;
  --color-btn-hov: #27272A;
  --color-accent-hov: #D4D4D8;
}

:root {
  --bg: var(--color-bg);
  --panel: var(--color-panel);
  --accent: var(--color-accent);
  --text: var(--color-text);
  --subtext: var(--color-subtext);
  --border: var(--color-border);
  --row-alt: var(--color-row-alt);
  --sel-bg: var(--color-sel-bg);
  --entry-bg: var(--color-entry-bg);
  --btn-hov: var(--color-btn-hov);
  --accent-hov: var(--color-accent-hov);
}

html, body, #root { height: 100%; }
body { margin: 0; }
```

- [ ] **Step 9: Create `app/src/vite-env.d.ts`**

```ts
/// <reference types="vite/client" />
```

- [ ] **Step 10: Add to `.gitignore`**

Append (do not overwrite):

```
app/node_modules/
app/dist/
src-tauri/target/
```

- [ ] **Step 11: Install and verify build**

Run from `d:\Projects\MidiToTyping`:
```bash
cd app && npm install && npm run typecheck && npm run build
```
Expected: typecheck passes; `app/dist/` produced; bundle <100 KB.

- [ ] **Step 12: Commit**

```bash
git add app/ .gitignore
git commit -m "feat(tauri): scaffold Vite + React 19 + TS + Tailwind v4 frontend"
```

---

### Task 2: Scaffold the Tauri Rust backend

**Goal:** A working Tauri v2 backend that opens a window pointing at the Vite dev server, with all needed plugins registered.

**Files:**
- Create: `src-tauri/Cargo.toml`
- Create: `src-tauri/build.rs`
- Create: `src-tauri/tauri.conf.json`
- Create: `src-tauri/capabilities/default.json`
- Create: `src-tauri/src/main.rs`
- Create: `src-tauri/src/lib.rs`
- Create: `src-tauri/icons/icon.png` (placeholder — copy from any existing PNG; required by Tauri)
- Create: `src-tauri/icons/icon.ico` (placeholder)
- Modify: `app/package.json` (add devDep `@tauri-apps/api`)

- [ ] **Step 1: Create `src-tauri/Cargo.toml`**

```toml
[package]
name = "playsong"
version = "0.1.0"
edition = "2021"
description = "MIDI-to-typing auto-player (Tauri v2)"
authors = ["Gulpanjul"]
license = "MIT"

[lib]
name = "playsong_lib"
crate-type = ["staticlib", "cdylib", "rlib"]

[build-dependencies]
tauri-build = { version = "2.0", features = [] }

[dependencies]
tauri = { version = "2.1", features = [] }
tauri-plugin-dialog = "2.0"
tauri-plugin-fs = "2.0"
tauri-plugin-store = "2.0"
tauri-plugin-global-shortcut = "2.0"
tauri-plugin-os = "2.0"
tauri-plugin-shell = "2.0"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
tokio = { version = "1", features = ["rt-multi-thread", "macros", "sync", "time"] }
midly = "0.5"
enigo = "0.3"
thiserror = "2"
anyhow = "1"

[target.'cfg(windows)'.dependencies]
windows = { version = "0.58", features = ["Win32_Media"] }

[profile.release]
panic = "abort"
codegen-units = 1
lto = true
opt-level = "s"
strip = true
```

- [ ] **Step 2: Create `src-tauri/build.rs`**

```rust
fn main() {
    tauri_build::build();
}
```

- [ ] **Step 3: Create `src-tauri/tauri.conf.json`**

```json
{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "playSong",
  "version": "0.1.0",
  "identifier": "com.gulpanjul.playsong",
  "build": {
    "beforeDevCommand": "npm --prefix ../app run dev",
    "beforeBuildCommand": "npm --prefix ../app run build",
    "devUrl": "http://localhost:1420",
    "frontendDist": "../app/dist"
  },
  "app": {
    "windows": [
      {
        "title": "playSong",
        "width": 1100,
        "height": 720,
        "minWidth": 900,
        "minHeight": 600,
        "resizable": true,
        "fullscreen": false
      }
    ],
    "security": {
      "csp": null
    }
  },
  "bundle": {
    "active": true,
    "targets": ["msi", "nsis"],
    "icon": ["icons/icon.png", "icons/icon.ico"]
  }
}
```

- [ ] **Step 4: Create `src-tauri/capabilities/default.json`**

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Default capabilities for the playSong main window",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "dialog:allow-open",
    "fs:allow-read-dir",
    "fs:allow-read-file",
    "fs:scope-app-recursive",
    "store:default",
    "global-shortcut:allow-register",
    "global-shortcut:allow-unregister",
    "global-shortcut:allow-unregister-all",
    "global-shortcut:allow-is-registered",
    "os:allow-platform",
    "shell:allow-open"
  ]
}
```

- [ ] **Step 5: Create `src-tauri/src/main.rs`**

```rust
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    playsong_lib::run();
}
```

- [ ] **Step 6: Create `src-tauri/src/lib.rs`**

```rust
#[tauri::command]
fn ping() -> &'static str {
    "pong"
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_store::Builder::new().build())
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .plugin(tauri_plugin_os::init())
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![ping])
        .run(tauri::generate_context!())
        .expect("error while running playSong");
}
```

- [ ] **Step 7: Copy placeholder icons**

```bash
# from repo root
mkdir -p src-tauri/icons
# Use any existing PNG/ICO. If no ICO exists, generate from the PNG with `magick`,
# or download Tauri's default icon temporarily — placeholders are fine for dev.
cp dist/playSong_clean.exe src-tauri/icons/.placeholder 2>/dev/null || true
```

If no ICO is available, run `npx @tauri-apps/cli icon path/to/any-square.png` from `src-tauri/` later — for now create empty files so Tauri's path check passes:
```bash
touch src-tauri/icons/icon.png src-tauri/icons/icon.ico
```
(Replace with real icons before release; not blocking dev.)

- [ ] **Step 8: Add `@tauri-apps/api` to `app/package.json` dependencies**

In `app/package.json`, under `"dependencies"`:
```json
"@tauri-apps/api": "2.1.0"
```
Then run `cd app && npm install`.

- [ ] **Step 9: Verify Tauri build (debug)**

Run from `d:\Projects\MidiToTyping`:
```bash
cd src-tauri && cargo check
```
Expected: compiles with no errors. Warnings about unused plugins are fine.

- [ ] **Step 10: Commit**

```bash
git add src-tauri/ app/package.json app/package-lock.json
git commit -m "feat(tauri): scaffold Tauri v2 backend with plugins registered"
```

---

### Task 3: Port domain truths — MIDI scale mapping

**Goal:** A pure Rust function `midi_pitch_to_key(pitch: u8) -> char` that exactly mirrors the Python `_SCALE` lookup with octave-wrap, plus `is_release_marker` and `_ALLOWED_KEYS` for parser sanity checks.

**Files:**
- Create: `src-tauri/src/mapping.rs`
- Modify: `src-tauri/src/lib.rs` (add `mod mapping;`)
- Test: inline `#[cfg(test)] mod tests` in `mapping.rs`

- [ ] **Step 1: Write the failing test**

Create `src-tauri/src/mapping.rs`:

```rust
//! MIDI pitch → typing-key mapping. Verbatim port of src/midi_parser.py:7
//! and the wrap rule on lines 33-34.

pub const SCALE: &str = "1!2@34$5%6^78*9(0qQwWeErtTyYuiIoOpPasSdDfgGhHjJklLzZxcCvVbBnm";

pub fn midi_pitch_to_key(pitch: u8) -> char {
    let scale: Vec<char> = SCALE.chars().collect();
    let len = scale.len() as i32;
    let mut idx = pitch as i32 - 36;
    while idx >= len { idx -= 12; }
    while idx < 0   { idx += 12; }
    scale[idx as usize]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn pitch_36_is_first_scale_char() {
        // C2 (MIDI 36) → idx 0 → '1'
        assert_eq!(midi_pitch_to_key(36), '1');
    }

    #[test]
    fn pitch_above_range_wraps_down() {
        // MIDI 96 (C7) → idx 60 → wraps down by 12 until in range.
        // SCALE has 61 chars; 60 is in range; 96 → idx 60 → 'm' (last char)
        let scale: Vec<char> = SCALE.chars().collect();
        assert_eq!(scale.len(), 61);
        assert_eq!(midi_pitch_to_key(96), scale[60]);
    }

    #[test]
    fn pitch_below_range_wraps_up() {
        // MIDI 24 → idx -12 → +12 → 0 → '1'
        assert_eq!(midi_pitch_to_key(24), '1');
    }

    #[test]
    fn pitch_far_above_wraps_repeatedly() {
        // MIDI 120 → idx 84 → -12 → 72 → -12 → 60 → in range
        let scale: Vec<char> = SCALE.chars().collect();
        assert_eq!(midi_pitch_to_key(120), scale[60]);
    }
}
```

- [ ] **Step 2: Add `mod mapping;` to `src-tauri/src/lib.rs`**

Insert at the top of `lib.rs`, before the `ping` command:
```rust
mod mapping;
```

- [ ] **Step 3: Run tests to verify they pass**

```bash
cd src-tauri && cargo test mapping
```
Expected: 4 passed.

- [ ] **Step 4: Commit**

```bash
git add src-tauri/src/mapping.rs src-tauri/src/lib.rs
git commit -m "feat(rust): port MIDI scale mapping with octave wrap"
```

---

### Task 4: Port domain truths — keyboard injector trait + whitelist

**Goal:** An `Injector` trait abstracting key press/release, plus the verbatim `_ALLOWED` whitelist, `CONVERSION_CASES` shift map, and `is_shifted` predicate. The real `EnigoInjector` impl is added in Task 5; this task uses a `MockInjector` for unit tests.

**Files:**
- Create: `src-tauri/src/injector.rs`
- Modify: `src-tauri/src/lib.rs` (add `mod injector;`)

- [ ] **Step 1: Write the failing tests**

Create `src-tauri/src/injector.rs`:

```rust
//! Keyboard injection abstraction. Whitelist + shift map ported verbatim
//! from src/keyboard_sim.py and src/constants.py CONVERSION_CASES.

use std::sync::Mutex;

/// Verbatim from src/keyboard_sim.py:3-8
pub const ALLOWED: &str = concat!(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "0123456789",
    "!@#$%^&*()_+{}|:\"<>?",
    "`~-=[]\\;',./ "
);

pub fn is_allowed(c: char) -> bool {
    ALLOWED.contains(c)
}

/// Verbatim from src/keyboard_sim.py:11-15
pub fn is_shifted(c: char) -> bool {
    let v = c as u32;
    if (65..=90).contains(&v) { return true; }
    "!@#$%^&*()_+{}|:\"<>?".contains(c)
}

/// Verbatim from src/constants.py:12-15. Maps shifted-symbol → its base key.
pub fn shifted_to_base(c: char) -> Option<char> {
    Some(match c {
        '!' => '1', '@' => '2', '#' => '3', '£' => '3',
        '$' => '4', '%' => '5', '^' => '6', '&' => '7',
        '*' => '8', '(' => '9', ')' => '0',
        _ => return None,
    })
}

pub trait Injector: Send + Sync {
    fn press(&self, key: char);
    fn release(&self, key: char);
}

/// Records every press/release call. Used in tests so we never actually
/// inject keys into the OS.
#[derive(Default)]
pub struct MockInjector {
    pub events: Mutex<Vec<String>>,
}

impl Injector for MockInjector {
    fn press(&self, key: char) {
        if !is_allowed(key) { return; }
        self.events.lock().unwrap().push(format!("press {}", key));
    }
    fn release(&self, key: char) {
        if !is_allowed(key) { return; }
        self.events.lock().unwrap().push(format!("release {}", key));
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn allowed_includes_letters_and_punctuation() {
        assert!(is_allowed('a'));
        assert!(is_allowed('Z'));
        assert!(is_allowed('!'));
        assert!(is_allowed(' '));
        assert!(!is_allowed('é'));
        assert!(!is_allowed('\n'));
    }

    #[test]
    fn shift_predicate_matches_python() {
        assert!(is_shifted('A'));
        assert!(is_shifted('Z'));
        assert!(is_shifted('!'));
        assert!(is_shifted(')'));
        assert!(!is_shifted('a'));
        assert!(!is_shifted('1'));
        assert!(!is_shifted('-'));
    }

    #[test]
    fn shifted_to_base_covers_eleven_entries() {
        let pairs = [
            ('!', '1'), ('@', '2'), ('#', '3'), ('£', '3'),
            ('$', '4'), ('%', '5'), ('^', '6'), ('&', '7'),
            ('*', '8'), ('(', '9'), (')', '0'),
        ];
        for (sym, base) in pairs {
            assert_eq!(shifted_to_base(sym), Some(base));
        }
        assert_eq!(shifted_to_base('A'), None);
    }

    #[test]
    fn mock_injector_drops_disallowed_chars() {
        let m = MockInjector::default();
        m.press('a');
        m.press('é');
        m.release('a');
        let events = m.events.lock().unwrap();
        assert_eq!(*events, vec!["press a", "release a"]);
    }
}
```

- [ ] **Step 2: Add `mod injector;` to `src-tauri/src/lib.rs`**

```rust
mod mapping;
mod injector;
```

- [ ] **Step 3: Run tests to verify they pass**

```bash
cd src-tauri && cargo test injector
```
Expected: 4 passed.

- [ ] **Step 4: Commit**

```bash
git add src-tauri/src/injector.rs src-tauri/src/lib.rs
git commit -m "feat(rust): port injector trait + whitelist + shift map"
```

---

### Task 5: Implement `EnigoInjector` (real key-press impl)

**Goal:** A production `Injector` that uses `enigo` to actually press keys via Win32 `SendInput`. Mirror the Python `press_letter` / `release_letter` exactly: for shifted chars, hold left-shift around the base-key press.

**Files:**
- Modify: `src-tauri/src/injector.rs`

- [ ] **Step 1: Append `EnigoInjector` to `src-tauri/src/injector.rs`**

Add at the bottom of the file (above `#[cfg(test)]`):

```rust
use enigo::{Direction, Enigo, Key, Keyboard, Settings};
use std::sync::Mutex as StdMutex;

pub struct EnigoInjector {
    inner: StdMutex<Enigo>,
}

impl EnigoInjector {
    pub fn new() -> Result<Self, String> {
        let enigo = Enigo::new(&Settings::default())
            .map_err(|e| format!("enigo init failed: {e}"))?;
        Ok(Self { inner: StdMutex::new(enigo) })
    }

    fn key_for(c: char) -> Key {
        Key::Unicode(c)
    }
}

impl Injector for EnigoInjector {
    fn press(&self, key: char) {
        if !is_allowed(key) { return; }
        let mut enigo = self.inner.lock().unwrap();
        if is_shifted(key) {
            let base = shifted_to_base(key).unwrap_or_else(|| key.to_ascii_lowercase());
            // Mirror Python: release base, hold shift, press base, release shift
            let _ = enigo.key(Self::key_for(base), Direction::Release);
            let _ = enigo.key(Key::LShift, Direction::Press);
            let _ = enigo.key(Self::key_for(base), Direction::Press);
            let _ = enigo.key(Key::LShift, Direction::Release);
        } else {
            let _ = enigo.key(Self::key_for(key), Direction::Release);
            let _ = enigo.key(Self::key_for(key), Direction::Press);
        }
    }

    fn release(&self, key: char) {
        if !is_allowed(key) { return; }
        let mut enigo = self.inner.lock().unwrap();
        if is_shifted(key) {
            let base = shifted_to_base(key).unwrap_or_else(|| key.to_ascii_lowercase());
            let _ = enigo.key(Self::key_for(base), Direction::Release);
        } else {
            let _ = enigo.key(Self::key_for(key), Direction::Release);
        }
    }
}
```

- [ ] **Step 2: Verify it still compiles**

```bash
cd src-tauri && cargo check
```
Expected: compiles. (No new tests — this exercises the OS, which we don't unit-test.)

- [ ] **Step 3: Commit**

```bash
git add src-tauri/src/injector.rs
git commit -m "feat(rust): implement EnigoInjector with shift-key handling"
```

---

### Task 6: MIDI parser — `midly`-based `parse_midi`

**Goal:** A function `parse_midi(path) -> Result<NoteSchedule>` that reads a `.mid` file and produces the same data the Python `parse_song_file` produces, but in a typed struct (no temp `.txt` round-trip).

**Files:**
- Create: `src-tauri/src/midi.rs`
- Create: `src-tauri/tests/fixtures/sample.mid` (copy any small `.mid` from existing repo)
- Modify: `src-tauri/src/lib.rs` (add `mod midi;`)

- [ ] **Step 1: Copy a fixture MIDI**

```bash
# From repo root — find any small .mid file the repo already ships
find . -name "*.mid" -not -path "./node_modules/*" -not -path "./src-tauri/target/*" | head -1
```
Pick the first hit and copy it:
```bash
mkdir -p src-tauri/tests/fixtures
cp <path-to-any-small-mid> src-tauri/tests/fixtures/sample.mid
```
If no `.mid` exists in the repo, ask the user for one before continuing.

- [ ] **Step 2: Write the failing tests AND implementation**

Create `src-tauri/src/midi.rs`:

```rust
//! MIDI parsing via `midly`. Output mirrors src/midi_parser.py +
//! src/playback.py:parse_info — events carry per-note delays in seconds
//! at 1.0× speed, ready for the playback engine to scale by speed.

use crate::mapping::midi_pitch_to_key;
use midly::{MetaMessage, MidiMessage, Smf, Timing, TrackEventKind};
use serde::Serialize;
use std::path::Path;

#[derive(Debug, Serialize, Clone)]
pub struct NoteEvent {
    /// Seconds to wait *after* this event before firing the next.
    pub delay_secs: f64,
    /// Concatenated keystrokes. Prefix '~' = release; otherwise press all chars.
    pub keys: String,
}

#[derive(Debug, Serialize, Clone)]
pub struct NoteSchedule {
    pub initial_tempo_bpm: f64,
    pub events: Vec<NoteEvent>,
}

#[derive(Debug, thiserror::Error)]
pub enum MidiError {
    #[error("io: {0}")]
    Io(#[from] std::io::Error),
    #[error("parse: {0}")]
    Parse(String),
}

pub fn parse_midi(path: &Path) -> Result<NoteSchedule, MidiError> {
    let bytes = std::fs::read(path)?;
    let smf = Smf::parse(&bytes).map_err(|e| MidiError::Parse(e.to_string()))?;

    let ticks_per_beat = match smf.header.timing {
        Timing::Metrical(tpb) => u32::from(u16::from(tpb)) as f64,
        Timing::Timecode(_, _) => {
            return Err(MidiError::Parse("SMPTE timing not supported".into()));
        }
    };

    // Merge tracks by absolute tick (mirrors mido.merge_tracks).
    #[derive(Debug)]
    struct Ev {
        abs_tick: u64,
        kind: EvKind,
    }
    #[derive(Debug)]
    enum EvKind {
        Note { release: bool, key: char },
        Tempo { bpm: f64 },
    }

    let mut merged: Vec<Ev> = Vec::new();
    for track in &smf.tracks {
        let mut abs_tick: u64 = 0;
        for ev in track {
            abs_tick += u32::from(ev.delta) as u64;
            match ev.kind {
                TrackEventKind::Meta(MetaMessage::Tempo(us_per_beat)) => {
                    let bpm = 60_000_000.0 / u32::from(us_per_beat) as f64;
                    merged.push(Ev { abs_tick, kind: EvKind::Tempo { bpm } });
                }
                TrackEventKind::Midi { message: MidiMessage::NoteOn { key, vel }, .. } => {
                    let release = u8::from(vel) == 0;
                    let ch = midi_pitch_to_key(u8::from(key));
                    merged.push(Ev { abs_tick, kind: EvKind::Note { release, key: ch } });
                }
                TrackEventKind::Midi { message: MidiMessage::NoteOff { key, .. }, .. } => {
                    let ch = midi_pitch_to_key(u8::from(key));
                    merged.push(Ev { abs_tick, kind: EvKind::Note { release: true, key: ch } });
                }
                _ => {}
            }
        }
    }
    merged.sort_by_key(|e| e.abs_tick);

    // Convert merged events → (tick, keys) rows like the Python text format,
    // then run the parse_info delay-conversion (replicating src/playback.py:parse_info).
    let mut initial_tempo_bpm = 120.0_f64;
    let mut tempo_bpm = initial_tempo_bpm;
    let mut tempo_seen = false;

    // Build a flat list of (abs_tick, keys-string-or-tempo-marker)
    enum Row { Tempo(f64), Notes(u64, String) }
    let mut rows: Vec<Row> = Vec::new();
    let mut first_note_tick: Option<u64> = None;

    // Group simultaneous notes (same abs_tick) into one keys string.
    let mut i = 0;
    while i < merged.len() {
        let t = merged[i].abs_tick;
        let mut group_press = String::new();
        let mut group_release = String::new();
        let mut tempo_at_t: Option<f64> = None;
        while i < merged.len() && merged[i].abs_tick == t {
            match merged[i].kind {
                EvKind::Tempo { bpm } => tempo_at_t = Some(bpm),
                EvKind::Note { release, key } => {
                    if first_note_tick.is_none() { first_note_tick = Some(t); }
                    if release { group_release.push(key); } else { group_press.push(key); }
                }
            }
            i += 1;
        }
        if let Some(bpm) = tempo_at_t {
            if !tempo_seen {
                initial_tempo_bpm = bpm;
                tempo_seen = true;
            }
            rows.push(Row::Tempo(bpm));
        }
        if !group_press.is_empty() {
            rows.push(Row::Notes(t, group_press));
        }
        if !group_release.is_empty() {
            rows.push(Row::Notes(t, format!("~{group_release}")));
        }
    }

    // Replicate src/playback.py:parse_info — convert absolute ticks to
    // per-event delays in SECONDS at 1.0× speed.
    // Note delays: (next_tick - this_tick) / ticks_per_beat * (60 / bpm)
    let _ = first_note_tick; // tick anchor handled implicitly by deltas
    let mut events: Vec<NoteEvent> = Vec::new();
    let mut current_bpm = initial_tempo_bpm;
    let mut last_note: Option<usize> = None; // index into events of last note row
    let mut last_tick: Option<u64> = None;

    for row in rows {
        match row {
            Row::Tempo(bpm) => { current_bpm = bpm; }
            Row::Notes(tick, keys) => {
                if let (Some(prev_tick), Some(prev_idx)) = (last_tick, last_note) {
                    let beat_delta = (tick - prev_tick) as f64 / ticks_per_beat;
                    let secs = beat_delta * 60.0 / current_bpm;
                    events[prev_idx].delay_secs = secs;
                }
                events.push(NoteEvent { delay_secs: 1.0, keys });
                last_note = Some(events.len() - 1);
                last_tick = Some(tick);
            }
        }
    }
    // Last event keeps default 1.0s tail (mirrors Python's note[0] = 1.0 fallback).

    Ok(NoteSchedule { initial_tempo_bpm, events })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    fn fixture() -> PathBuf {
        PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("tests").join("fixtures").join("sample.mid")
    }

    #[test]
    fn parses_fixture_into_nonempty_schedule() {
        let s = parse_midi(&fixture()).expect("fixture parses");
        assert!(!s.events.is_empty(), "expected at least one note event");
        assert!(s.initial_tempo_bpm > 0.0);
    }

    #[test]
    fn every_event_has_nonneg_delay() {
        let s = parse_midi(&fixture()).expect("fixture parses");
        for ev in &s.events {
            assert!(ev.delay_secs >= 0.0, "negative delay: {}", ev.delay_secs);
        }
    }

    #[test]
    fn release_events_carry_tilde_prefix() {
        let s = parse_midi(&fixture()).expect("fixture parses");
        let has_release = s.events.iter().any(|e| e.keys.starts_with('~'));
        assert!(has_release, "expected at least one release event");
    }
}
```

- [ ] **Step 3: Add `mod midi;` to `src-tauri/src/lib.rs`**

```rust
mod mapping;
mod injector;
mod midi;
```

- [ ] **Step 4: Run tests**

```bash
cd src-tauri && cargo test midi
```
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add src-tauri/src/midi.rs src-tauri/src/lib.rs src-tauri/tests/fixtures/sample.mid
git commit -m "feat(rust): MIDI parser with midly producing NoteSchedule"
```

---

### Task 7: Playback engine — state, control, scheduler

**Goal:** A `PlaybackEngine` that owns the schedule + index + speed, can be started/paused/seeked/restarted from any thread, and runs a single tokio task that fires events through an `Arc<dyn Injector>` while emitting state events to the frontend.

**Files:**
- Create: `src-tauri/src/playback.rs`
- Modify: `src-tauri/src/lib.rs` (add `mod playback;`)

- [ ] **Step 1: Write the failing tests AND implementation**

Create `src-tauri/src/playback.rs`:

```rust
//! Playback engine — owns the schedule + index + speed and drives a single
//! tokio task. Mirrors src/playback.py semantics:
//!   - per-note delay scaled by speed: delay/speed
//!   - rewind = max(0, idx - 10)
//!   - skip   = idx + 10, but if idx + 10 >= total then reset to 0 + pause
//!   - restart = idx = 0, is_playing = true
//!   - generation token = JoinHandle::abort() on transition

use crate::injector::Injector;
use crate::midi::{NoteEvent, NoteSchedule};
use serde::Serialize;
use std::sync::Arc;
use tokio::sync::Mutex;
use tokio::task::JoinHandle;
use tokio::time::{sleep, Duration, Instant};

pub const SEEK_STEP: i64 = 10;

#[derive(Debug, Clone, Default, Serialize)]
pub struct PlaybackState {
    pub is_playing: bool,
    pub index: usize,
    pub total: usize,
    pub speed: f64,
    pub song_path: Option<String>,
}

pub trait StateSink: Send + Sync {
    fn emit_state(&self, s: &PlaybackState);
    fn emit_done(&self);
    fn emit_tick(&self, index: usize, key: &str);
}

/// No-op sink for tests.
pub struct NullSink;
impl StateSink for NullSink {
    fn emit_state(&self, _s: &PlaybackState) {}
    fn emit_done(&self) {}
    fn emit_tick(&self, _i: usize, _k: &str) {}
}

pub struct PlaybackEngine {
    state: Arc<Mutex<PlaybackState>>,
    schedule: Arc<Mutex<Option<NoteSchedule>>>,
    handle: Arc<Mutex<Option<JoinHandle<()>>>>,
    injector: Arc<dyn Injector>,
    sink: Arc<dyn StateSink>,
}

impl PlaybackEngine {
    pub fn new(injector: Arc<dyn Injector>, sink: Arc<dyn StateSink>) -> Self {
        let state = PlaybackState { speed: 1.0, ..Default::default() };
        Self {
            state: Arc::new(Mutex::new(state)),
            schedule: Arc::new(Mutex::new(None)),
            handle: Arc::new(Mutex::new(None)),
            injector,
            sink,
        }
    }

    pub async fn load(&self, schedule: NoteSchedule, song_path: Option<String>) {
        self.abort_running().await;
        *self.schedule.lock().await = Some(schedule.clone());
        let mut s = self.state.lock().await;
        s.is_playing = false;
        s.index = 0;
        s.total = schedule.events.len();
        s.song_path = song_path;
        self.sink.emit_state(&s);
    }

    pub async fn set_speed(&self, speed: f64) {
        let speed = speed.clamp(0.25, 3.0);
        let mut s = self.state.lock().await;
        s.speed = speed;
        self.sink.emit_state(&s);
    }

    pub async fn snapshot(&self) -> PlaybackState {
        self.state.lock().await.clone()
    }

    pub async fn play(&self) {
        let already = self.state.lock().await.is_playing;
        if already { return; }
        {
            let mut s = self.state.lock().await;
            s.is_playing = true;
            self.sink.emit_state(&s);
        }
        self.spawn_task().await;
    }

    pub async fn pause(&self) {
        self.abort_running().await;
        let mut s = self.state.lock().await;
        s.is_playing = false;
        self.sink.emit_state(&s);
    }

    pub async fn toggle(&self) -> bool {
        let now = self.state.lock().await.is_playing;
        if now { self.pause().await; false } else { self.play().await; true }
    }

    pub async fn seek(&self, delta: i64) -> usize {
        self.abort_running().await;
        let total = self.state.lock().await.total as i64;
        let mut s = self.state.lock().await;
        let was_playing = s.is_playing;
        let new_idx = s.index as i64 + delta;
        if delta > 0 && new_idx >= total {
            // Skip past end: reset + pause (mirrors playSong_clean.py:on_end_press)
            s.index = 0;
            s.is_playing = false;
            self.sink.emit_state(&s);
            return 0;
        }
        s.index = new_idx.max(0) as usize;
        self.sink.emit_state(&s);
        drop(s);
        if was_playing { self.spawn_task().await; }
        self.state.lock().await.index
    }

    pub async fn restart(&self) {
        self.abort_running().await;
        {
            let mut s = self.state.lock().await;
            s.index = 0;
            s.is_playing = true;
            self.sink.emit_state(&s);
        }
        self.spawn_task().await;
    }

    async fn abort_running(&self) {
        if let Some(h) = self.handle.lock().await.take() {
            h.abort();
        }
    }

    async fn spawn_task(&self) {
        let state = self.state.clone();
        let schedule = self.schedule.clone();
        let injector = self.injector.clone();
        let sink = self.sink.clone();
        let handle_slot = self.handle.clone();

        let h = tokio::spawn(async move {
            loop {
                let (idx, total, speed) = {
                    let s = state.lock().await;
                    if !s.is_playing { return; }
                    (s.index, s.total, s.speed)
                };
                if idx >= total {
                    let mut s = state.lock().await;
                    s.is_playing = false;
                    s.index = 0;
                    sink.emit_state(&s);
                    sink.emit_done();
                    return;
                }
                let event: NoteEvent = {
                    let sched = schedule.lock().await;
                    sched.as_ref().unwrap().events[idx].clone()
                };

                if event.keys.starts_with('~') {
                    for k in event.keys.chars().skip(1) { injector.release(k); }
                } else {
                    for k in event.keys.chars() { injector.press(k); }
                }
                sink.emit_tick(idx, &event.keys);

                {
                    let mut s = state.lock().await;
                    s.index += 1;
                    sink.emit_state(&s);
                }
                let delay = (event.delay_secs / speed).max(0.0);
                if delay > 0.0 {
                    sleep(Duration::from_secs_f64(delay)).await;
                } else {
                    tokio::task::yield_now().await;
                }
                let _ = Instant::now(); // keep import used
            }
        });

        *handle_slot.lock().await = Some(h);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::injector::MockInjector;
    use crate::midi::NoteEvent;

    fn schedule(keys: &[&str]) -> NoteSchedule {
        NoteSchedule {
            initial_tempo_bpm: 120.0,
            events: keys.iter().map(|k| NoteEvent {
                delay_secs: 0.001, keys: k.to_string(),
            }).collect(),
        }
    }

    fn engine() -> (PlaybackEngine, Arc<MockInjector>) {
        let inj = Arc::new(MockInjector::default());
        let eng = PlaybackEngine::new(inj.clone(), Arc::new(NullSink));
        (eng, inj)
    }

    #[tokio::test]
    async fn play_emits_keys_in_order_then_finishes() {
        let (eng, inj) = engine();
        eng.load(schedule(&["a", "b", "c"]), None).await;
        eng.play().await;
        // wait for completion
        for _ in 0..100 {
            if !eng.snapshot().await.is_playing { break; }
            tokio::time::sleep(Duration::from_millis(10)).await;
        }
        let events = inj.events.lock().unwrap().clone();
        assert_eq!(events, vec!["press a", "press b", "press c"]);
        let s = eng.snapshot().await;
        assert!(!s.is_playing);
        assert_eq!(s.index, 0);
    }

    #[tokio::test]
    async fn release_keys_use_tilde_prefix() {
        let (eng, inj) = engine();
        eng.load(schedule(&["a", "~a"]), None).await;
        eng.play().await;
        for _ in 0..100 {
            if !eng.snapshot().await.is_playing { break; }
            tokio::time::sleep(Duration::from_millis(10)).await;
        }
        let events = inj.events.lock().unwrap().clone();
        assert_eq!(events, vec!["press a", "release a"]);
    }

    #[tokio::test]
    async fn pause_then_play_resumes_at_index() {
        let (eng, _inj) = engine();
        eng.load(schedule(&["a"; 50]), None).await;
        eng.play().await;
        tokio::time::sleep(Duration::from_millis(20)).await;
        eng.pause().await;
        let mid = eng.snapshot().await;
        assert!(!mid.is_playing);
        assert!(mid.index > 0 && mid.index < 50);
    }

    #[tokio::test]
    async fn seek_minus_ten_clamps_at_zero() {
        let (eng, _inj) = engine();
        eng.load(schedule(&["a"; 5]), None).await;
        eng.seek(-SEEK_STEP).await;
        assert_eq!(eng.snapshot().await.index, 0);
    }

    #[tokio::test]
    async fn seek_past_end_resets_and_pauses() {
        let (eng, _inj) = engine();
        eng.load(schedule(&["a"; 5]), None).await;
        eng.play().await;
        tokio::time::sleep(Duration::from_millis(5)).await;
        eng.seek(SEEK_STEP).await; // +10 with total=5
        let s = eng.snapshot().await;
        assert_eq!(s.index, 0);
        assert!(!s.is_playing);
    }

    #[tokio::test]
    async fn restart_sets_index_zero_and_plays() {
        let (eng, inj) = engine();
        eng.load(schedule(&["a", "b"]), None).await;
        eng.play().await;
        tokio::time::sleep(Duration::from_millis(20)).await;
        eng.restart().await;
        for _ in 0..100 {
            if !eng.snapshot().await.is_playing { break; }
            tokio::time::sleep(Duration::from_millis(10)).await;
        }
        let evs = inj.events.lock().unwrap().clone();
        // we can't assert exact length (race-y), but we know at least one
        // "press a" exists and the engine ended at index 0 again.
        assert!(evs.iter().any(|e| e == "press a"));
        assert_eq!(eng.snapshot().await.index, 0);
    }
}
```

- [ ] **Step 2: Add `mod playback;` to `src-tauri/src/lib.rs`**

```rust
mod mapping;
mod injector;
mod midi;
mod playback;
```

- [ ] **Step 3: Run tests**

```bash
cd src-tauri && cargo test playback
```
Expected: 6 passed.

- [ ] **Step 4: Commit**

```bash
git add src-tauri/src/playback.rs src-tauri/src/lib.rs
git commit -m "feat(rust): playback engine with pause/seek/restart and abort-token"
```

---

### Task 8: Config wrapper over `tauri-plugin-store`

**Goal:** A typed `Config` struct with the same JSON schema as `src/config.py`, persisted via `tauri-plugin-store` to `playSong_config.json` in the app data dir.

**Files:**
- Create: `src-tauri/src/config.rs`
- Modify: `src-tauri/src/lib.rs` (add `mod config;`)

- [ ] **Step 1: Create `src-tauri/src/config.rs`**

```rust
//! Persistent config. Schema mirrors src/config.py:32-40.
//! Stored at <app-data>/playSong_config.json via tauri-plugin-store.

use serde::{Deserialize, Serialize};
use tauri::{AppHandle, Manager, Runtime};
use tauri_plugin_store::StoreExt;

const STORE_FILE: &str = "playSong_config.json";

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub lang: String,        // "id" | "en"
    pub theme: String,       // "dark" | "light"
    pub palette: String,     // "celestial" | "grand_piano"
    pub folders: Vec<String>,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            lang: "id".into(),
            theme: "dark".into(),
            palette: "celestial".into(),
            folders: vec![],
        }
    }
}

fn validate(mut c: Config) -> Config {
    if !["id", "en"].contains(&c.lang.as_str()) { c.lang = "id".into(); }
    if !["dark", "light"].contains(&c.theme.as_str()) { c.theme = "dark".into(); }
    if !["celestial", "grand_piano"].contains(&c.palette.as_str()) { c.palette = "celestial".into(); }
    c.folders.retain(|p| !p.is_empty());
    c
}

pub fn load<R: Runtime>(app: &AppHandle<R>) -> Config {
    let Ok(store) = app.store(STORE_FILE) else { return Config::default(); };
    let lang   = store.get("lang").and_then(|v| v.as_str().map(String::from)).unwrap_or_else(|| "id".into());
    let theme  = store.get("theme").and_then(|v| v.as_str().map(String::from)).unwrap_or_else(|| "dark".into());
    let palette= store.get("palette").and_then(|v| v.as_str().map(String::from)).unwrap_or_else(|| "celestial".into());
    let folders= store.get("folders")
        .and_then(|v| v.as_array().cloned())
        .map(|arr| arr.into_iter().filter_map(|x| x.as_str().map(String::from)).collect())
        .unwrap_or_default();
    validate(Config { lang, theme, palette, folders })
}

pub fn save<R: Runtime>(app: &AppHandle<R>, c: &Config) -> Result<(), String> {
    let store = app.store(STORE_FILE).map_err(|e| e.to_string())?;
    let c = validate(c.clone());
    store.set("lang", serde_json::Value::String(c.lang));
    store.set("theme", serde_json::Value::String(c.theme));
    store.set("palette", serde_json::Value::String(c.palette));
    store.set("folders", serde_json::Value::Array(
        c.folders.into_iter().map(serde_json::Value::String).collect()
    ));
    store.save().map_err(|e| e.to_string())
}
```

- [ ] **Step 2: Add `mod config;` to `lib.rs`**

```rust
mod mapping;
mod injector;
mod midi;
mod playback;
mod config;
```

- [ ] **Step 3: Verify it compiles**

```bash
cd src-tauri && cargo check
```
Expected: compiles. (No unit tests — `tauri::AppHandle` is hard to mock; we'll validate config in the smoke test.)

- [ ] **Step 4: Commit**

```bash
git add src-tauri/src/config.rs src-tauri/src/lib.rs
git commit -m "feat(rust): typed config wrapper over tauri-plugin-store"
```

---

### Task 9: Platform module — Windows timer resolution + OS gate

**Goal:** Bump Windows timer resolution to 1ms at startup (and restore on shutdown) for sub-15ms note timing accuracy. On non-Windows, expose `is_playback_supported() = false`.

**Files:**
- Create: `src-tauri/src/platform.rs`
- Modify: `src-tauri/src/lib.rs` (add `mod platform;`, call from `run`)

- [ ] **Step 1: Create `src-tauri/src/platform.rs`**

```rust
//! Platform-specific bits. Currently just Windows timer resolution.

#[cfg(windows)]
pub fn begin_high_resolution_timer() {
    use windows::Win32::Media::timeBeginPeriod;
    unsafe { let _ = timeBeginPeriod(1); }
}

#[cfg(windows)]
pub fn end_high_resolution_timer() {
    use windows::Win32::Media::timeEndPeriod;
    unsafe { let _ = timeEndPeriod(1); }
}

#[cfg(not(windows))]
pub fn begin_high_resolution_timer() {}

#[cfg(not(windows))]
pub fn end_high_resolution_timer() {}

pub fn is_playback_supported() -> bool {
    cfg!(windows)
}
```

- [ ] **Step 2: Wire startup hook in `lib.rs`**

Modify `lib.rs` to call `begin_high_resolution_timer` before building Tauri:

```rust
mod mapping;
mod injector;
mod midi;
mod playback;
mod config;
mod platform;

#[tauri::command]
fn ping() -> &'static str { "pong" }

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    platform::begin_high_resolution_timer();
    let result = tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_store::Builder::new().build())
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .plugin(tauri_plugin_os::init())
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![ping])
        .run(tauri::generate_context!());
    platform::end_high_resolution_timer();
    result.expect("error while running playSong");
}
```

- [ ] **Step 3: Verify it compiles**

```bash
cd src-tauri && cargo check
```
Expected: compiles on Windows; on macOS/Linux the cfg-not-windows variant is used.

- [ ] **Step 4: Commit**

```bash
git add src-tauri/src/platform.rs src-tauri/src/lib.rs
git commit -m "feat(rust): Windows 1ms timer resolution + OS gate helper"
```

---

### Task 10: Tauri commands surface

**Goal:** Wire all commands the frontend will call. Backed by a single `AppState` holding the `PlaybackEngine` and the Tauri `AppHandle`-emitting `StateSink`.

**Files:**
- Create: `src-tauri/src/commands.rs`
- Modify: `src-tauri/src/lib.rs`

- [ ] **Step 1: Create `src-tauri/src/commands.rs`**

```rust
use crate::config::{self, Config};
use crate::injector::EnigoInjector;
use crate::midi::{self, NoteSchedule};
use crate::platform;
use crate::playback::{PlaybackEngine, PlaybackState, StateSink};
use serde::Serialize;
use std::path::{Path, PathBuf};
use std::sync::Arc;
use tauri::{AppHandle, Emitter, Manager, Runtime, State};

pub struct TauriSink<R: Runtime> { handle: AppHandle<R> }
impl<R: Runtime> StateSink for TauriSink<R> {
    fn emit_state(&self, s: &PlaybackState) { let _ = self.handle.emit("playback:state", s); }
    fn emit_done(&self) { let _ = self.handle.emit("playback:done", ()); }
    fn emit_tick(&self, index: usize, key: &str) {
        let _ = self.handle.emit("playback:tick", serde_json::json!({"index": index, "key": key}));
    }
}

pub struct AppState { pub engine: PlaybackEngine }

impl AppState {
    pub fn new<R: Runtime>(handle: AppHandle<R>) -> Result<Self, String> {
        let inj = Arc::new(EnigoInjector::new()?);
        let sink = Arc::new(TauriSink { handle });
        Ok(Self { engine: PlaybackEngine::new(inj, sink) })
    }
}

#[derive(Serialize)]
pub struct MidiFile { pub name: String, pub size: u64, pub path: String }

#[tauri::command]
pub fn list_midis_in_folder(path: String) -> Result<Vec<MidiFile>, String> {
    let p = Path::new(&path);
    let rd = std::fs::read_dir(p).map_err(|e| e.to_string())?;
    let mut out = Vec::new();
    for entry in rd.flatten() {
        let name = entry.file_name().to_string_lossy().to_string();
        let lower = name.to_lowercase();
        if !(lower.ends_with(".mid") || lower.ends_with(".midi")) { continue; }
        let meta = entry.metadata().map_err(|e| e.to_string())?;
        out.push(MidiFile {
            name,
            size: meta.len(),
            path: entry.path().to_string_lossy().to_string(),
        });
    }
    out.sort_by(|a, b| a.name.to_lowercase().cmp(&b.name.to_lowercase()));
    Ok(out)
}

#[tauri::command]
pub fn parse_midi(path: String) -> Result<NoteSchedule, String> {
    midi::parse_midi(&PathBuf::from(path)).map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn load_song(state: State<'_, AppState>, path: String) -> Result<PlaybackState, String> {
    let sched = midi::parse_midi(&PathBuf::from(&path)).map_err(|e| e.to_string())?;
    state.engine.load(sched, Some(path)).await;
    Ok(state.engine.snapshot().await)
}

#[tauri::command]
pub async fn play(state: State<'_, AppState>) -> Result<(), ()> { state.engine.play().await; Ok(()) }
#[tauri::command]
pub async fn pause(state: State<'_, AppState>) -> Result<(), ()> { state.engine.pause().await; Ok(()) }
#[tauri::command]
pub async fn toggle(state: State<'_, AppState>) -> Result<bool, ()> { Ok(state.engine.toggle().await) }
#[tauri::command]
pub async fn seek(state: State<'_, AppState>, delta: i64) -> Result<usize, ()> { Ok(state.engine.seek(delta).await) }
#[tauri::command]
pub async fn restart(state: State<'_, AppState>) -> Result<(), ()> { state.engine.restart().await; Ok(()) }
#[tauri::command]
pub async fn set_speed(state: State<'_, AppState>, speed: f64) -> Result<(), ()> { state.engine.set_speed(speed).await; Ok(()) }
#[tauri::command]
pub async fn get_state(state: State<'_, AppState>) -> Result<PlaybackState, ()> { Ok(state.engine.snapshot().await) }

#[tauri::command]
pub fn get_config<R: Runtime>(app: AppHandle<R>) -> Config { config::load(&app) }
#[tauri::command]
pub fn set_config<R: Runtime>(app: AppHandle<R>, cfg: Config) -> Result<(), String> { config::save(&app, &cfg) }

#[tauri::command]
pub fn is_playback_supported() -> bool { platform::is_playback_supported() }
```

- [ ] **Step 2: Wire commands + AppState in `lib.rs`**

Replace `lib.rs` body:

```rust
mod mapping;
mod injector;
mod midi;
mod playback;
mod config;
mod platform;
mod commands;
mod hotkeys;

use commands::AppState;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    platform::begin_high_resolution_timer();
    let result = tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .plugin(tauri_plugin_store::Builder::new().build())
        .plugin(tauri_plugin_global_shortcut::Builder::new().build())
        .plugin(tauri_plugin_os::init())
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let handle = app.handle().clone();
            let state = AppState::new(handle.clone())?;
            app.manage(state);
            #[cfg(windows)]
            hotkeys::register(&handle)?;
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::list_midis_in_folder,
            commands::parse_midi,
            commands::load_song,
            commands::play,
            commands::pause,
            commands::toggle,
            commands::seek,
            commands::restart,
            commands::set_speed,
            commands::get_state,
            commands::get_config,
            commands::set_config,
            commands::is_playback_supported,
        ])
        .run(tauri::generate_context!());
    platform::end_high_resolution_timer();
    result.expect("error while running playSong");
}
```

(Note: `mod hotkeys;` references Task 11; `cargo check` will fail until Task 11 lands. We commit Task 10 + Task 11 together.)

---

### Task 11: Global hotkeys (Windows-only)

**Goal:** Register DELETE / HOME / END / INSERT globally. On press, drive the engine via `block_on` on a dedicated runtime, and emit `hotkey:fired` events so the UI can flash an indicator.

**Files:**
- Create: `src-tauri/src/hotkeys.rs`

- [ ] **Step 1: Create `src-tauri/src/hotkeys.rs`**

```rust
//! Global hotkeys (Windows-only at v1). Mirrors playSong_clean.py:15-50.

use crate::commands::AppState;
use tauri::{AppHandle, Emitter, Manager, Runtime};
use tauri_plugin_global_shortcut::{Code, GlobalShortcutExt, Shortcut, ShortcutState};

pub fn register<R: Runtime>(app: &AppHandle<R>) -> Result<(), Box<dyn std::error::Error>> {
    let gs = app.global_shortcut();

    let app_for_handler = app.clone();
    gs.on_shortcut(Shortcut::new(None, Code::Delete), move |_app, _sc, ev| {
        if ev.state() != ShortcutState::Pressed { return; }
        let h = app_for_handler.clone();
        tauri::async_runtime::spawn(async move {
            let state: tauri::State<AppState> = h.state();
            let now = state.engine.toggle().await;
            let _ = h.emit("hotkey:fired",
                serde_json::json!({"which": "play_pause", "is_playing": now}));
        });
    })?;

    let app_for_handler = app.clone();
    gs.on_shortcut(Shortcut::new(None, Code::Home), move |_a, _s, ev| {
        if ev.state() != ShortcutState::Pressed { return; }
        let h = app_for_handler.clone();
        tauri::async_runtime::spawn(async move {
            let state: tauri::State<AppState> = h.state();
            let _ = state.engine.seek(-(crate::playback::SEEK_STEP)).await;
            let _ = h.emit("hotkey:fired", serde_json::json!({"which": "rewind"}));
        });
    })?;

    let app_for_handler = app.clone();
    gs.on_shortcut(Shortcut::new(None, Code::End), move |_a, _s, ev| {
        if ev.state() != ShortcutState::Pressed { return; }
        let h = app_for_handler.clone();
        tauri::async_runtime::spawn(async move {
            let state: tauri::State<AppState> = h.state();
            let _ = state.engine.seek(crate::playback::SEEK_STEP).await;
            let _ = h.emit("hotkey:fired", serde_json::json!({"which": "skip"}));
        });
    })?;

    let app_for_handler = app.clone();
    gs.on_shortcut(Shortcut::new(None, Code::Insert), move |_a, _s, ev| {
        if ev.state() != ShortcutState::Pressed { return; }
        let h = app_for_handler.clone();
        tauri::async_runtime::spawn(async move {
            let state: tauri::State<AppState> = h.state();
            state.engine.restart().await;
            let _ = h.emit("hotkey:fired", serde_json::json!({"which": "restart"}));
        });
    })?;

    Ok(())
}
```

- [ ] **Step 2: Verify everything compiles**

```bash
cd src-tauri && cargo check && cargo test
```
Expected: compiles; all unit tests still pass (mapping × 4, injector × 4, midi × 3, playback × 6 = 17).

- [ ] **Step 3: Commit Tasks 10 + 11 together**

```bash
git add src-tauri/src/commands.rs src-tauri/src/hotkeys.rs src-tauri/src/lib.rs
git commit -m "feat(rust): Tauri commands + Windows global hotkeys"
```

---

### Task 12: Frontend — types + Tauri-bridge wrappers

**Goal:** TypeScript mirrors of the Rust types and a single `lib/tauri.ts` that gives the rest of the app typed `invoke` / `listen` calls.

**Files:**
- Create: `app/src/types.ts`
- Create: `app/src/lib/tauri.ts`

- [ ] **Step 1: Create `app/src/types.ts`**

```ts
export type Lang = 'id' | 'en';
export type Theme = 'dark' | 'light';
export type Palette = 'celestial' | 'grand_piano';

export interface Config {
  lang: Lang;
  theme: Theme;
  palette: Palette;
  folders: string[];
}

export interface NoteEvent {
  delay_secs: number;
  keys: string;
}

export interface NoteSchedule {
  initial_tempo_bpm: number;
  events: NoteEvent[];
}

export interface PlaybackState {
  is_playing: boolean;
  index: number;
  total: number;
  speed: number;
  song_path: string | null;
}

export interface MidiFile {
  name: string;
  size: number;
  path: string;
}

export type HotkeyName = 'play_pause' | 'rewind' | 'skip' | 'restart';
```

- [ ] **Step 2: Create `app/src/lib/tauri.ts`**

```ts
import { invoke } from '@tauri-apps/api/core';
import { listen, type UnlistenFn } from '@tauri-apps/api/event';
import type { Config, MidiFile, NoteSchedule, PlaybackState, HotkeyName } from '../types';

export const api = {
  listMidisInFolder: (path: string) => invoke<MidiFile[]>('list_midis_in_folder', { path }),
  parseMidi:        (path: string) => invoke<NoteSchedule>('parse_midi', { path }),
  loadSong:         (path: string) => invoke<PlaybackState>('load_song', { path }),
  play:             () => invoke<void>('play'),
  pause:            () => invoke<void>('pause'),
  toggle:           () => invoke<boolean>('toggle'),
  seek:             (delta: number) => invoke<number>('seek', { delta }),
  restart:          () => invoke<void>('restart'),
  setSpeed:         (speed: number) => invoke<void>('set_speed', { speed }),
  getState:         () => invoke<PlaybackState>('get_state'),
  getConfig:        () => invoke<Config>('get_config'),
  setConfig:        (cfg: Config) => invoke<void>('set_config', { cfg }),
  isPlaybackSupported: () => invoke<boolean>('is_playback_supported'),
};

export function onPlaybackState(cb: (s: PlaybackState) => void): Promise<UnlistenFn> {
  return listen<PlaybackState>('playback:state', e => cb(e.payload));
}
export function onPlaybackTick(cb: (t: { index: number; key: string }) => void): Promise<UnlistenFn> {
  return listen<{ index: number; key: string }>('playback:tick', e => cb(e.payload));
}
export function onPlaybackDone(cb: () => void): Promise<UnlistenFn> {
  return listen<null>('playback:done', () => cb());
}
export function onHotkey(cb: (which: HotkeyName) => void): Promise<UnlistenFn> {
  return listen<{ which: HotkeyName }>('hotkey:fired', e => cb(e.payload.which));
}
```

- [ ] **Step 3: Verify typecheck**

```bash
cd app && npm run typecheck
```
Expected: passes.

- [ ] **Step 4: Commit**

```bash
git add app/src/types.ts app/src/lib/tauri.ts
git commit -m "feat(frontend): typed Tauri bridge wrappers"
```

---

### Task 13: Frontend — strings (i18n) and themes

**Goal:** Direct ports of `src/strings.py` and `src/themes.py` into TypeScript, plus a CSS-variable-driven theme switcher.

**Files:**
- Create: `app/src/i18n/strings.ts`
- Create: `app/src/theme/themes.ts`
- Modify: `app/src/styles/globals.css`

- [ ] **Step 1: Create `app/src/i18n/strings.ts`**

Port verbatim from `src/strings.py`. Difficulty entries are tuples `(label, color)` — represent as `{ label, color }`.

```ts
import type { Lang } from '../types';

export interface DiffEntry { label: string; color: string }
export interface StringsBundle {
  splash_loading: string; splash_subtitle: string; window_title: string;
  header_title: string; header_subtitle: string; folder_nav_panel: string;
  back_btn: string; add_folder_btn: string; remove_folder_btn: string;
  add_folder_dialog: string; no_folder_selected: string;
  speed_label: string; speed_range: string;
  diff_beginner: DiffEntry; diff_learning: DiffEntry; diff_relaxed: DiffEntry;
  diff_normal: DiffEntry; diff_advanced: DiffEntry; diff_pro: DiffEntry; diff_master: DiffEntry;
  col_no: string; col_title: string; col_size_kb: string;
  file_count_fmt: string; file_count_all: string; status_file: string;
  play_btn: string; cancel_btn: string;
  warn_title: string; warn_msg: string; no_file_msg: string;
  mido_title: string; mido_msg: string;
  palette_celestial: string; palette_grand: string;
  info_btn: string; info_title: string;
  player_title: string; player_play: string; player_pause: string;
  player_pick: string; player_exit: string; player_hotkeys: string;
  player_ready: string; player_stats: string;
}

export const STRINGS: Record<Lang, StringsBundle> = {
  id: {
    splash_loading: 'Memuat aplikasi...',
    splash_subtitle: 'Auto-Player Piano · Sky & Piano Tiles',
    window_title: 'Song Player – Pilih File Lagu',
    header_title: '🎵  Song Auto-Player',
    header_subtitle: 'Pilih folder → pilih lagu → mainkan',
    folder_nav_panel: 'Navigasi Folder',
    back_btn: '← Kembali',
    add_folder_btn: '+ Tambah',
    remove_folder_btn: '− Hapus',
    add_folder_dialog: 'Pilih Folder Lagu',
    no_folder_selected: '  Pilih folder untuk melihat file lagu...',
    speed_label: 'Kecepatan Putar',
    speed_range: '0.25×  ──────  3.00×',
    diff_beginner: { label: 'Pemula', color: '#6BCB77' },
    diff_learning: { label: 'Belajar', color: '#74C0FC' },
    diff_relaxed: { label: 'Santai', color: '#A9C0D6' },
    diff_normal: { label: 'Normal', color: '#CDD6F4' },
    diff_advanced: { label: 'Mahir', color: '#FFA94D' },
    diff_pro: { label: 'Pro', color: '#FF6B6B' },
    diff_master: { label: 'Master', color: '#DA77F2' },
    col_no: 'No', col_title: 'Judul', col_size_kb: 'Ukuran',
    file_count_fmt: '{shown}/{total} file',
    file_count_all: '{total} file',
    status_file: '  {path}  |  {size} bytes  |  {mtime}',
    play_btn: '▶  Mainkan File Ini',
    cancel_btn: 'Batal',
    warn_title: 'Pilih File',
    warn_msg: 'Silakan pilih file dari daftar terlebih dahulu.',
    no_file_msg: 'Tidak ada file yang dipilih. Keluar.',
    mido_title: 'Mido Missing',
    mido_msg: "Library 'mido' tidak ditemukan.\nJalankan: pip install mido",
    palette_celestial: 'Zinc', palette_grand: 'Slate',
    info_btn: 'Info', info_title: 'Tentang Aplikasi',
    player_title: 'Song Player',
    player_play: '▶  Mainkan', player_pause: '⏸  Jeda',
    player_pick: '🎵  Pilih Lagu Lain', player_exit: '✕  Keluar',
    player_hotkeys: 'Hotkey: DEL=Play/Jeda · HOME=−10 · END=+10 · INSERT=Restart',
    player_ready: '[SIAP] {name}',
    player_stats: '  Total nada : {n}   ·   Kecepatan : {s}×',
  },
  en: {
    splash_loading: 'Loading application...',
    splash_subtitle: 'Piano Auto-Player · Sky & Piano Tiles',
    window_title: 'Song Player – Select Song File',
    header_title: '🎵  Song Auto-Player',
    header_subtitle: 'Select folder → choose song → play',
    folder_nav_panel: 'Folder Navigator',
    back_btn: '← Back',
    add_folder_btn: '+ Add',
    remove_folder_btn: '− Remove',
    add_folder_dialog: 'Select Song Folder',
    no_folder_selected: '  Select a folder on the left to view song files...',
    speed_label: 'Playback Speed',
    speed_range: '0.25×  ──────  3.00×',
    diff_beginner: { label: 'Beginner', color: '#6BCB77' },
    diff_learning: { label: 'Learning', color: '#74C0FC' },
    diff_relaxed: { label: 'Relaxed', color: '#A9C0D6' },
    diff_normal: { label: 'Normal', color: '#CDD6F4' },
    diff_advanced: { label: 'Advanced', color: '#FFA94D' },
    diff_pro: { label: 'Pro', color: '#FF6B6B' },
    diff_master: { label: 'Master', color: '#DA77F2' },
    col_no: 'No', col_title: 'Title', col_size_kb: 'Size',
    file_count_fmt: '{shown}/{total} files',
    file_count_all: '{total} files',
    status_file: '  {path}  |  {size} bytes  |  {mtime}',
    play_btn: '▶  Play This File',
    cancel_btn: 'Cancel',
    warn_title: 'Select File',
    warn_msg: 'Please select a file from the list first.',
    no_file_msg: 'No file selected. Exiting.',
    mido_title: 'Mido Missing',
    mido_msg: "Library 'mido' not found.\nRun: pip install mido",
    palette_celestial: 'Zinc', palette_grand: 'Slate',
    info_btn: 'Info', info_title: 'About',
    player_title: 'Song Player',
    player_play: '▶  Play', player_pause: '⏸  Pause',
    player_pick: '🎵  Pick Another Song', player_exit: '✕  Exit',
    player_hotkeys: 'Hotkeys: DEL=Play/Pause · HOME=−10 · END=+10 · INSERT=Restart',
    player_ready: '[READY] {name}',
    player_stats: '  Total notes : {n}   ·   Speed : {s}×',
  },
};

export function fmt(template: string, vars: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (_, k) => String(vars[k] ?? ''));
}
```

- [ ] **Step 2: Create `app/src/theme/themes.ts`**

```ts
import type { Palette, Theme } from '../types';

export interface ColorSet {
  BG: string; PANEL: string; ACCENT: string; ACCENT_HOV: string;
  TEXT: string; SUBTEXT: string; ENTRY_BG: string; BTN_HOV: string;
  ROW_ALT: string; SEL_BG: string; BORDER: string;
}

export const THEMES: Record<Palette, Record<Theme, ColorSet>> = {
  celestial: {
    dark: {
      BG:'#09090B', PANEL:'#18181B', ACCENT:'#FAFAFA', ACCENT_HOV:'#D4D4D8',
      TEXT:'#FAFAFA', SUBTEXT:'#71717A', ENTRY_BG:'#27272A', BTN_HOV:'#27272A',
      ROW_ALT:'#111113', SEL_BG:'#3F3F46', BORDER:'#27272A',
    },
    light: {
      BG:'#FFFFFF', PANEL:'#F4F4F5', ACCENT:'#18181B', ACCENT_HOV:'#3F3F46',
      TEXT:'#09090B', SUBTEXT:'#71717A', ENTRY_BG:'#FFFFFF', BTN_HOV:'#D4D4D8',
      ROW_ALT:'#FAFAFA', SEL_BG:'#E4E4E7', BORDER:'#E4E4E7',
    },
  },
  grand_piano: {
    dark: {
      BG:'#020817', PANEL:'#0F172A', ACCENT:'#818CF8', ACCENT_HOV:'#6366F1',
      TEXT:'#F8FAFC', SUBTEXT:'#64748B', ENTRY_BG:'#1E293B', BTN_HOV:'#1E293B',
      ROW_ALT:'#050E1A', SEL_BG:'#312E81', BORDER:'#1E293B',
    },
    light: {
      BG:'#FFFFFF', PANEL:'#F8FAFC', ACCENT:'#6366F1', ACCENT_HOV:'#4F46E5',
      TEXT:'#0F172A', SUBTEXT:'#64748B', ENTRY_BG:'#FFFFFF', BTN_HOV:'#C7D2FE',
      ROW_ALT:'#F1F5F9', SEL_BG:'#E0E7FF', BORDER:'#E2E8F0',
    },
  },
};

const KEY_TO_VAR: Record<keyof ColorSet, string> = {
  BG:'--bg', PANEL:'--panel', ACCENT:'--accent', ACCENT_HOV:'--accent-hov',
  TEXT:'--text', SUBTEXT:'--subtext', ENTRY_BG:'--entry-bg', BTN_HOV:'--btn-hov',
  ROW_ALT:'--row-alt', SEL_BG:'--sel-bg', BORDER:'--border',
};

export function applyTheme(palette: Palette, theme: Theme) {
  const set = THEMES[palette][theme];
  const root = document.documentElement;
  (Object.keys(set) as (keyof ColorSet)[]).forEach(k => {
    root.style.setProperty(KEY_TO_VAR[k], set[k]);
  });
  root.dataset.theme = theme;
  root.dataset.palette = palette;
}
```

- [ ] **Step 3: Update `app/src/styles/globals.css`**

Replace the file with:

```css
@import "tailwindcss";

:root {
  --bg: #09090B; --panel: #18181B; --accent: #FAFAFA; --accent-hov: #D4D4D8;
  --text: #FAFAFA; --subtext: #71717A; --entry-bg: #27272A; --btn-hov: #27272A;
  --row-alt: #111113; --sel-bg: #3F3F46; --border: #27272A;
}

@theme inline {
  --color-bg: var(--bg);
  --color-panel: var(--panel);
  --color-accent: var(--accent);
  --color-text: var(--text);
  --color-subtext: var(--subtext);
  --color-border: var(--border);
}

html, body, #root { height: 100%; }
body { margin: 0; background: var(--bg); color: var(--text); }
```

- [ ] **Step 4: Verify typecheck + build**

```bash
cd app && npm run typecheck && npm run build
```
Expected: passes.

- [ ] **Step 5: Commit**

```bash
git add app/src/i18n/ app/src/theme/ app/src/styles/globals.css
git commit -m "feat(frontend): port strings + themes with CSS-variable theming"
```

---

### Task 14: Frontend — Config & Theme contexts

**Goal:** A `ConfigProvider` that loads config on mount, persists on change, and exposes `lang` / `theme` / `palette` / `folders` and setters. A `useTheme` hook that calls `applyTheme` whenever theme/palette change.

**Files:**
- Create: `app/src/contexts/ConfigContext.tsx`
- Create: `app/src/hooks/useConfig.ts`
- Create: `app/src/hooks/useTheme.ts`

- [ ] **Step 1: Create `app/src/contexts/ConfigContext.tsx`**

```tsx
import { createContext, useEffect, useState, type ReactNode } from 'react';
import type { Config } from '../types';
import { api } from '../lib/tauri';

const DEFAULT: Config = { lang: 'id', theme: 'dark', palette: 'celestial', folders: [] };

interface Ctx {
  config: Config;
  setConfig: (c: Partial<Config>) => void;
  ready: boolean;
}

export const ConfigContext = createContext<Ctx>({ config: DEFAULT, setConfig: () => {}, ready: false });

export function ConfigProvider({ children }: { children: ReactNode }) {
  const [config, setLocal] = useState<Config>(DEFAULT);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    api.getConfig().then(c => { setLocal(c); setReady(true); }).catch(() => setReady(true));
  }, []);

  function setConfig(patch: Partial<Config>) {
    setLocal(prev => {
      const next = { ...prev, ...patch };
      api.setConfig(next).catch(() => {});
      return next;
    });
  }

  return <ConfigContext.Provider value={{ config, setConfig, ready }}>{children}</ConfigContext.Provider>;
}
```

- [ ] **Step 2: Create `app/src/hooks/useConfig.ts`**

```ts
import { useContext } from 'react';
import { ConfigContext } from '../contexts/ConfigContext';
export function useConfig() { return useContext(ConfigContext); }
```

- [ ] **Step 3: Create `app/src/hooks/useTheme.ts`**

```ts
import { useEffect } from 'react';
import { applyTheme } from '../theme/themes';
import { useConfig } from './useConfig';

export function useTheme() {
  const { config } = useConfig();
  useEffect(() => { applyTheme(config.palette, config.theme); }, [config.palette, config.theme]);
}
```

- [ ] **Step 4: Verify typecheck**

```bash
cd app && npm run typecheck
```
Expected: passes.

- [ ] **Step 5: Commit**

```bash
git add app/src/contexts/ app/src/hooks/
git commit -m "feat(frontend): config context + theme hook"
```

---

### Task 15: Frontend — Playback context + hook

**Goal:** A `PlaybackProvider` that subscribes to backend events on mount and exposes the live `PlaybackState` plus action callbacks.

**Files:**
- Create: `app/src/contexts/PlaybackContext.tsx`
- Create: `app/src/hooks/usePlayback.ts`

- [ ] **Step 1: Create `app/src/contexts/PlaybackContext.tsx`**

```tsx
import { createContext, useEffect, useState, type ReactNode } from 'react';
import type { PlaybackState } from '../types';
import { api, onPlaybackState, onPlaybackDone } from '../lib/tauri';

const DEFAULT: PlaybackState = { is_playing: false, index: 0, total: 0, speed: 1.0, song_path: null };

interface Ctx {
  state: PlaybackState;
  loadSong: (path: string) => Promise<void>;
  play: () => Promise<void>;
  pause: () => Promise<void>;
  toggle: () => Promise<void>;
  seek: (delta: number) => Promise<void>;
  restart: () => Promise<void>;
  setSpeed: (s: number) => Promise<void>;
}

export const PlaybackContext = createContext<Ctx>({
  state: DEFAULT,
  loadSong: async () => {}, play: async () => {}, pause: async () => {},
  toggle: async () => {}, seek: async () => {}, restart: async () => {},
  setSpeed: async () => {},
});

export function PlaybackProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<PlaybackState>(DEFAULT);

  useEffect(() => {
    let unsubState: (() => void) | undefined;
    let unsubDone: (() => void) | undefined;
    (async () => {
      try { setState(await api.getState()); } catch {}
      unsubState = await onPlaybackState(setState);
      unsubDone = await onPlaybackDone(() => {
        setState(prev => ({ ...prev, is_playing: false, index: 0 }));
      });
    })();
    return () => { unsubState?.(); unsubDone?.(); };
  }, []);

  const ctx: Ctx = {
    state,
    loadSong: async (path) => { setState(await api.loadSong(path)); },
    play: () => api.play(),
    pause: () => api.pause(),
    toggle: async () => { await api.toggle(); },
    seek: async (d) => { await api.seek(d); },
    restart: () => api.restart(),
    setSpeed: (s) => api.setSpeed(s),
  };
  return <PlaybackContext.Provider value={ctx}>{children}</PlaybackContext.Provider>;
}
```

- [ ] **Step 2: Create `app/src/hooks/usePlayback.ts`**

```ts
import { useContext } from 'react';
import { PlaybackContext } from '../contexts/PlaybackContext';
export function usePlayback() { return useContext(PlaybackContext); }
```

- [ ] **Step 3: Verify typecheck**

```bash
cd app && npm run typecheck
```
Expected: passes.

- [ ] **Step 4: Commit**

```bash
git add app/src/contexts/PlaybackContext.tsx app/src/hooks/usePlayback.ts
git commit -m "feat(frontend): playback context with engine-event subscription"
```

---

### Task 16: Frontend — minimal shadcn-style UI primitives

**Goal:** Hand-rolled lightweight UI primitives (Button, Slider, Input) styled with CSS variables, so we don't need to bring in `shadcn init` (which assumes Tailwind v3 by default and has a moving target). Visual style matches shadcn.

**Files:**
- Create: `app/src/components/ui/Button.tsx`
- Create: `app/src/components/ui/Slider.tsx`
- Create: `app/src/components/ui/Input.tsx`
- Create: `app/src/components/ui/Dialog.tsx`

- [ ] **Step 1: Create `app/src/components/ui/Button.tsx`**

```tsx
import { type ButtonHTMLAttributes, forwardRef } from 'react';

type Variant = 'primary' | 'secondary' | 'ghost' | 'destructive';
type Size = 'sm' | 'md' | 'lg';

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

const variantClass: Record<Variant, string> = {
  primary:    'bg-[var(--accent)] text-[var(--bg)] hover:bg-[var(--accent-hov)]',
  secondary:  'bg-[var(--panel)] text-[var(--text)] border border-[var(--border)] hover:bg-[var(--btn-hov)]',
  ghost:      'bg-transparent text-[var(--text)] hover:bg-[var(--btn-hov)]',
  destructive:'bg-red-600 text-white hover:bg-red-700',
};
const sizeClass: Record<Size, string> = {
  sm: 'h-8 px-3 text-sm', md: 'h-10 px-4 text-sm', lg: 'h-12 px-6 text-base',
};

export const Button = forwardRef<HTMLButtonElement, Props>(function Button(
  { variant = 'primary', size = 'md', className = '', ...rest }, ref
) {
  return (
    <button
      ref={ref}
      {...rest}
      className={`inline-flex items-center justify-center rounded-md font-medium transition-colors disabled:opacity-50 disabled:pointer-events-none ${variantClass[variant]} ${sizeClass[size]} ${className}`}
    />
  );
});
```

- [ ] **Step 2: Create `app/src/components/ui/Slider.tsx`**

```tsx
import { type ChangeEvent } from 'react';

interface Props {
  value: number; min: number; max: number; step: number;
  onChange: (v: number) => void;
  label?: string;
}

export function Slider({ value, min, max, step, onChange, label }: Props) {
  const handle = (e: ChangeEvent<HTMLInputElement>) => onChange(parseFloat(e.target.value));
  return (
    <div className="flex flex-col gap-1">
      {label && <span className="text-xs text-[var(--subtext)]">{label}</span>}
      <input
        type="range" min={min} max={max} step={step} value={value} onChange={handle}
        className="w-full accent-[var(--accent)]"
      />
    </div>
  );
}
```

- [ ] **Step 3: Create `app/src/components/ui/Input.tsx`**

```tsx
import { type InputHTMLAttributes, forwardRef } from 'react';

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  function Input({ className = '', ...rest }, ref) {
    return (
      <input
        ref={ref}
        {...rest}
        className={`h-9 px-3 rounded-md bg-[var(--entry-bg)] text-[var(--text)] border border-[var(--border)] outline-none focus:ring-2 focus:ring-[var(--accent)]/30 ${className}`}
      />
    );
  }
);
```

- [ ] **Step 4: Create `app/src/components/ui/Dialog.tsx`**

```tsx
import { type ReactNode, useEffect } from 'react';

interface Props {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
}

export function Dialog({ open, onClose, title, children }: Props) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={onClose}>
      <div
        className="bg-[var(--panel)] text-[var(--text)] rounded-lg shadow-xl border border-[var(--border)] min-w-[360px] max-w-[640px] p-6"
        onClick={e => e.stopPropagation()}
      >
        {title && <h2 className="text-lg font-semibold mb-3">{title}</h2>}
        {children}
      </div>
    </div>
  );
}
```

- [ ] **Step 5: Verify typecheck**

```bash
cd app && npm run typecheck
```
Expected: passes.

- [ ] **Step 6: Commit**

```bash
git add app/src/components/ui/
git commit -m "feat(frontend): minimal UI primitives (Button, Slider, Input, Dialog)"
```

---

### Task 17: Frontend — Header component

**Goal:** Top-of-screen header with title/subtitle and three segmented toggles (theme, palette, lang) plus an Info button.

**Files:**
- Create: `app/src/components/Header.tsx`
- Create: `app/src/components/InfoPopup.tsx`

- [ ] **Step 1: Create `app/src/components/Header.tsx`**

```tsx
import { useState } from 'react';
import { useConfig } from '../hooks/useConfig';
import { STRINGS } from '../i18n/strings';
import { Button } from './ui/Button';
import { InfoPopup } from './InfoPopup';

export function Header() {
  const { config, setConfig } = useConfig();
  const S = STRINGS[config.lang];
  const [showInfo, setShowInfo] = useState(false);

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-[var(--border)]">
      <div>
        <h1 className="text-xl font-semibold">{S.header_title}</h1>
        <p className="text-xs text-[var(--subtext)]">{S.header_subtitle}</p>
      </div>
      <div className="flex items-center gap-2">
        <SegToggle
          options={[{ v: 'dark', l: '🌙' }, { v: 'light', l: '☀' }]}
          value={config.theme}
          onChange={v => setConfig({ theme: v as 'dark' | 'light' })}
        />
        <SegToggle
          options={[{ v: 'celestial', l: S.palette_celestial }, { v: 'grand_piano', l: S.palette_grand }]}
          value={config.palette}
          onChange={v => setConfig({ palette: v as 'celestial' | 'grand_piano' })}
        />
        <SegToggle
          options={[{ v: 'id', l: 'ID' }, { v: 'en', l: 'EN' }]}
          value={config.lang}
          onChange={v => setConfig({ lang: v as 'id' | 'en' })}
        />
        <Button variant="ghost" size="sm" onClick={() => setShowInfo(true)}>{S.info_btn}</Button>
      </div>
      <InfoPopup open={showInfo} onClose={() => setShowInfo(false)} />
    </header>
  );
}

function SegToggle({ options, value, onChange }: {
  options: { v: string; l: string }[]; value: string; onChange: (v: string) => void;
}) {
  return (
    <div className="inline-flex rounded-md border border-[var(--border)] bg-[var(--panel)] p-0.5">
      {options.map(o => (
        <button
          key={o.v}
          onClick={() => onChange(o.v)}
          className={`px-3 h-7 text-xs rounded transition-colors ${
            o.v === value
              ? 'bg-[var(--accent)] text-[var(--bg)]'
              : 'text-[var(--subtext)] hover:text-[var(--text)]'
          }`}
        >
          {o.l}
        </button>
      ))}
    </div>
  );
}
```

- [ ] **Step 2: Create `app/src/components/InfoPopup.tsx`**

```tsx
import { Dialog } from './ui/Dialog';
import { useConfig } from '../hooks/useConfig';
import { STRINGS } from '../i18n/strings';

const APP = { version: '0.1.0', date: '2026-04-28', author: 'Gulpanjul', github: 'github.com/Gulpanjul/MidiToTyping' };

export function InfoPopup({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { config } = useConfig();
  const S = STRINGS[config.lang];
  return (
    <Dialog open={open} onClose={onClose} title={S.info_title}>
      <div className="text-sm space-y-2">
        <div><b>playSong</b> v{APP.version} · {APP.date}</div>
        <div className="text-[var(--subtext)]">by {APP.author}</div>
        <div className="text-[var(--subtext)]">{S.player_hotkeys}</div>
        <div className="pt-2">
          <a href={`https://${APP.github}`} target="_blank" rel="noreferrer"
             className="text-[var(--accent)] hover:underline">{APP.github}</a>
        </div>
      </div>
    </Dialog>
  );
}
```

- [ ] **Step 3: Verify typecheck**

```bash
cd app && npm run typecheck
```
Expected: passes.

- [ ] **Step 4: Commit**

```bash
git add app/src/components/Header.tsx app/src/components/InfoPopup.tsx
git commit -m "feat(frontend): Header with segmented toggles + Info popup"
```

---

### Task 18: Frontend — FolderPane (folder list + speed slider)

**Goal:** Left panel with folder list, add/remove buttons, and the playback speed slider.

**Files:**
- Create: `app/src/components/FolderPane.tsx`

- [ ] **Step 1: Create `app/src/components/FolderPane.tsx`**

```tsx
import { useState } from 'react';
import { open as openDialog } from '@tauri-apps/plugin-dialog';
import { Button } from './ui/Button';
import { Slider } from './ui/Slider';
import { useConfig } from '../hooks/useConfig';
import { usePlayback } from '../hooks/usePlayback';
import { STRINGS } from '../i18n/strings';

interface Props {
  selectedFolder: string | null;
  onSelectFolder: (p: string) => void;
}

export function FolderPane({ selectedFolder, onSelectFolder }: Props) {
  const { config, setConfig } = useConfig();
  const { state, setSpeed } = usePlayback();
  const S = STRINGS[config.lang];
  const [busy, setBusy] = useState(false);

  async function handleAdd() {
    if (busy) return;
    setBusy(true);
    try {
      const picked = await openDialog({ directory: true, multiple: false, title: S.add_folder_dialog });
      if (typeof picked === 'string' && !config.folders.includes(picked)) {
        setConfig({ folders: [...config.folders, picked] });
        onSelectFolder(picked);
      }
    } finally { setBusy(false); }
  }

  function handleRemove() {
    if (!selectedFolder) return;
    setConfig({ folders: config.folders.filter(f => f !== selectedFolder) });
    onSelectFolder('');
  }

  return (
    <aside className="w-64 shrink-0 border-r border-[var(--border)] bg-[var(--panel)] flex flex-col">
      <div className="p-3 border-b border-[var(--border)]">
        <div className="text-xs uppercase tracking-wide text-[var(--subtext)] mb-2">{S.folder_nav_panel}</div>
        <div className="flex gap-2">
          <Button size="sm" variant="secondary" onClick={handleAdd} disabled={busy}>{S.add_folder_btn}</Button>
          <Button size="sm" variant="ghost" onClick={handleRemove} disabled={!selectedFolder}>{S.remove_folder_btn}</Button>
        </div>
      </div>
      <ul className="flex-1 overflow-y-auto py-2">
        {config.folders.length === 0 && (
          <li className="px-3 py-4 text-xs text-[var(--subtext)]">{S.no_folder_selected}</li>
        )}
        {config.folders.map(f => (
          <li key={f}>
            <button
              onClick={() => onSelectFolder(f)}
              className={`w-full text-left px-3 py-2 text-sm truncate ${
                f === selectedFolder ? 'bg-[var(--sel-bg)]' : 'hover:bg-[var(--btn-hov)]'
              }`}
              title={f}
            >
              {f.split(/[\\/]/).pop() || f}
            </button>
          </li>
        ))}
      </ul>
      <div className="p-3 border-t border-[var(--border)]">
        <Slider
          label={`${S.speed_label} — ${state.speed.toFixed(2)}×`}
          min={0.25} max={3.0} step={0.05}
          value={state.speed}
          onChange={v => setSpeed(v)}
        />
        <div className="text-[10px] text-[var(--subtext)] text-center mt-1">{S.speed_range}</div>
      </div>
    </aside>
  );
}
```

- [ ] **Step 2: Add `@tauri-apps/plugin-dialog` to `app/package.json`**

In `app/package.json` `dependencies`:
```json
"@tauri-apps/plugin-dialog": "2.0.0",
"@tauri-apps/plugin-fs": "2.0.0",
"@tauri-apps/plugin-store": "2.0.0",
"@tauri-apps/plugin-shell": "2.0.0"
```
Then `cd app && npm install`.

- [ ] **Step 3: Verify typecheck**

```bash
cd app && npm run typecheck
```
Expected: passes.

- [ ] **Step 4: Commit**

```bash
git add app/src/components/FolderPane.tsx app/package.json app/package-lock.json
git commit -m "feat(frontend): FolderPane with add/remove + speed slider"
```

---

### Task 19: Frontend — MusicPane (song list + search)

**Goal:** Right panel with song table, search input (debounced 200ms), and selection state.

**Files:**
- Create: `app/src/components/MusicPane.tsx`

- [ ] **Step 1: Create `app/src/components/MusicPane.tsx`**

```tsx
import { useEffect, useMemo, useState } from 'react';
import { Input } from './ui/Input';
import { useConfig } from '../hooks/useConfig';
import { STRINGS, fmt } from '../i18n/strings';
import { api } from '../lib/tauri';
import type { MidiFile } from '../types';

interface Props {
  folder: string | null;
  selectedFile: MidiFile | null;
  onSelectFile: (f: MidiFile) => void;
}

export function MusicPane({ folder, selectedFile, onSelectFile }: Props) {
  const { config } = useConfig();
  const S = STRINGS[config.lang];
  const [files, setFiles] = useState<MidiFile[]>([]);
  const [query, setQuery] = useState('');
  const [debounced, setDebounced] = useState('');

  useEffect(() => {
    if (!folder) { setFiles([]); return; }
    api.listMidisInFolder(folder).then(setFiles).catch(() => setFiles([]));
  }, [folder]);

  useEffect(() => {
    const t = setTimeout(() => setDebounced(query), 200);
    return () => clearTimeout(t);
  }, [query]);

  const filtered = useMemo(() => {
    if (!debounced) return files;
    const q = debounced.toLowerCase();
    return files.filter(f => f.name.toLowerCase().includes(q));
  }, [files, debounced]);

  const counter = debounced
    ? fmt(S.file_count_fmt, { shown: filtered.length, total: files.length })
    : fmt(S.file_count_all, { total: files.length });

  if (!folder) {
    return <section className="flex-1 flex items-center justify-center text-[var(--subtext)]">{S.no_folder_selected}</section>;
  }

  return (
    <section className="flex-1 flex flex-col">
      <div className="p-3 border-b border-[var(--border)] flex items-center gap-3">
        <Input placeholder="search…" value={query} onChange={e => setQuery(e.target.value)} className="flex-1" />
        <span className="text-xs text-[var(--subtext)]">{counter}</span>
      </div>
      <div className="flex-1 overflow-y-auto">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-[var(--panel)] text-[var(--subtext)] text-xs uppercase">
            <tr>
              <th className="text-left px-3 py-2 w-10">{S.col_no}</th>
              <th className="text-left px-3 py-2">{S.col_title}</th>
              <th className="text-right px-3 py-2 w-24">{S.col_size_kb}</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((f, i) => (
              <tr
                key={f.path}
                onClick={() => onSelectFile(f)}
                onDoubleClick={() => onSelectFile(f)}
                className={`cursor-pointer ${
                  f.path === selectedFile?.path ? 'bg-[var(--sel-bg)]' : i % 2 ? 'bg-[var(--row-alt)]' : ''
                }`}
              >
                <td className="px-3 py-1.5">{i + 1}</td>
                <td className="px-3 py-1.5 truncate" title={f.name}>{f.name}</td>
                <td className="px-3 py-1.5 text-right">{(f.size / 1024).toFixed(1)} KB</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
```

- [ ] **Step 2: Verify typecheck**

```bash
cd app && npm run typecheck
```
Expected: passes.

- [ ] **Step 3: Commit**

```bash
git add app/src/components/MusicPane.tsx
git commit -m "feat(frontend): MusicPane with debounced search + song table"
```

---

### Task 20: Frontend — BottomBar + PlayerSheet

**Goal:** Bottom action bar (Play / Cancel) and the modal player sheet (currently-playing surface with play/pause + stats).

**Files:**
- Create: `app/src/components/BottomBar.tsx`
- Create: `app/src/components/PlayerSheet.tsx`

- [ ] **Step 1: Create `app/src/components/BottomBar.tsx`**

```tsx
import { Button } from './ui/Button';
import { useConfig } from '../hooks/useConfig';
import { STRINGS } from '../i18n/strings';
import type { MidiFile } from '../types';

interface Props {
  selectedFile: MidiFile | null;
  onPlay: () => void;
  onCancel: () => void;
}

export function BottomBar({ selectedFile, onPlay, onCancel }: Props) {
  const { config } = useConfig();
  const S = STRINGS[config.lang];
  return (
    <footer className="px-6 py-3 border-t border-[var(--border)] flex items-center justify-between">
      <span className="text-xs text-[var(--subtext)] truncate">
        {selectedFile?.path ?? ''}
      </span>
      <div className="flex gap-2">
        <Button variant="ghost" onClick={onCancel}>{S.cancel_btn}</Button>
        <Button onClick={onPlay} disabled={!selectedFile}>{S.play_btn}</Button>
      </div>
    </footer>
  );
}
```

- [ ] **Step 2: Create `app/src/components/PlayerSheet.tsx`**

```tsx
import { useEffect } from 'react';
import { Dialog } from './ui/Dialog';
import { Button } from './ui/Button';
import { useConfig } from '../hooks/useConfig';
import { usePlayback } from '../hooks/usePlayback';
import { STRINGS, fmt } from '../i18n/strings';

interface Props { open: boolean; onClose: () => void; songName: string }

export function PlayerSheet({ open, onClose, songName }: Props) {
  const { config } = useConfig();
  const { state, toggle } = usePlayback();
  const S = STRINGS[config.lang];

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === ' ') { e.preventDefault(); toggle(); }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, toggle]);

  return (
    <Dialog open={open} onClose={onClose} title={S.player_title}>
      <div className="space-y-3 text-sm">
        <div className="text-[var(--subtext)]">{fmt(S.player_ready, { name: songName })}</div>
        <div className="text-xs text-[var(--subtext)]">
          {fmt(S.player_stats, { n: String(state.total), s: state.speed.toFixed(2) })}
        </div>
        <div className="text-xs text-[var(--subtext)]">{S.player_hotkeys}</div>
        <div className="h-2 bg-[var(--entry-bg)] rounded overflow-hidden">
          <div className="h-full bg-[var(--accent)] transition-all"
               style={{ width: `${state.total ? (state.index / state.total) * 100 : 0}%` }} />
        </div>
        <div className="flex gap-2 pt-2">
          <Button onClick={() => toggle()} className="flex-1">
            {state.is_playing ? S.player_pause : S.player_play}
          </Button>
          <Button variant="ghost" onClick={onClose}>{S.player_exit}</Button>
        </div>
      </div>
    </Dialog>
  );
}
```

- [ ] **Step 3: Verify typecheck**

```bash
cd app && npm run typecheck
```
Expected: passes.

- [ ] **Step 4: Commit**

```bash
git add app/src/components/BottomBar.tsx app/src/components/PlayerSheet.tsx
git commit -m "feat(frontend): BottomBar + PlayerSheet"
```

---

### Task 21: Frontend — Wire `App.tsx` together

**Goal:** Replace placeholder `App.tsx` with the full layout: Providers → Header → (FolderPane + MusicPane) → BottomBar → PlayerSheet, plus a "Windows-only at v1" banner on non-Windows.

**Files:**
- Modify: `app/src/App.tsx`
- Create: `app/src/components/UnsupportedBanner.tsx`

- [ ] **Step 1: Create `app/src/components/UnsupportedBanner.tsx`**

```tsx
export function UnsupportedBanner() {
  return (
    <div className="bg-yellow-500/15 text-yellow-300 text-xs px-4 py-2 border-b border-yellow-500/30">
      Playback is supported on Windows only in v1. The browser & folder tools still work; Play is disabled.
    </div>
  );
}
```

- [ ] **Step 2: Replace `app/src/App.tsx`**

```tsx
import { useEffect, useState } from 'react';
import { ConfigProvider } from './contexts/ConfigContext';
import { PlaybackProvider } from './contexts/PlaybackContext';
import { useTheme } from './hooks/useTheme';
import { useConfig } from './hooks/useConfig';
import { usePlayback } from './hooks/usePlayback';
import { Header } from './components/Header';
import { FolderPane } from './components/FolderPane';
import { MusicPane } from './components/MusicPane';
import { BottomBar } from './components/BottomBar';
import { PlayerSheet } from './components/PlayerSheet';
import { UnsupportedBanner } from './components/UnsupportedBanner';
import { api } from './lib/tauri';
import type { MidiFile } from './types';

function Shell() {
  useTheme();
  const { config, ready } = useConfig();
  const { loadSong, play } = usePlayback();
  const [folder, setFolder] = useState<string | null>(null);
  const [file, setFile] = useState<MidiFile | null>(null);
  const [showPlayer, setShowPlayer] = useState(false);
  const [supported, setSupported] = useState(true);

  useEffect(() => { api.isPlaybackSupported().then(setSupported); }, []);
  useEffect(() => {
    if (ready && !folder && config.folders[0]) setFolder(config.folders[0]);
  }, [ready, folder, config.folders]);

  async function onPlay() {
    if (!file) return;
    await loadSong(file.path);
    await play();
    setShowPlayer(true);
  }

  return (
    <div className="h-screen flex flex-col bg-[var(--bg)] text-[var(--text)]">
      {!supported && <UnsupportedBanner />}
      <Header />
      <div className="flex-1 flex overflow-hidden">
        <FolderPane selectedFolder={folder} onSelectFolder={p => { setFolder(p || null); setFile(null); }} />
        <MusicPane folder={folder} selectedFile={file} onSelectFile={setFile} />
      </div>
      <BottomBar
        selectedFile={file}
        onPlay={onPlay}
        onCancel={() => { setFile(null); setShowPlayer(false); }}
      />
      <PlayerSheet open={showPlayer} onClose={() => setShowPlayer(false)} songName={file?.name ?? ''} />
    </div>
  );
}

export default function App() {
  return (
    <ConfigProvider>
      <PlaybackProvider>
        <Shell />
      </PlaybackProvider>
    </ConfigProvider>
  );
}
```

- [ ] **Step 3: Build to verify**

```bash
cd app && npm run typecheck && npm run build
```
Expected: passes.

- [ ] **Step 4: Commit**

```bash
git add app/src/App.tsx app/src/components/UnsupportedBanner.tsx
git commit -m "feat(frontend): wire full app shell with providers and panels"
```

---

### Task 22: End-to-end dev run + smoke test

**Goal:** Launch the integrated dev build and smoke-test the golden path. Bugs found here become bugfix commits.

**Files:** none (manual testing)

- [ ] **Step 1: Start dev mode**

```bash
cd src-tauri && cargo tauri dev
```
Expected: Vite spawns on :1420, Rust compiles, a Tauri window opens showing the empty playSong shell with the Header and "no folder selected" message.

- [ ] **Step 2: Add a folder**

In the running app, click `+ Tambah` (or `+ Add` in EN). Pick the repo's `Music/` folder (or any folder containing `.mid` files). The folder should appear in the left list and become selected. Songs from it should populate the right table.

- [ ] **Step 3: Toggle theme/palette/lang**

Click each segmented toggle. The palette should change colors instantly (no flicker). Switching ID/EN should change all visible labels.

- [ ] **Step 4: Play a song**

Pick a song. Click `▶ Mainkan File Ini` (or `Play This File`). The player sheet should open. Open Notepad in the foreground; within ~1s, keys should start landing in Notepad.

- [ ] **Step 5: Test hotkeys**

While Notepad is focused:
- Press **DELETE** → playback toggles. Press again → toggles back. Verify the player sheet's button reflects state.
- Press **HOME** → index decreases by ≤10.
- Press **END** → if not near end, index increases by 10; if near end, it resets and pauses.
- Press **INSERT** → playback restarts from index 0.

- [ ] **Step 6: Restart the app**

Close the Tauri window, then rerun `cargo tauri dev`. The previously-added folder, the chosen theme/palette/lang should all be restored.

- [ ] **Step 7: If anything is broken, fix it before continuing**

Each bug fix is a separate commit (`fix(...): ...`). Re-run the smoke test after each fix.

- [ ] **Step 8: Commit a smoke-test marker (only if all pass without changes)**

If no fixes were needed, this step is a no-op. Otherwise, the fix commits already happened.

---

### Task 23: Release build verification

**Goal:** Produce an MSI installer and verify size/startup/UAC targets.

**Files:** none (build verification)

- [ ] **Step 1: Build release**

```bash
cd src-tauri && cargo tauri build
```
Expected: artifact under `src-tauri/target/release/bundle/msi/playSong_*.msi`.

- [ ] **Step 2: Check bundle size**

```bash
ls -lh src-tauri/target/release/bundle/msi/
ls -lh src-tauri/target/release/playsong.exe
```
Target: `.exe` ≤ 8 MB, `.msi` ≤ 5 MB.

- [ ] **Step 3: Install and verify no UAC prompt**

Run the MSI on a Windows machine. Verify:
- The installer does NOT show a UAC shield icon and does NOT prompt for admin elevation.
- After install, double-clicking `playSong.exe` from Start Menu launches it without a UAC prompt.
- Hotkeys still work globally (alt-tab to Notepad, press DELETE — playback toggles).

- [ ] **Step 4: Measure cold-start time**

Use a stopwatch or `Measure-Command` in PowerShell:
```powershell
Measure-Command { Start-Process -FilePath "$env:ProgramFiles\playSong\playSong.exe" -Wait }
```
Target: time-to-window < 800ms.

- [ ] **Step 5: Document results in commit**

```bash
git commit --allow-empty -m "chore: release build verified — <SIZE_MB>MB MSI, <TIME>ms cold start, no UAC"
```

---

### Task 24: Update repo docs

**Goal:** README + CLAUDE.md describe the new Tauri build path (Python tree preserved alongside).

**Files:**
- Modify: `README.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Add a new top section to `README.md`**

Insert after the project header:

````markdown
## Tauri rewrite (v0.1.x)

**Stack:** Tauri v2, Vite + React 19 + TypeScript, Rust backend (`midly` for MIDI, `enigo` for key injection).

### Dev
```bash
cd app && npm install        # one-time
cd src-tauri && cargo tauri dev
```

### Build
```bash
cd src-tauri && cargo tauri build
# Output: src-tauri/target/release/bundle/msi/playSong_*.msi
```

**No Administrator required** — both global hotkeys and synthetic input use standard Win32 APIs (`SetWindowsHookEx`, `SendInput`).

The legacy Python implementation in `playSong_clean.py` + `src/` is preserved for reference until parity is fully verified, then will be archived.
````

- [ ] **Step 2: Add a section to `CLAUDE.md`**

Insert after the "Architecture" section:

````markdown
## Tauri rewrite layout

In addition to the Python tree, this repo now contains:

- `app/` — Vite + React 19 + TypeScript frontend (one window, no SSR)
- `src-tauri/` — Tauri v2 Rust backend (MIDI parser, key injector, playback engine, hotkeys, config)

When fixing bugs in **the Tauri build**, do NOT modify `playSong_clean.py` or `src/*.py`. The Python tree is the legacy implementation, kept for reference.

### Tauri dev / build
```bash
cd src-tauri && cargo tauri dev    # hot-reload dev
cd src-tauri && cargo tauri build  # production MSI
```

### Tauri tests
```bash
cd src-tauri && cargo test         # 17 unit tests across mapping/injector/midi/playback
cd app && npm run typecheck        # TS strict-mode check
```

### Domain truths (never re-derive — port verbatim)
- `_SCALE` mapping: `src-tauri/src/mapping.rs` (mirrors `src/midi_parser.py:7`)
- `_ALLOWED` whitelist: `src-tauri/src/injector.rs` (mirrors `src/keyboard_sim.py:3-8`)
- `CONVERSION_CASES` shift map: `src-tauri/src/injector.rs::shifted_to_base`
- Hotkey magnitudes (rewind/skip = 10 notes): `src-tauri/src/playback.rs::SEEK_STEP`
- Config schema (`{lang, theme, palette, folders}`): `src-tauri/src/config.rs`
````

- [ ] **Step 3: Commit**

```bash
git add README.md CLAUDE.md
git commit -m "docs: describe Tauri rewrite alongside legacy Python tree"
```

---

## Verification (cumulative)

**Unit tests (Rust):**
```bash
cd src-tauri && cargo test
```
Expected: 17 passed across `mapping` (4), `injector` (4), `midi` (3), `playback` (6).

**Frontend type check:**
```bash
cd app && npm run typecheck
```
Expected: zero errors.

**Frontend build:**
```bash
cd app && npm run build
```
Expected: `app/dist/` produced; bundle visible.

**End-to-end smoke test:** Task 22 + Task 23 above.

**Comparison vs Python baseline:**
- Bundle size ≤ 5 MB (Python: 11 MB).
- Cold start ≤ 800 ms (Python: ~1500 ms with PyInstaller extract).
- No Administrator prompt at install or run (Python: required admin).

**Feature parity checklist:**
- [ ] All 28 strings rendered in both `id` and `en`.
- [ ] All 4 palette/theme combinations switch live without flicker.
- [ ] Folder list persists across restarts.
- [ ] Speed slider 0.25–3.0× scales playback delays.
- [ ] DELETE / HOME / END / INSERT all work globally with the documented magnitudes.
- [ ] Search filters song list with ~200ms debounce.
- [ ] Releasing keys (events with `~` prefix) actually call release, not press.
- [ ] Shifted symbols (`!@#$%^&*()`) press base key with shift held.
