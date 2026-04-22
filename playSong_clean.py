# ============================================================
# File: playSong_clean.py
# Date: 2026-04-21
# Author: playSong maintainer
# Task: Auto-player MIDI → keyboard simulation untuk game piano
# AI-Assisted: Yes — Claude Code (Sonnet 4.6)
# ============================================================

"""
playSong.py - Piano Tile / Song Auto-Player
============================================
Program ini secara otomatis memencet keyboard untuk memainkan lagu
(untuk game seperti Sky: Children of the Light, Piano Tiles, dll).

Cara kerja:
- Buka GUI → pilih folder → navigasi folder → pilih lagu
- Mensimulasikan penekanan keyboard sesuai timing di file lagu

Kontrol saat bermain:
- DELETE  : Play / Pause
- HOME    : Rewind (mundur 10 langkah)
- END     : Skip   (maju  10 langkah)
- Ctrl+C  : Keluar

Format file lagu (.txt):
    <timestamp_detik>  <tombol>
    0.0  q
    0.5  we
    1.0  ~q        ← prefix ~ = lepaskan tombol
    1.5  tempo=120 ← ubah BPM di tengah lagu
"""

import os
import sys
import json
import threading
# keyboard diimport secara lazy di press_letter / release_letter / main()

# ──────────────────────────────────────────────────────────
# Global state
# ──────────────────────────────────────────────────────────
LANG          : str   = 'id'
THEME         : str   = 'dark'
PALETTE       : str   = 'celestial'
is_playing    : bool  = False
stored_index  : int   = 0
playback_speed: float = 1.0
info_tuple    : tuple = (1.0, None, [])
_play_gen     : int   = 0
folder_history: list  = []

CONVERSION_CASES: dict = {
    '!': '1', '@': '2', '#': '3', '£': '3', '$': '4', '%': '5',
    '^': '6', '&': '7', '*': '8', '(': '9', ')': '0',
}

SUPPORTED_EXTENSIONS: tuple = ('.mid', '.midi')

# ──────────────────────────────────────────────────────────
# Localization strings
# ──────────────────────────────────────────────────────────
STRINGS: dict = {
    'id': {
        'splash_loading'    : 'Memuat aplikasi...',
        'splash_subtitle'   : 'Auto-Player Piano · Sky & Piano Tiles',
        'window_title'      : '🎵 Song Player – Pilih File Lagu',
        'header_title'      : '🎵  Song Auto-Player',
        'header_subtitle'   : 'Pilih folder → pilih lagu → mainkan',
        'folder_nav_panel'  : '📁  Navigasi Folder',
        'back_btn'          : '← Kembali',
        'add_folder_btn'    : '➕ Tambah',
        'remove_folder_btn' : '➖ Hapus',
        'add_folder_dialog' : 'Pilih Folder Lagu',
        'no_folder_selected': '  Pilih folder untuk melihat file lagu...',
        'speed_label'       : '⚡ Kecepatan Putar',
        'speed_range'       : '0.25×  ──────  3.00×',
        'diff_beginner'     : ('🐣 Pemula',  '#6BCB77'),
        'diff_learning'     : ('📖 Belajar', '#74C0FC'),
        'diff_relaxed'      : ('😌 Santai',  '#A9C0D6'),
        'diff_normal'       : ('✅ Normal',  '#CDD6F4'),
        'diff_advanced'     : ('⚡ Mahir',   '#FFA94D'),
        'diff_pro'          : ('🔥 Pro',     '#FF6B6B'),
        'diff_master'       : ('💎 Master',  '#DA77F2'),
        'col_no'            : 'No',
        'col_title'         : 'Judul',
        'col_size_kb'       : 'Ukuran',
        'file_count_fmt'    : '{shown}/{total} file',
        'file_count_all'    : '{total} file',
        'status_file'       : '  {path}  |  {size:,} bytes  |  {mtime}',
        'play_btn'          : '▶  Mainkan File Ini',
        'cancel_btn'        : '✕  Batal',
        'warn_title'        : 'Pilih File',
        'warn_msg'          : 'Silakan pilih file dari daftar terlebih dahulu.',
        'no_file_msg'       : 'Tidak ada file yang dipilih. Keluar.',
        'mido_title'        : 'Mido Missing',
        'mido_msg'          : (
            "Library 'mido' tidak ditemukan.\n"
            "Jalankan perintah ini di terminal:\npip install mido"
        ),
        'palette_celestial' : '🌌 Sky',
        'palette_grand'     : '🎹 Piano',
    },
    'en': {
        'splash_loading'    : 'Loading application...',
        'splash_subtitle'   : 'Piano Auto-Player · Sky & Piano Tiles',
        'window_title'      : '🎵 Song Player – Select Song File',
        'header_title'      : '🎵  Song Auto-Player',
        'header_subtitle'   : 'Select folder → choose song → play',
        'folder_nav_panel'  : '📁  Folder Navigator',
        'back_btn'          : '← Back',
        'add_folder_btn'    : '➕ Add',
        'remove_folder_btn' : '➖ Remove',
        'add_folder_dialog' : 'Select Song Folder',
        'no_folder_selected': '  Select a folder on the left to view song files...',
        'speed_label'       : '⚡ Playback Speed',
        'speed_range'       : '0.25×  ──────  3.00×',
        'diff_beginner'     : ('🐣 Beginner',  '#6BCB77'),
        'diff_learning'     : ('📖 Learning',  '#74C0FC'),
        'diff_relaxed'      : ('😌 Relaxed',   '#A9C0D6'),
        'diff_normal'       : ('✅ Normal',     '#CDD6F4'),
        'diff_advanced'     : ('⚡ Advanced',   '#FFA94D'),
        'diff_pro'          : ('🔥 Pro',        '#FF6B6B'),
        'diff_master'       : ('💎 Master',     '#DA77F2'),
        'col_no'            : 'No',
        'col_title'         : 'Title',
        'col_size_kb'       : 'Size',
        'file_count_fmt'    : '{shown}/{total} files',
        'file_count_all'    : '{total} files',
        'status_file'       : '  {path}  |  {size:,} bytes  |  {mtime}',
        'play_btn'          : '▶  Play This File',
        'cancel_btn'        : '✕  Cancel',
        'warn_title'        : 'Select File',
        'warn_msg'          : 'Please select a file from the list first.',
        'no_file_msg'       : 'No file selected. Exiting.',
        'mido_title'        : 'Mido Missing',
        'mido_msg'          : (
            "Library 'mido' not found.\n"
            "Run this command in terminal:\npip install mido"
        ),
        'palette_celestial' : '🌌 Sky',
        'palette_grand'     : '🎹 Piano',
    },
}

# ──────────────────────────────────────────────────────────
# Theme color palettes — eye-friendly, balanced contrast
# ──────────────────────────────────────────────────────────
THEMES: dict = {
    'celestial': {
        'dark': {
            'BG'      : '#192236',
            'PANEL'   : '#1E2D47',
            'ACCENT'  : '#7EC8E3',
            'TEXT'    : '#D6E4F0',
            'SUBTEXT' : '#6D8EA6',
            'ENTRY_BG': '#131B2C',
            'BTN_HOV' : '#5BAFCC',
            'ROW_ALT' : '#1C2940',
            'SEL_BG'  : '#2A4A6A',
        },
        'light': {
            'BG'      : '#EBF4FD',
            'PANEL'   : '#D4E8F7',
            'ACCENT'  : '#1E6FA5',
            'TEXT'    : '#0D2136',
            'SUBTEXT' : '#4A7A9B',
            'ENTRY_BG': '#FFFFFF',
            'BTN_HOV' : '#165A8A',
            'ROW_ALT' : '#F2F8FE',
            'SEL_BG'  : '#BFD9EE',
        },
    },
    'grand_piano': {
        'dark': {
            'BG'      : '#1A1A1A',
            'PANEL'   : '#242424',
            'ACCENT'  : '#C8A96E',
            'TEXT'    : '#EDE8DC',
            'SUBTEXT' : '#7A7268',
            'ENTRY_BG': '#1E1E1E',
            'BTN_HOV' : '#B89558',
            'ROW_ALT' : '#1D1D1D',
            'SEL_BG'  : '#3D3020',
        },
        'light': {
            'BG'      : '#FAF6EE',
            'PANEL'   : '#EDE7D8',
            'ACCENT'  : '#2A2016',
            'TEXT'    : '#2A2016',
            'SUBTEXT' : '#6B5E4A',
            'ENTRY_BG': '#FFFDF5',
            'BTN_HOV' : '#4A3C28',
            'ROW_ALT' : '#F5F0E2',
            'SEL_BG'  : '#D8CEBA',
        },
    },
}


# ──────────────────────────────────────────────────────────
# Config persistence  (lang / theme / palette / folders)
# ──────────────────────────────────────────────────────────
def _config_path() -> str:
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'playSong_config.json')


def load_config() -> None:
    global LANG, THEME, PALETTE, folder_history
    try:
        with open(_config_path(), 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        if cfg.get('lang') in ('id', 'en'):
            LANG = cfg['lang']
        if cfg.get('theme') in ('dark', 'light'):
            THEME = cfg['theme']
        if cfg.get('palette') in ('celestial', 'grand_piano'):
            PALETTE = cfg['palette']
        if isinstance(cfg.get('folders'), list):
            folder_history = [p for p in cfg['folders'] if isinstance(p, str)]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass


def save_config() -> None:
    try:
        with open(_config_path(), 'w', encoding='utf-8') as f:
            json.dump({
                'lang'   : LANG,
                'theme'  : THEME,
                'palette': PALETTE,
                'folders': list(folder_history),
            }, f, indent=2, ensure_ascii=False)
    except OSError:
        pass


# ──────────────────────────────────────────────────────────
# Helper: apakah karakter butuh Shift?
# ──────────────────────────────────────────────────────────
def is_shifted(char: str) -> bool:
    ascii_val = ord(char)
    if 65 <= ascii_val <= 90:
        return True
    if char in '!@#$%^&*()_+{}|:"<>?':
        return True
    return False


# ──────────────────────────────────────────────────────────
# Simulasi keyboard
# ──────────────────────────────────────────────────────────
def press_letter(letter: str) -> None:
    import keyboard
    if is_shifted(letter):
        if letter in CONVERSION_CASES:
            letter = CONVERSION_CASES[letter]
        keyboard.release(letter.lower())
        keyboard.press('left shift')
        keyboard.press(letter.lower())
        keyboard.release('left shift')
    else:
        keyboard.release(letter)
        keyboard.press(letter)


def release_letter(letter: str) -> None:
    import keyboard
    if is_shifted(letter):
        if letter in CONVERSION_CASES:
            letter = CONVERSION_CASES[letter]
        keyboard.release(letter.lower())
    else:
        keyboard.release(letter)


# ──────────────────────────────────────────────────────────
# Parser file MIDI / lagu teks
# ──────────────────────────────────────────────────────────
def parse_song_file(filepath: str) -> tuple:
    if filepath.lower().endswith(('.mid', '.midi')):
        try:
            import mido
        except ImportError as _e:
            import tkinter.messagebox as messagebox
            S = STRINGS[LANG]
            if getattr(sys, 'frozen', False):
                # Running as .exe — sub-module bundling issue
                msg = (
                    "Modul MIDI tidak ter-bundle dengan benar di dalam exe.\n"
                    "Silakan download ulang versi terbaru aplikasi ini.\n\n"
                    f"Detail: {_e}"
                    if LANG == 'id' else
                    "MIDI module was not bundled correctly inside the exe.\n"
                    "Please re-download the latest version of this app.\n\n"
                    f"Detail: {_e}"
                )
            else:
                msg = S['mido_msg']
            messagebox.showerror(S['mido_title'], msg)
            sys.exit(1)

        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        txt_path = os.path.join(base_dir, '~temp_midi_convert.txt')
        print(f"\n[MIDI] Membaca {filepath} \n       -> (temp) {txt_path}")
        mid            = mido.MidiFile(filepath)
        ticks_per_beat = mid.ticks_per_beat
        scale          = '1!2@34$5%6^78*9(0qQwWeErtTyYuiIoOpPasSdDfgGhHjJklLzZxcCvVbBnm'

        merged           = mido.merge_tracks(mid.tracks)
        abs_ticks        = 0
        first_note_ticks = None
        lines            = []

        for msg in merged:
            abs_ticks += msg.time
            if msg.type == 'set_tempo':
                bpm      = round(60_000_000 / msg.tempo)
                beat_pos = abs_ticks / ticks_per_beat
                if first_note_ticks is not None:
                    beat_pos = (abs_ticks - first_note_ticks) / ticks_per_beat
                lines.append(f"{beat_pos:.4f} tempo={bpm}")

            elif msg.type in ('note_on', 'note_off'):
                map_idx = msg.note - 36
                while map_idx >= len(scale):
                    map_idx -= 12
                while map_idx < 0:
                    map_idx += 12

                if first_note_ticks is None:
                    first_note_ticks = abs_ticks

                beat_pos = (abs_ticks - first_note_ticks) / ticks_per_beat
                char     = scale[map_idx]

                if msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    lines.append(f"{beat_pos:.4f} ~{char}")
                else:
                    lines.append(f"{beat_pos:.4f} {char}")

        with open(txt_path, 'w', encoding='utf-8') as f:
            for ln in lines:
                f.write(ln + '\n')

        filepath = txt_path

    notes: list = []
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(None, 1)
            if len(parts) < 2:
                continue
            try:
                timestamp = float(parts[0])
                keys      = parts[1].strip()
                notes.append([timestamp, keys])
            except ValueError:
                continue
    return (1.0, None, [[0.0, 'header']] + notes)


# ──────────────────────────────────────────────────────────
# Splash screen
# ──────────────────────────────────────────────────────────
def show_splash() -> None:
    import tkinter as tk
    from tkinter import ttk

    C = THEMES[PALETTE][THEME]
    S = STRINGS[LANG]

    splash = tk.Tk()
    splash.overrideredirect(True)

    w, h = 440, 240
    sw   = splash.winfo_screenwidth()
    sh   = splash.winfo_screenheight()
    x    = (sw - w) // 2
    y    = (sh - h) // 2
    splash.geometry(f'{w}x{h}+{x}+{y}')
    splash.configure(bg=C['ACCENT'])
    splash.attributes('-topmost', True)

    inner = tk.Frame(splash, bg=C['BG'], padx=2, pady=2)
    inner.pack(fill='both', expand=True, padx=3, pady=3)

    tk.Label(inner, text='🎵', bg=C['BG'], fg=C['ACCENT'],
             font=('Segoe UI Emoji', 40)).pack(pady=(28, 4))
    tk.Label(inner, text='Song Auto-Player',
             bg=C['BG'], fg=C['TEXT'],
             font=('Segoe UI', 16, 'bold')).pack()
    tk.Label(inner, text=S['splash_subtitle'],
             bg=C['BG'], fg=C['SUBTEXT'],
             font=('Segoe UI', 9)).pack(pady=(4, 20))

    style = ttk.Style(splash)
    style.theme_use('clam')
    style.configure('Splash.Horizontal.TProgressbar',
        troughcolor=C['ENTRY_BG'], background=C['ACCENT'],
        bordercolor=C['BG'], lightcolor=C['ACCENT'], darkcolor=C['ACCENT'])

    pb = ttk.Progressbar(inner, style='Splash.Horizontal.TProgressbar',
                         orient='horizontal', length=320, mode='determinate')
    pb.pack()
    tk.Label(inner, text=S['splash_loading'],
             bg=C['BG'], fg=C['SUBTEXT'],
             font=('Segoe UI', 8)).pack(pady=6)

    steps    = 40
    interval = 2000 // steps

    def _animate(step: int = 0) -> None:
        if step <= steps:
            pb['value'] = step * (100 / steps)
            splash.after(interval, _animate, step + 1)
        else:
            splash.destroy()

    splash.after(0, _animate)
    splash.mainloop()


# ──────────────────────────────────────────────────────────
# GUI — Two-pane: Folder Navigator (left) + Music List (right)
# ──────────────────────────────────────────────────────────
def process_file() -> 'tuple | str | None':
    """
    Return: infoTuple, '__RELOAD__' (bahasa toggle), atau None (batal).
    Perubahan tema/palet ditangani live via repaint() tanpa menutup window.
    """
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk
    import datetime

    global playback_speed, folder_history, LANG, THEME, PALETTE

    S = STRINGS[LANG]
    C: dict = dict(THEMES[PALETTE][THEME])   # mutable in-place → repaint-safe

    def _reload_C() -> None:
        C.clear()
        C.update(THEMES[PALETTE][THEME])

    if not folder_history:
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        folder_history.append(os.path.normpath(base_dir))

    # ── State ──────────────────────────────────────────────
    selected_path  = [None]
    folder_list    = folder_history          # alias
    nav_folder     = [None]                  # None = root level
    nav_stack      : list = []               # for Back navigation
    active_folder  = [None]                  # folder shown in music list
    display_folders: list = []               # paths currently in folder_lb
    music_files    : list = []               # dicts in music tree
    sort_key_music = ['name']
    sort_rev_music = [False]

    # ── Window ─────────────────────────────────────────────
    root = tk.Tk()
    root.title(S['window_title'])
    root.geometry('860x600')
    root.minsize(680, 480)
    root.configure(bg=C['BG'])

    style = ttk.Style(root)
    style.theme_use('clam')

    def _apply_ttk_style() -> None:
        style.configure('Treeview',
            background=C['ENTRY_BG'], foreground=C['TEXT'],
            fieldbackground=C['ENTRY_BG'], rowheight=22,
            font=('Consolas', 9))
        style.configure('Treeview.Heading',
            background=C['PANEL'], foreground=C['TEXT'],
            font=('Segoe UI', 9, 'bold'), relief='flat')
        style.map('Treeview',
            background=[('selected', C['ACCENT'])],
            foreground=[('selected', C['BG'])])
        style.configure('TScrollbar',
            background=C['PANEL'], troughcolor=C['BG'], arrowcolor=C['TEXT'])

    _apply_ttk_style()

    def _close_window() -> None:
        root.quit()
        root.destroy()

    # ── Widget factories ────────────────────────────────────
    def make_btn(parent, text, cmd, accent=False, width=None):
        kw = {'width': width} if width else {}
        b  = tk.Button(
            parent, text=text, command=cmd, relief='flat',
            bg=C['ACCENT'] if accent else C['PANEL'],
            fg=C['BG']     if accent else C['TEXT'],
            font=('Segoe UI', 9, 'bold' if accent else 'normal'),
            padx=10, pady=5, cursor='hand2', bd=0,
            activebackground=C['BTN_HOV'],
            activeforeground=C['BG'] if accent else C['TEXT'],
            **kw,
        )
        if accent:
            b.bind('<Enter>', lambda _: b.config(bg=C['BTN_HOV']))
            b.bind('<Leave>', lambda _: b.config(bg=C['ACCENT']))
        else:
            b.bind('<Enter>', lambda _: b.config(bg=C['BTN_HOV']))
            b.bind('<Leave>', lambda _: b.config(bg=C['PANEL']))
        return b

    def make_seg_btn(parent, text, active: bool, cmd):
        b = tk.Button(
            parent, text=text, command=cmd, relief='flat',
            bg=C['ACCENT'] if active else C['PANEL'],
            fg=C['BG']     if active else C['TEXT'],
            font=('Segoe UI', 8, 'bold' if active else 'normal'),
            padx=8, pady=3, cursor='hand2', bd=0,
            activebackground=C['BTN_HOV'], activeforeground=C['BG'],
        )
        if not active:
            b.bind('<Enter>', lambda _: b.config(bg=C['BTN_HOV']))
            b.bind('<Leave>', lambda _: b.config(bg=C['PANEL']))
        return b

    def _rebuild_seg(frame, items, cur_val, cmd_fn) -> None:
        for child in frame.winfo_children():
            child.destroy()
        for val, lbl in items:
            make_seg_btn(frame, lbl, cur_val == val,
                         lambda v=val: cmd_fn(v)).pack(side='left', padx=1)

    # ── Toggle functions ────────────────────────────────────
    def set_lang(lang: str) -> None:
        global LANG
        if LANG == lang:
            return
        LANG = lang
        save_config()
        selected_path[0] = '__RELOAD__'
        root.after_idle(_close_window)

    def set_theme(theme: str) -> None:
        global THEME
        if THEME == theme:
            return
        THEME = theme
        save_config()
        repaint()

    def set_palette(palette: str) -> None:
        global PALETTE
        if PALETTE == palette:
            return
        PALETTE = palette
        save_config()
        repaint()

    # ── Folder navigation helpers ───────────────────────────
    def _get_subdirs(path: str) -> list:
        try:
            return sorted(
                [os.path.join(path, d) for d in os.listdir(path)
                 if os.path.isdir(os.path.join(path, d))],
                key=lambda p: os.path.basename(p).lower(),
            )
        except OSError:
            return []

    def _breadcrumb_text() -> str:
        """Construct display path relative to a root folder."""
        if nav_folder[0] is None:
            return '/'
        path = nav_folder[0]
        for root_f in folder_list:
            if path == root_f or path.startswith(root_f + os.sep):
                rel  = os.path.relpath(path, root_f)
                base = os.path.basename(root_f) or root_f
                return base if rel == '.' else f'{base} › {rel.replace(os.sep, " › ")}'
        return os.path.basename(path) or path

    def load_folder_pane(folder=None) -> None:
        """Populate folder_lb with root folders or sub-dirs of `folder`."""
        folder_lb.delete(0, tk.END)
        display_folders.clear()
        nav_folder[0] = folder

        if folder is None:
            items = list(folder_list)
        else:
            sub   = _get_subdirs(folder)
            items = sub if sub else [folder]   # leaf: show self as marker

        display_folders.extend(items)
        for path in items:
            name = os.path.basename(path) or path
            folder_lb.insert(tk.END, f'📁  {name}')
        folder_lb.itemconfig(0 if items else tk.END, foreground=C['TEXT'])
        for i in range(folder_lb.size()):
            folder_lb.itemconfig(i, foreground=C['TEXT'])

        lbl_breadcrumb.config(text=_breadcrumb_text())

        # Back button: enabled when we can go up
        can_back = bool(nav_stack) or nav_folder[0] is not None
        btn_back.config(state='normal' if can_back else 'disabled',
                        fg=C['ACCENT'] if can_back else C['SUBTEXT'])

        # Remove: only available at root level (to protect file system)
        at_root = nav_folder[0] is None
        btn_remove.config(state='normal' if at_root else 'disabled')

    def on_folder_click(event=None) -> None:
        """Single click: show files + navigate into folder (if it has sub-dirs)."""
        sel = folder_lb.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx >= len(display_folders):
            return
        path = display_folders[idx]

        # Always update music list immediately
        active_folder[0] = path
        refresh_music()

        # Navigate deeper if this folder has sub-dirs
        if _get_subdirs(path):
            nav_stack.append(nav_folder[0])
            load_folder_pane(path)

    def on_back_click() -> None:
        """Go up one level in the folder hierarchy."""
        if nav_stack:
            prev = nav_stack.pop()
            load_folder_pane(prev)
        else:
            load_folder_pane(None)
        active_folder[0] = nav_folder[0]
        refresh_music()

    def on_add_folder() -> None:
        path = filedialog.askdirectory(parent=root, title=S['add_folder_dialog'])
        if path:
            path = os.path.normpath(path)
            if path not in folder_list:
                folder_list.append(path)
                save_config()
                if nav_folder[0] is None:
                    load_folder_pane(None)

    def on_remove_folder() -> None:
        if nav_folder[0] is not None:
            return                              # only remove root folders
        sel = folder_lb.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx < len(display_folders):
            path = display_folders[idx]
            if path in folder_list:
                folder_list.remove(path)
                if active_folder[0] == path:
                    active_folder[0] = None
                    refresh_music()
                save_config()
                load_folder_pane(None)

    # ── Music list helpers ──────────────────────────────────
    def _scan_flat(folder: str) -> list:
        """Non-recursive: .midi files directly in `folder`."""
        try:
            names = sorted(
                [f for f in os.listdir(folder)
                 if f.lower().endswith(SUPPORTED_EXTENSIONS)],
                key=str.lower,
            )
        except OSError:
            return []
        result = []
        for name in names:
            full = os.path.join(folder, name)
            try:
                size = os.stat(full).st_size
            except OSError:
                size = 0
            result.append({'path': full, 'name': name, 'size': size})
        return result

    def refresh_music() -> None:
        for item in tree.get_children():
            tree.delete(item)
        music_files.clear()

        folder = active_folder[0]
        if not folder or not os.path.isdir(folder):
            lbl_count.config(text='0 file')
            lbl_status.config(text=S['no_folder_selected'])
            return

        raw = _scan_flat(folder)

        # Search filter
        kw = search_var.get().lower()
        if kw:
            raw = [f for f in raw if kw in f['name'].lower()]

        # Sort
        sk  = sort_key_music[0]
        rev = sort_rev_music[0]
        if sk == 'size':
            raw.sort(key=lambda f: f['size'], reverse=rev)
        else:
            raw.sort(key=lambda f: f['name'].lower(), reverse=rev)

        music_files.extend(raw)
        n_total = len(_scan_flat(folder)) if kw else len(raw)

        for i, f in enumerate(raw, 1):
            size_kb = max(1, f['size'] // 1024)
            tag     = 'odd' if i % 2 else 'even'
            tree.insert('', tk.END, iid=f'music_{i}',
                        values=(i, f['name'], f'{size_kb} KB'), tags=(tag,))

        tree.tag_configure('odd',  background=C['ENTRY_BG'], foreground=C['TEXT'])
        tree.tag_configure('even', background=C['ROW_ALT'],  foreground=C['TEXT'])

        n = len(raw)
        if kw:
            lbl_count.config(text=S['file_count_fmt'].format(shown=n, total=n_total))
        else:
            lbl_count.config(text=S['file_count_all'].format(total=n))

        status_txt = S['no_folder_selected'] if n == 0 else f'  {n} file'
        lbl_status.config(text=status_txt)

    def sort_music(key: str) -> None:
        if sort_key_music[0] == key:
            sort_rev_music[0] = not sort_rev_music[0]
        else:
            sort_key_music[0] = key
            sort_rev_music[0] = False
        refresh_music()

    # ── repaint (live theme update) ─────────────────────────
    def repaint() -> None:
        _reload_C()
        _apply_ttk_style()

        root.configure(bg=C['BG'])
        frm_top.configure(bg=C['PANEL'])
        frm_header_left.configure(bg=C['PANEL'])
        frm_header_right.configure(bg=C['PANEL'])
        lbl_title.configure(bg=C['PANEL'],    fg=C['ACCENT'])
        lbl_subtitle.configure(bg=C['PANEL'], fg=C['SUBTEXT'])

        for frm in (frm_theme_seg, frm_palette_seg, frm_lang_seg):
            frm.configure(bg=C['BG'])
        _rebuild_seg(frm_theme_seg,
                     [('dark', '🌙'), ('light', '☀️')],
                     THEME, set_theme)
        _rebuild_seg(frm_palette_seg,
                     [('celestial', S['palette_celestial']),
                      ('grand_piano', S['palette_grand'])],
                     PALETTE, set_palette)
        _rebuild_seg(frm_lang_seg,
                     [('id', '🌐 ID'), ('en', '🌐 EN')],
                     LANG, set_lang)

        frm_body.configure(bg=C['BG'])
        frm_left.configure(bg=C['BG'])
        frm_right.configure(bg=C['BG'])

        lbl_folder_nav.configure(bg=C['BG'], fg=C['SUBTEXT'])

        frm_back_row.configure(bg=C['BG'])
        can_back = bool(nav_stack) or nav_folder[0] is not None
        btn_back.configure(bg=C['BG'],
                           fg=C['ACCENT'] if can_back else C['SUBTEXT'],
                           activebackground=C['PANEL'],
                           activeforeground=C['TEXT'])
        lbl_breadcrumb.configure(bg=C['BG'], fg=C['SUBTEXT'])

        folder_lb.configure(bg=C['ENTRY_BG'], fg=C['TEXT'],
                            selectbackground=C['ACCENT'], selectforeground=C['BG'])
        for i in range(folder_lb.size()):
            folder_lb.itemconfig(i, foreground=C['TEXT'])

        frm_folder_btns.configure(bg=C['BG'])
        btn_add.configure(bg=C['ACCENT'], fg=C['BG'],
                          activebackground=C['BTN_HOV'], activeforeground=C['BG'])
        btn_remove.configure(bg=C['PANEL'], fg=C['TEXT'],
                             activebackground=C['BTN_HOV'], activeforeground=C['TEXT'])

        frm_sep.configure(bg=C['SUBTEXT'])

        lbl_speed_section.configure(bg=C['BG'], fg=C['SUBTEXT'])
        lbl_speed.configure(bg=C['BG'], fg=C['ACCENT'])
        lbl_diff.configure(bg=C['BG'])
        slider_w.configure(bg=C['BG'], fg=C['TEXT'],
                           troughcolor=C['ACCENT'], activebackground=C['BTN_HOV'])
        lbl_speed_range.configure(bg=C['BG'], fg=C['SUBTEXT'])

        frm_frow.configure(bg=C['BG'])
        lbl_search_icon.configure(bg=C['BG'], fg=C['TEXT'])
        search_entry.configure(bg=C['ENTRY_BG'], fg=C['TEXT'],
                               insertbackground=C['TEXT'])
        lbl_count.configure(bg=C['BG'], fg=C['SUBTEXT'])

        frm_status_bar.configure(bg=C['ACCENT'])
        lbl_status.configure(bg=C['PANEL'], fg=C['SUBTEXT'])

        frm_bot.configure(bg=C['BG'])
        btn_play.configure(bg=C['ACCENT'], fg=C['BG'],
                           activebackground=C['BTN_HOV'], activeforeground=C['BG'])
        btn_cancel.configure(bg=C['PANEL'], fg=C['TEXT'],
                             activebackground=C['BTN_HOV'], activeforeground=C['TEXT'])

        tree.tag_configure('odd',  background=C['ENTRY_BG'], foreground=C['TEXT'])
        tree.tag_configure('even', background=C['ROW_ALT'],  foreground=C['TEXT'])

    # ── Header ─────────────────────────────────────────────
    frm_top = tk.Frame(root, bg=C['PANEL'], pady=8)
    frm_top.pack(fill='x')

    frm_header_left = tk.Frame(frm_top, bg=C['PANEL'])
    frm_header_left.pack(side='left', fill='both', expand=True)
    lbl_title = tk.Label(frm_header_left, text=S['header_title'],
                         bg=C['PANEL'], fg=C['ACCENT'],
                         font=('Segoe UI', 14, 'bold'))
    lbl_title.pack(anchor='w', padx=12)
    lbl_subtitle = tk.Label(frm_header_left, text=S['header_subtitle'],
                            bg=C['PANEL'], fg=C['SUBTEXT'],
                            font=('Segoe UI', 8))
    lbl_subtitle.pack(anchor='w', padx=12)

    frm_header_right = tk.Frame(frm_top, bg=C['PANEL'])
    frm_header_right.pack(side='right', padx=10, pady=4)

    frm_theme_seg = tk.Frame(frm_header_right, bg=C['BG'], padx=1, pady=1)
    frm_theme_seg.pack(side='right', padx=(6, 0))
    _rebuild_seg(frm_theme_seg,
                 [('dark', '🌙'), ('light', '☀️')],
                 THEME, set_theme)

    frm_palette_seg = tk.Frame(frm_header_right, bg=C['BG'], padx=1, pady=1)
    frm_palette_seg.pack(side='right', padx=(6, 0))
    _rebuild_seg(frm_palette_seg,
                 [('celestial', S['palette_celestial']),
                  ('grand_piano', S['palette_grand'])],
                 PALETTE, set_palette)

    frm_lang_seg = tk.Frame(frm_header_right, bg=C['BG'], padx=1, pady=1)
    frm_lang_seg.pack(side='right', padx=(6, 0))
    _rebuild_seg(frm_lang_seg,
                 [('id', '🌐 ID'), ('en', '🌐 EN')],
                 LANG, set_lang)

    # ── Body ───────────────────────────────────────────────
    frm_body = tk.Frame(root, bg=C['BG'])
    frm_body.pack(fill='both', expand=True, padx=10, pady=6)

    # ── Left panel: folder navigator ───────────────────────
    frm_left = tk.Frame(frm_body, bg=C['BG'], width=230)
    frm_left.pack(side='left', fill='y', padx=(0, 8))
    frm_left.pack_propagate(False)

    lbl_folder_nav = tk.Label(frm_left, text=S['folder_nav_panel'],
                              bg=C['BG'], fg=C['SUBTEXT'],
                              font=('Segoe UI', 9, 'bold'))
    lbl_folder_nav.pack(anchor='w')

    # Back row: [← Back] [breadcrumb path]
    frm_back_row = tk.Frame(frm_left, bg=C['BG'])
    frm_back_row.pack(fill='x', pady=(2, 0))

    btn_back = tk.Button(
        frm_back_row, text=S['back_btn'],
        command=on_back_click, relief='flat',
        bg=C['BG'], fg=C['SUBTEXT'],
        font=('Segoe UI', 8, 'bold'), padx=4, pady=2,
        cursor='hand2', bd=0, state='disabled',
        activebackground=C['PANEL'], activeforeground=C['TEXT'],
    )
    btn_back.pack(side='left')

    lbl_breadcrumb = tk.Label(
        frm_back_row, text='/',
        bg=C['BG'], fg=C['SUBTEXT'],
        font=('Segoe UI', 8), anchor='w',
    )
    lbl_breadcrumb.pack(side='left', padx=(4, 0), fill='x', expand=True)

    # Folder listbox
    folder_lb = tk.Listbox(
        frm_left,
        bg=C['ENTRY_BG'], fg=C['TEXT'],
        selectbackground=C['ACCENT'], selectforeground=C['BG'],
        font=('Segoe UI', 9), relief='flat', bd=0,
        activestyle='none',
    )
    folder_lb.pack(fill='both', expand=True, pady=4)

    # Add / Remove root-folder buttons
    frm_folder_btns = tk.Frame(frm_left, bg=C['BG'])
    frm_folder_btns.pack(fill='x')
    btn_add    = make_btn(frm_folder_btns, S['add_folder_btn'],    on_add_folder,    accent=True)
    btn_remove = make_btn(frm_folder_btns, S['remove_folder_btn'], on_remove_folder)
    btn_add.pack(   side='left', padx=(0, 4), fill='x', expand=True)
    btn_remove.pack(side='left',              fill='x', expand=True)

    # Divider
    frm_sep = tk.Frame(frm_left, bg=C['SUBTEXT'], height=1)
    frm_sep.pack(fill='x', pady=(10, 4))

    # Speed section
    lbl_speed_section = tk.Label(frm_left, text=S['speed_label'],
                                 bg=C['BG'], fg=C['SUBTEXT'],
                                 font=('Segoe UI', 9, 'bold'))
    lbl_speed_section.pack(anchor='w', pady=(0, 2))

    speed_var = tk.DoubleVar(value=1.0)

    def _speed_difficulty(v: float) -> tuple:
        s = STRINGS[LANG]
        if v <= 0.45: return s['diff_beginner']
        if v <= 0.65: return s['diff_learning']
        if v <= 0.85: return s['diff_relaxed']
        if v <= 1.05: return s['diff_normal']
        if v <= 1.50: return s['diff_advanced']
        if v <= 2.25: return s['diff_pro']
        return s['diff_master']

    lbl_speed = tk.Label(frm_left, text='1.00×',
                         bg=C['BG'], fg=C['ACCENT'],
                         font=('Segoe UI', 12, 'bold'))
    lbl_speed.pack()

    lbl_diff = tk.Label(frm_left,
                        text=_speed_difficulty(1.0)[0],
                        fg=_speed_difficulty(1.0)[1],
                        bg=C['BG'],
                        font=('Segoe UI', 9, 'bold'))
    lbl_diff.pack(pady=(0, 2))

    def on_speed(*_) -> None:
        v = speed_var.get()
        lbl_speed.config(text=f'{v:.2f}×')
        label, color = _speed_difficulty(v)
        lbl_diff.config(text=label, fg=color)

    slider_w = tk.Scale(
        frm_left, variable=speed_var, from_=0.25, to=3.0, resolution=0.05,
        orient='horizontal', bg=C['BG'], fg=C['TEXT'],
        troughcolor=C['ACCENT'], activebackground=C['BTN_HOV'],
        highlightthickness=0, showvalue=False,
        command=on_speed, length=200,
    )
    slider_w.pack()

    lbl_speed_range = tk.Label(frm_left, text=S['speed_range'],
                               bg=C['BG'], fg=C['SUBTEXT'],
                               font=('Segoe UI', 7))
    lbl_speed_range.pack()

    # ── Right panel: music list ─────────────────────────────
    frm_right = tk.Frame(frm_body, bg=C['BG'])
    frm_right.pack(side='left', fill='both', expand=True)

    # Search row
    frm_frow = tk.Frame(frm_right, bg=C['BG'])
    frm_frow.pack(fill='x', pady=(0, 6))

    lbl_search_icon = tk.Label(frm_frow, text='🔍',
                               bg=C['BG'], fg=C['TEXT'],
                               font=('Segoe UI', 11))
    lbl_search_icon.pack(side='left')

    search_var   = tk.StringVar()
    search_entry = tk.Entry(
        frm_frow, textvariable=search_var,
        bg=C['ENTRY_BG'], fg=C['TEXT'],
        insertbackground=C['TEXT'], relief='flat',
        font=('Segoe UI', 10), bd=6,
    )
    search_entry.pack(side='left', fill='x', expand=True, padx=6)

    lbl_count = tk.Label(frm_frow, text='0 file',
                         bg=C['BG'], fg=C['SUBTEXT'],
                         font=('Segoe UI', 8), width=14)
    lbl_count.pack(side='left')

    # Music Treeview — flat list, show='headings' (no tree column)
    cols = (S['col_no'], S['col_title'], S['col_size_kb'])
    tree = ttk.Treeview(frm_right, columns=cols, show='headings',
                        selectmode='browse')

    tree.heading(S['col_no'],      text=S['col_no'],      anchor='center',
                 command=lambda: sort_music('no'))
    tree.heading(S['col_title'],   text=S['col_title'],   anchor='w',
                 command=lambda: sort_music('name'))
    tree.heading(S['col_size_kb'], text=S['col_size_kb'], anchor='e',
                 command=lambda: sort_music('size'))

    tree.column(S['col_no'],      width=45,  stretch=False, anchor='center')
    tree.column(S['col_title'],   width=100, stretch=True,  anchor='w')
    tree.column(S['col_size_kb'], width=80,  stretch=False, anchor='e')

    vsb = ttk.Scrollbar(frm_right, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side='right', fill='y')
    tree.pack(fill='both', expand=True)

    # Accent stripe + status bar
    frm_status_bar = tk.Frame(frm_right, bg=C['ACCENT'], height=2)
    frm_status_bar.pack(fill='x', pady=(2, 0))

    lbl_status = tk.Label(frm_right, text=S['no_folder_selected'],
                          bg=C['PANEL'], fg=C['SUBTEXT'],
                          font=('Segoe UI', 8), anchor='w', padx=6)
    lbl_status.pack(fill='x')

    # ── Bottom buttons ─────────────────────────────────────
    frm_bot = tk.Frame(root, bg=C['BG'])
    frm_bot.pack(pady=8)
    btn_play   = make_btn(frm_bot, S['play_btn'],   lambda: confirm_select(), accent=True, width=20)
    btn_cancel = make_btn(frm_bot, S['cancel_btn'], lambda: cancel(),                      width=10)
    btn_play.pack(  side='left', padx=6)
    btn_cancel.pack(side='left')

    # ── Event bindings ─────────────────────────────────────
    search_entry.focus_set()
    search_var.trace_add('write', lambda *_: refresh_music())

    folder_lb.bind('<<ListboxSelect>>', on_folder_click)
    tree.bind('<Double-1>', lambda _: confirm_select())

    def on_tree_select(event) -> None:
        sel = tree.selection()
        if not sel:
            return
        vals = tree.item(sel[0], 'values')
        filename = vals[1] if len(vals) > 1 else ''
        if active_folder[0] and filename:
            full_path = os.path.join(active_folder[0], filename)
            try:
                st = os.stat(full_path)
                mt = datetime.datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M')
                lbl_status.config(
                    text=S['status_file'].format(path=full_path, size=st.st_size, mtime=mt)
                )
            except OSError:
                pass

    tree.bind('<<TreeviewSelect>>', on_tree_select)

    def on_key(event) -> None:
        if event.keysym == 'Return':
            confirm_select()
        elif event.keysym in ('Up', 'Down'):
            items = tree.get_children()
            if not items:
                return
            sel = tree.selection()
            cur = -1
            if sel:
                try:
                    cur = list(items).index(sel[0])
                except ValueError:
                    cur = -1
            if cur == -1:
                tree.selection_set(items[0])
                tree.see(items[0])
                return
            if event.keysym == 'Up' and cur > 0:
                new = items[cur - 1]
            elif event.keysym == 'Down' and cur < len(items) - 1:
                new = items[cur + 1]
            else:
                return
            tree.selection_set(new)
            tree.see(new)

    root.bind('<Key>', on_key)

    def confirm_select() -> None:
        sel = tree.selection()
        if not sel:
            messagebox.showwarning(S['warn_title'], S['warn_msg'])
            return
        vals     = tree.item(sel[0], 'values')
        filename = vals[1] if len(vals) > 1 else ''
        if active_folder[0] and filename:
            full_path = os.path.join(active_folder[0], filename)
            if os.path.isfile(full_path):
                selected_path[0] = full_path
                global playback_speed
                playback_speed = speed_var.get()
                save_config()
                root.after_idle(_close_window)
                return
        messagebox.showwarning(S['warn_title'], S['warn_msg'])

    def cancel() -> None:
        root.after_idle(_close_window)

    def on_close() -> None:
        selected_path[0] = None
        root.after_idle(_close_window)

    root.protocol('WM_DELETE_WINDOW', on_close)

    # ── Initial load ───────────────────────────────────────
    load_folder_pane(None)   # show root folders
    root.mainloop()

    # ── Evaluate result ────────────────────────────────────
    if selected_path[0] == '__RELOAD__':
        return '__RELOAD__'

    if selected_path[0] is None:
        print(STRINGS[LANG]['no_file_msg'])
        return None

    print(f"\nFile   : {selected_path[0]}")
    print(f"Speed  : {playback_speed}x")
    return parse_song_file(selected_path[0])


# ──────────────────────────────────────────────────────────
# Parse info nada dari infoTuple
# ──────────────────────────────────────────────────────────
def floor_to_zero(value) -> 'float | None':
    return value if value and value > 0 else None


def parse_info() -> list:
    tempo = info_tuple[0]
    notes = [list(n) for n in info_tuple[2][1:]]
    i     = 0
    while i < len(notes):
        note = notes[i]
        if 'tempo' in note[1]:
            try:
                tempo = 60 / float(note[1].split('=')[1])
            except (ValueError, IndexError):
                pass
            notes.pop(i)
            continue
        if i < len(notes) - 1:
            next_note = notes[i + 1]
            note[0]   = (next_note[0] - note[0]) * tempo
        else:
            note[0] = 1.0
        i += 1
    return notes


# ──────────────────────────────────────────────────────────
# Playback Engine
# ──────────────────────────────────────────────────────────
def play_next_note(gen: int = 0) -> None:
    global stored_index, is_playing

    if gen != _play_gen:
        return

    notes = info_tuple[2]
    if not (is_playing and stored_index < len(notes)):
        if stored_index >= len(notes):
            is_playing   = False
            stored_index = 0
            print('\n=== Lagu selesai ===')
        return

    note_info = notes[stored_index]
    delay     = floor_to_zero(note_info[0])
    keys      = note_info[1]

    if keys[0] == '~':
        for key in keys[1:]:
            release_letter(key)
    else:
        for key in keys:
            press_letter(key)

    if '~' not in keys:
        safe_keys = keys.encode('ascii', errors='replace').decode('ascii')
        print(f'{(delay or 0):8.3f}s  {safe_keys}')

    stored_index += 1

    if delay:
        threading.Timer(delay / playback_speed, play_next_note, args=(gen,)).start()
    else:
        threading.Thread(target=play_next_note, args=(gen,), daemon=True).start()


# ──────────────────────────────────────────────────────────
# Hotkey handlers
# ──────────────────────────────────────────────────────────
def on_delete_press(event) -> bool:
    global is_playing, _play_gen
    is_playing = not is_playing
    _play_gen += 1
    gen        = _play_gen
    if is_playing:
        print('\n[PLAY] Playing...')
        threading.Thread(target=play_next_note, args=(gen,), daemon=True).start()
    else:
        print('\n[PAUSE] Paused.')
    return True


def on_home_press(event) -> None:
    global stored_index
    stored_index = max(0, stored_index - 10)
    print(f'[REWIND] --> nada #{stored_index}')


def on_end_press(event) -> None:
    global stored_index, is_playing, _play_gen
    limit = len(info_tuple[2])
    if stored_index + 10 >= limit:
        is_playing   = False
        _play_gen   += 1
        stored_index = 0
        print('[SKIP] Melampaui akhir lagu -> reset.')
    else:
        stored_index += 10
        print(f'[SKIP] --> nada #{stored_index}')


def on_insert_press(event) -> None:
    global stored_index, is_playing, _play_gen
    _play_gen   += 1
    stored_index = 0
    is_playing   = True
    gen          = _play_gen
    print('\n[RESTART] Memulai ulang dari awal...')
    threading.Thread(target=play_next_note, args=(gen,), daemon=True).start()


# ──────────────────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────────────────
def main() -> None:
    import keyboard
    global info_tuple, playback_speed, is_playing, _play_gen, stored_index

    load_config()

    keyboard.on_press_key('delete', on_delete_press)
    keyboard.on_press_key('home',   on_home_press)
    keyboard.on_press_key('end',    on_end_press)
    keyboard.on_press_key('insert', on_insert_press)

    show_splash()

    while True:
        result = process_file()

        if result == '__RELOAD__':
            continue

        if not result:
            break

        info_tuple = result
        parsed       = parse_info()
        info_tuple   = (info_tuple[0], info_tuple[1], parsed)
        stored_index = 0
        is_playing   = False
        _play_gen   += 1

        print()
        print('╔══════════════════════════════╗')
        print('║     Song Player - Ready      ║')
        print('╠══════════════════════════════╣')
        print('║  DELETE  → Play / Pause      ║')
        print('║  HOME    → Rewind  (−10)     ║')
        print('║  END     → Skip    (+10)     ║')
        print('║  INSERT  → Restart dari awal ║')
        print('╠══════════════════════════════╣')
        print('║  Enter   → Pilih lagu lain   ║')
        print('║  Ctrl+C  → Keluar            ║')
        print('╚══════════════════════════════╝')
        print(f'\n  Total nada : {len(info_tuple[2])}')
        print(f'  Kecepatan  : {playback_speed}×\n')

        try:
            input('Menunggu perintah...\n')
        except KeyboardInterrupt:
            break
        finally:
            is_playing = False
            _play_gen += 1

    print('\nKeluar.')


if __name__ == '__main__':
    main()
