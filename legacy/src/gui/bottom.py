import os
import tkinter as tk
# datetime, messagebox imported lazily inside handlers
import src.constants as state
from src.gui.widgets import make_btn
from src.gui.icons import make_icon_button, x_mark


def build_bottom(ctx: dict) -> None:
    root, C, S = ctx['root'], ctx['C'], ctx['S']
    tree = ctx['tree']

    def confirm_select() -> None:
        sel = tree.selection()
        if not sel:
            from tkinter import messagebox
            messagebox.showwarning(S['warn_title'], S['warn_msg'])
            return
        vals = tree.item(sel[0], 'values')
        filename = vals[1] if len(vals) > 1 else ''
        if ctx['active_folder'][0] and filename:
            full_path = os.path.join(ctx['active_folder'][0], filename)
            if os.path.isfile(full_path):
                ctx['selected_path'][0] = full_path
                state.playback_speed = ctx['speed_var'].get()
                from src.config import save_config
                save_config()
                root.after_idle(ctx['close_window'])
                return
        from tkinter import messagebox
        messagebox.showwarning(S['warn_title'], S['warn_msg'])

    def on_tree_select(event) -> None:
        sel = tree.selection()
        if not sel:
            return
        vals = tree.item(sel[0], 'values')
        filename = vals[1] if len(vals) > 1 else ''
        if ctx['active_folder'][0] and filename:
            full_path = os.path.join(ctx['active_folder'][0], filename)
            try:
                import datetime
                st = os.stat(full_path)
                mt = datetime.datetime.fromtimestamp(st.st_mtime).strftime('%Y-%m-%d %H:%M')
                ctx['lbl_status'].config(
                    text=S['status_file'].format(path=full_path, size=st.st_size, mtime=mt))
            except OSError:
                pass

    def on_key(event) -> None:
        if event.keysym == 'Return':
            confirm_select()
            return
        if event.keysym not in ('Up', 'Down'):
            return
        items = tree.get_children()
        if not items:
            return
        sel = tree.selection()
        try:
            cur = list(items).index(sel[0]) if sel else -1
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

    frm_bot = tk.Frame(root, bg=C['BG'])
    frm_bot.pack(pady=10)
    btn_play = make_btn(frm_bot, S['play_btn'], confirm_select, C, accent=True, width=22)
    btn_cancel = make_icon_button(frm_bot, x_mark,
                                  lambda: root.after_idle(ctx['close_window']),
                                  bg=C['PANEL'], color=C['TEXT'], hover=C['BTN_HOV'],
                                  size=16, pad_x=10, pad_y=9)
    btn_play.pack(side='left', padx=6)
    btn_cancel.pack(side='left')

    def on_close() -> None:
        ctx['selected_path'][0] = None
        root.after_idle(ctx['close_window'])

    ctx['search_entry'].focus_set()
    tree.bind('<Double-1>', lambda _: confirm_select())
    tree.bind('<<TreeviewSelect>>', on_tree_select)
    root.bind('<Key>', on_key)
    root.protocol('WM_DELETE_WINDOW', on_close)

    ctx.update({
        'frm_bot': frm_bot, 'btn_play': btn_play, 'btn_cancel': btn_cancel,
        'confirm_select': confirm_select,
    })
