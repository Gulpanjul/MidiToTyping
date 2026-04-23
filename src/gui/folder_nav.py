import os
import tkinter as tk
# tkinter.filedialog imported lazily inside on_add_folder
import src.constants as state
from src.config import save_config


def init_folder_nav(ctx: dict) -> None:

    def _get_subdirs(path: str) -> list:
        try:
            return sorted(
                [os.path.join(path, d) for d in os.listdir(path)
                 if os.path.isdir(os.path.join(path, d))],
                key=lambda p: os.path.basename(p).lower(),
            )
        except OSError:
            return []

    def _breadcrumb() -> str:
        folder = ctx['nav_folder'][0]
        if folder is None:
            return '/'
        for root_f in state.folder_history:
            if folder == root_f or folder.startswith(root_f + os.sep):
                rel  = os.path.relpath(folder, root_f)
                base = os.path.basename(root_f) or root_f
                return base if rel == '.' else f'{base} › {rel.replace(os.sep, " › ")}'
        return os.path.basename(folder) or folder

    def load_folder_pane(folder=None) -> None:
        lb = ctx['folder_lb']
        lb.delete(0, tk.END)
        ctx['display_folders'].clear()
        ctx['nav_folder'][0] = folder
        items = list(state.folder_history) if folder is None else (_get_subdirs(folder) or [folder])
        ctx['display_folders'].extend(items)
        for path in items:
            lb.insert(tk.END, f'📁  {os.path.basename(path) or path}')
        for i in range(lb.size()):
            lb.itemconfig(i, foreground=ctx['C']['TEXT'])
        ctx['lbl_breadcrumb'].config(text=_breadcrumb())
        can_back = bool(ctx['nav_stack']) or folder is not None
        ctx['btn_back'].config(state='normal' if can_back else 'disabled',
                               fg=ctx['C']['ACCENT'] if can_back else ctx['C']['SUBTEXT'])
        ctx['btn_remove'].config(state='normal' if folder is None else 'disabled')

    def on_folder_click(event=None) -> None:
        sel = ctx['folder_lb'].curselection()
        if not sel or sel[0] >= len(ctx['display_folders']):
            return
        path = ctx['display_folders'][sel[0]]
        ctx['active_folder'][0] = path
        ctx['refresh_music']()
        if _get_subdirs(path):
            ctx['nav_stack'].append(ctx['nav_folder'][0])
            load_folder_pane(path)

    def on_back_click() -> None:
        prev = ctx['nav_stack'].pop() if ctx['nav_stack'] else None
        load_folder_pane(prev)
        ctx['active_folder'][0] = ctx['nav_folder'][0]
        ctx['refresh_music']()

    def on_add_folder() -> None:
        from tkinter import filedialog
        path = filedialog.askdirectory(parent=ctx['root'], title=ctx['S']['add_folder_dialog'])
        if path:
            path = os.path.normpath(path)
            if path not in state.folder_history:
                state.folder_history.append(path)
                save_config()
                if ctx['nav_folder'][0] is None:
                    load_folder_pane(None)

    def on_remove_folder() -> None:
        if ctx['nav_folder'][0] is not None:
            return
        sel = ctx['folder_lb'].curselection()
        if not sel or sel[0] >= len(ctx['display_folders']):
            return
        path = ctx['display_folders'][sel[0]]
        if path in state.folder_history:
            state.folder_history.remove(path)
            if ctx['active_folder'][0] == path:
                ctx['active_folder'][0] = None
                ctx['refresh_music']()
            save_config()
            load_folder_pane(None)

    ctx['load_folder_pane']  = load_folder_pane
    ctx['on_folder_click']   = on_folder_click
    ctx['on_back_click']     = on_back_click
    ctx['on_add_folder']     = on_add_folder
    ctx['on_remove_folder']  = on_remove_folder
