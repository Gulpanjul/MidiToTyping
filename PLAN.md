# Rencana: Rapikan MidiToTyping sesuai 7 Lensa

> **Status: SELESAI (2026-06-15)** — semua gate hijau: `cargo test` 17/17, `npm run typecheck` + `npm run build` lolos, grep ternary inline = 0. Disalin dari `.claude/plans/dynamic-churning-piglet.md` untuk akses tim.

## Context

Setelah review 7-lensa dan pembuatan `SYSTEM_MAP.md`, terkumpul temuan konkret: **doc↔kode mismatch** (klaim "scan rekursif", versi `0.1.x` usang, roadmap fitur v0.2 yang sebenarnya sudah jadi), **debt reusability** (i18n inline), dan **housekeeping** (file `.env` nyasar). Tujuan: rapikan tanpa mengubah perilaku inti, menghormati constraint `CLAUDE.md` (domain truths = port verbatim). Eksekusi **bertahap + ber-gate**: tiap increment dibuktikan test, bukan diklaim.

## Keputusan scope

| Topik | Keputusan |
|---|---|
| Scan rekursif | Perbaiki **dokumen** (non-rekursif = desain, sesuai legacy). Fitur rekursif → Deferred. |
| File `.env` (isi `/docs`) | **Hapus** (nyasar, gitignored, tak dipakai). |
| Header Doc (aturan baru) | Hanya file baru; tidak retrofit file existing. |
| `parse_midi` decompose | **Jangan** — zona verbatim-port. |

## Tier 1 — Aman, nol risiko perilaku ✅

1. README:124 klaim "scan rekursif otomatis" → wording non-rekursif (per folder).
2. Versi `0.1.x`→`0.2.0` (README + CLAUDE: referensi current build + nama artifact MSI/NSIS).
3. Roadmap: tombol in-app rewind/skip/restart ditandai **done** (sudah ada di PlayerSheet).
4. Hapus `.env` (isi `/docs`).
5. a11y: `aria-selected` + `tabIndex` pada baris tabel lagu (MusicPane).
6. Pindahkan `use enigo`/`StdMutex` ke blok import atas (injector.rs).
7. Sinkron `SYSTEM_MAP.md` (key count, blind-spot resolved, `.env` Not found).

## Tier 2 — Refactor terjaga gate ✅

8. Konsolidasi 22 string i18n inline (12+3+1+5 ternary + 2 array bilingual) → `STRINGS`/`StringsBundle` (PlayerSheet, InfoPopup, MusicPane, BottomBar).
9. Satukan 4 handler hotkey → 1 macro `hotkey!` (payload `is_playing` khusus DELETE dipertahankan).

## Deferred — tunggu permintaan

`useNoteLog()` hook · virtualization tabel (`@tanstack/react-virtual`) · perketat CSP (`csp:null`) · fitur scan rekursif · micro-opt clone `NoteEvent` per tick · `parse_midi` decompose (verbatim-port).

## Verifikasi (sudah dijalankan)

- `cargo test --manifest-path src-tauri/Cargo.toml` → 17 passed.
- `npm --prefix app run typecheck` → lolos.
- `npm --prefix app run build` → sukses (1605 modul).
- grep `lang === 'id'` di `app/src` → 0.

## Catatan kepatuhan

- Verbatim-port dihormati: `mapping.rs`, `midi.rs`, `playback.rs`, whitelist/shift `injector.rs` tidak disentuh.
- WIP Playwright (`app/e2e/`, `playwright.config.ts`, `package*.json`, `app/.gitignore`) di luar scope — tidak ikut di-commit.
