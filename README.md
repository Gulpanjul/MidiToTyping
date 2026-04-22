<!--
============================================================
File: README.md
Date: 2026-04-13
Author: playSong maintainer
Task: Dokumentasi penggunaan, build, dan format file lagu
AI-Assisted: Yes — Claude Code (Opus 4.6)
============================================================
-->

# 🎵 playSong — Song Auto-Player

Program Python yang secara otomatis memencet keyboard untuk memainkan lagu (MIDI) — cocok untuk game piano seperti **Sky: Children of the Light**, **Piano Tiles**, atau instrumen virtual berbasis keyboard mapping.

> **Sensitivity**: PUBLIC — tidak ada kredensial, data pribadi, atau konfigurasi produksi di repo ini.

---

## ✨ Fitur

- 🎹 **Auto-player MIDI** — parsing file `.mid` / `.midi` otomatis ke mapping tombol keyboard
- 📁 **Multi-folder scan** — tambah berapapun folder, scan rekursif semua subfolder
- 🔍 **GUI pemilih lagu** — filter real-time, sort kolom, grouping per folder, navigasi keyboard
- ⚡ **Slider kecepatan** — 0.25× sampai 3.00×
- ⏯ **Hotkey playback** — Play/Pause, Rewind, Skip, Restart
- 🎼 **Tempo marker in-song** — dukung `tempo=120` di tengah lagu

---

## 📦 Struktur Project

```
py/
├── playSong_clean.py      ← Source utama
├── playSong_clean.spec    ← PyInstaller spec file
├── dist/                  ← Hasil build (.exe)
├── build/                 ← Cache build PyInstaller
├── tests/                 ← Test scripts & sample MIDI
├── archive/               ← Versi lama, file referensi
└── docs/                  ← Standar LSH Group + fe-acara guidelines
```

---

## 🚀 Menjalankan (Development)

### Prerequisites

- Python 3.10+
- Library: `keyboard`, `mido`

```bash
pip install keyboard mido
```

### Run

```bash
python playSong_clean.py
```

> **⚠️ Windows**: Library `keyboard` memerlukan **administrator privileges** untuk menangkap global hotkey. Jalankan terminal sebagai Administrator.

---

## 🎮 Cara Pakai

1. Jalankan program → GUI pemilih file terbuka
2. Klik **➕ Tambah** untuk menambahkan folder berisi file `.mid`
3. Program akan scan rekursif semua subfolder
4. Filter dengan kolom search, pilih lagu, set kecepatan dengan slider
5. Klik **▶ Mainkan File Ini** (atau double-click, atau tekan Enter)
6. Fokuskan window game target, lalu tekan hotkey untuk mulai:

### Hotkey Playback

| Tombol | Fungsi |
|--------|--------|
| `DELETE` | Play / Pause |
| `HOME` | Rewind (mundur 10 nada) |
| `END` | Skip (maju 10 nada) |
| `INSERT` | Restart dari awal |
| `Ctrl+C` | Keluar program |

---

## 📝 Format File Lagu

### MIDI (direkomendasikan)

File `.mid` / `.midi` langsung didukung. Program otomatis mengonversi not MIDI ke mapping piano 61-tombol (mulai dari C2 = note 36).

### Text Format (fallback internal)

Saat memproses MIDI, program menghasilkan file temp `~temp_midi_convert.txt` dengan format:

```
<timestamp_beat>  <tombol>
0.0000   q        ← tekan tombol 'q'
0.5000   we       ← tekan 'w' dan 'e' bersamaan
1.0000   ~q       ← lepaskan tombol 'q' (prefix ~)
1.5000   tempo=120 ← ubah BPM di tengah lagu
```

**Key scale** (61 tombol, C2 ke atas):
```
1!2@34$5%6^78*9(0qQwWeErtTyYuiIoOpPasSdDfgGhHjJklLzZxcCvVbBnm
```

---

## 🔨 Build ke `.exe`

Project sudah punya `playSong_clean.spec`. Untuk rebuild:

```bash
pip install pyinstaller
pyinstaller playSong_clean.spec
```

Output: `dist/playSong_clean.exe`

### Opsi build alternatif (tanpa spec file)

```bash
pyinstaller --onefile --console playSong_clean.py
```

---

## ⚠️ Known Limitations

Ini batasan yang **harus diketahui sebelum pakai** (G3 Discernment — surface problems, don't hide them):

1. **Hanya bekerja di foreground window** — library `keyboard` mensimulasikan penekanan tombol fisik secara global. Artinya window game harus punya fokus. Mengetik di aplikasi lain saat lagu main akan ter-interrupt.

2. **Tidak bisa target HWND spesifik** — pendekatan `PostMessage`/`SendMessage` ke window handle sudah dipertimbangkan, tapi **tidak dijalankan** karena mayoritas game modern (Unity, Unreal) pakai DirectInput/Raw Input yang mem-bypass message queue Windows. Pesan yang dikirim akan diabaikan engine game.

3. **Butuh admin di Windows** — global keyboard hook memerlukan elevated privileges.

4. **MIDI multi-channel flattened** — semua track digabung. Mapping not di luar range 61-tombol akan dilipat (folded) ke oktaf terdekat.

5. **Timer latency** — `threading.Timer` punya jitter ~10-15ms pada Windows. Lagu dengan BPM sangat tinggi mungkin terasa kurang presisi.

---

## 🛡 Security & Compliance

Project ini mengikuti **LSH Group AI-Assisted Development Standards v1.0** (lihat [docs/CLAUDE.md](docs/CLAUDE.md)):

- ✅ **No hardcoded secrets** — tidak ada API key, password, atau token
- ✅ **No PII** — tidak ada data pengguna nyata
- ✅ **Error handling** — parser file dan MIDI punya graceful fallback
- ✅ **AI transparency** — lihat footer

**Sensitivity Level**: PUBLIC (Level 0) — safe untuk dishare internal maupun eksternal.

---

## 🧪 Testing

File test & sample MIDI ada di [tests/](tests/):

```bash
python tests/test_midi.py
python tests/test_playSong.py
```

---

## 📚 Dokumentasi Tambahan

- [docs/CLAUDE.md](docs/CLAUDE.md) — Clean code standards (frontend + LSH Group AI discipline)
- [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) — Cheat sheet 4D + 6-Gate Protocol
- [docs/PORTABILITY_ANALYSIS.md](docs/PORTABILITY_ANALYSIS.md) — Analisis portabilitas struktur clean code

> **Catatan**: Sebagian besar dokumen di `docs/` adalah standar **frontend Next.js** (fe-acara). Bagian yang relevan untuk project Python ini adalah: **file header block**, **AI transparency**, **4D Protocol**, **6-Gate Protocol**, dan **security standards**.

---

## 📄 Lisensi

Internal project. Tidak untuk distribusi eksternal tanpa izin.

---

**AI Role**: Co-authored — Claude Code (Opus 4.6) drafted the README, human maintainer reviews and approves.
**Human verification**: Reviewed — pastikan technical claims akurat sebelum dishare.

*Produced with AI assistance | Reviewed by: [Your Name]*

**Last Updated**: 2026-04-13
**Version**: 1.0.0
