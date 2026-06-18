# Plan: Tidy Up MidiToTyping per the 7 Quality Lenses

> **Status: DONE (2026-06-15)** — all gates green: `cargo test` 17/17, `npm run typecheck` + `npm run build` pass, residual inline-i18n ternaries grep = 0. Copied from `.claude/plans/dynamic-churning-piglet.md` for team access.

## Context

After the 7-lens review and creation of `SYSTEM_MAP.md`, a set of concrete findings surfaced: **doc↔code mismatches** (the "recursive scan" claim, stale `0.1.x` version, a v0.2 roadmap item that was actually already shipped), **reusability debt** (inline i18n), and **housekeeping** (a stray `.env` file). Goal: tidy these up without changing core behavior, honoring the `CLAUDE.md` constraint (domain truths = verbatim port). Execution is **incremental + gated**: each increment is proven by tests, not asserted.

## Scope decisions

| Topic | Decision |
|---|---|
| Recursive scan | Fix the **docs** (non-recursive is by design, matching legacy). Recursive feature → Deferred. |
| `.env` file (content `/docs`) | **Delete** (stray, gitignored, unused). |
| Header Doc (new rule) | New files only; do not retrofit existing files. |
| `parse_midi` decompose | **Don't** — verbatim-port zone. |

## Tier 1 — Safe, zero behavior risk ✅

1. README:124 "scan rekursif otomatis" claim → non-recursive wording (per folder).
2. Version `0.1.x`→`0.2.0` (README + CLAUDE: current-build references + MSI/NSIS artifact names).
3. Roadmap: mark the in-app rewind/skip/restart buttons as **done** (already present in PlayerSheet).
4. Delete `.env` (content `/docs`).
5. a11y: `aria-selected` + `tabIndex` on song table rows (MusicPane).
6. Move `use enigo`/`StdMutex` to the top import block (injector.rs).
7. Sync `SYSTEM_MAP.md` (key count, resolved blind-spots, `.env` Not found).

## Tier 2 — Test-guarded refactor ✅

8. Consolidate 22 inline i18n strings (12+3+1+5 ternaries + 2 bilingual arrays) into `STRINGS`/`StringsBundle` (PlayerSheet, InfoPopup, MusicPane, BottomBar).
9. Collapse the 4 hotkey handlers into a single `hotkey!` macro (the DELETE handler keeps its extra `is_playing` payload).

## Deferred — on request

`useNoteLog()` hook · table virtualization (`@tanstack/react-virtual`) · tighten CSP (`csp:null`) · recursive folder scan feature · micro-opt the per-tick `NoteEvent` clone · `parse_midi` decompose (verbatim port).

## Verification (already run)

- `cargo test --manifest-path src-tauri/Cargo.toml` → 17 passed.
- `npm --prefix app run typecheck` → pass.
- `npm --prefix app run build` → success (1605 modules).
- grep `lang === 'id'` in `app/src` → 0.

## Compliance notes

- Verbatim port respected: `mapping.rs`, `midi.rs`, `playback.rs`, the `injector.rs` whitelist/shift map were not touched.
- The Playwright WIP (`app/e2e/`, `playwright.config.ts`, `package*.json`, `app/.gitignore`) is out of scope — not committed.
