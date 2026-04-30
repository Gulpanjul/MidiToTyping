import os
import sys
import tkinter as tk
from tkinter import ttk
import src.constants as state
from src.strings import STRINGS
from src.themes import THEMES
from src.config import save_config
from src.gui._parse_handler import safe_parse
from src.gui.header import build_header
from src.gui.folder_nav import init_folder_nav
from src.gui.folder_pane import build_folder_pane
from src.gui.music_pane import init_music_logic, build_music_pane
from src.gui.bottom import build_bottom
from src.gui.repaint import repaint as _repaint


def process_file() -> 'tuple | str | None':
    S = STRINGS[state.LANG]
    C = dict(THEMES[state.PALETTE][state.THEME])

    root = tk.Tk()
    root.title(S['window_title'])
    root.geometry('860x600')
    root.minsize(680, 480)
    root.configure(bg=C['BG'])

    style = ttk.Style(root)
    style.theme_use('clam')

    ctx: dict = {
        'root': root, 'C': C, 'S': S, 'style': style,
        'selected_path': [None],
        'nav_folder': [None], 'nav_stack': [], 'active_folder': [None],
        'display_folders': [], 'music_files': [],
        'sort_key_music': ['name'], 'sort_rev_music': [False],
    }

    def close_window():
        root.quit()
        root.destroy()

    def set_lang(lang: str) -> None:
        if state.LANG == lang:
            return
        state.LANG = lang
        save_config()
        ctx['selected_path'][0] = '__RELOAD__'
        root.after_idle(close_window)

    def set_theme(theme: str) -> None:
        if state.THEME == theme:
            return
        state.THEME = theme
        save_config()
        _repaint(ctx)

    def set_palette(palette: str) -> None:
        if state.PALETTE == palette:
            return
        state.PALETTE = palette
        save_config()
        _repaint(ctx)

    ctx.update(close_window=close_window, set_lang=set_lang,
               set_theme=set_theme, set_palette=set_palette)

    if not state.folder_history:
        base = os.path.dirname(sys.executable if getattr(sys, 'frozen', False)
                               else os.path.abspath(__file__ + '/../../..'))
        state.folder_history.append(os.path.normpath(base))

    style.configure('Treeview', background=C['ENTRY_BG'], foreground=C['TEXT'],
                    fieldbackground=C['ENTRY_BG'], rowheight=26, font=('Segoe UI', 9))
    style.configure('Treeview.Heading', background=C['PANEL'], foreground=C['SUBTEXT'],
                    font=('Segoe UI', 8, 'bold'), relief='flat')
    style.map('Treeview', background=[('selected', C['ACCENT'])],
              foreground=[('selected', C['BG'])])
    style.configure('TScrollbar', background=C['PANEL'], troughcolor=C['BG'],
                    arrowcolor=C['TEXT'])

    build_header(ctx)
    init_folder_nav(ctx)
    build_folder_pane(ctx)
    init_music_logic(ctx)
    build_music_pane(ctx)
    build_bottom(ctx)

    ctx['load_folder_pane'](None)
    root.mainloop()

    if ctx['selected_path'][0] == '__RELOAD__':
        return '__RELOAD__'
    if ctx['selected_path'][0] is None:
        print(S['no_file_msg'])
        return None

    state.current_song = ctx['selected_path'][0]
    print(f"\nFile   : {ctx['selected_path'][0]}")
    print(f"Speed  : {state.playback_speed}x")
    return safe_parse(ctx['selected_path'][0], S)
