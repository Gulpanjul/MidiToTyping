import os
import tkinter as tk
from tkinter import ttk
import src.constants as state


def _scan_flat(folder: str) -> list:
    try:
        names = sorted([f for f in os.listdir(folder)
                        if f.lower().endswith(state.SUPPORTED_EXTENSIONS)], key=str.lower)
    except OSError:
        return []
    def _entry(n):
        p = os.path.join(folder, n)
        try:    return {'path': p, 'name': n, 'size': os.stat(p).st_size}
        except OSError: return {'path': p, 'name': n, 'size': 0}
    return [_entry(n) for n in names]

def init_music_logic(ctx: dict) -> None:

    def refresh_music() -> None:
        tree, C, S = ctx['tree'], ctx['C'], ctx['S']
        for item in tree.get_children(): tree.delete(item)
        ctx['music_files'].clear()
        folder = ctx['active_folder'][0]
        if not folder or not os.path.isdir(folder):
            ctx['lbl_count'].config(text='0 file')
            ctx['lbl_status'].config(text=S['no_folder_selected'])
            return
        raw = _scan_flat(folder)
        kw  = ctx['search_var'].get().lower()
        if kw:
            raw = [f for f in raw if kw in f['name'].lower()]
        sk, rev = ctx['sort_key_music'][0], ctx['sort_rev_music'][0]
        raw.sort(key=lambda f: f['size'] if sk == 'size' else f['name'].lower(), reverse=rev)
        ctx['music_files'].extend(raw)
        n_total = len(_scan_flat(folder)) if kw else len(raw)
        for i, f in enumerate(raw, 1):
            tag = 'odd' if i % 2 else 'even'
            tree.insert('', tk.END, iid=f'music_{i}',
                        values=(i, f['name'], f'{max(1, f["size"] // 1024)} KB'), tags=(tag,))
        tree.tag_configure('odd',  background=C['ENTRY_BG'], foreground=C['TEXT'])
        tree.tag_configure('even', background=C['ROW_ALT'],  foreground=C['TEXT'])
        n   = len(raw)
        lbl = S['file_count_fmt'].format(shown=n, total=n_total) if kw else S['file_count_all'].format(total=n)
        ctx['lbl_count'].config(text=lbl)
        ctx['lbl_status'].config(text=S['no_folder_selected'] if n == 0 else f'  {n} file')

    def sort_music(key: str) -> None:
        if ctx['sort_key_music'][0] == key:
            ctx['sort_rev_music'][0] = not ctx['sort_rev_music'][0]
        else:
            ctx['sort_key_music'][0] = key
            ctx['sort_rev_music'][0] = False
        refresh_music()

    ctx['refresh_music'] = refresh_music
    ctx['sort_music']    = sort_music


def build_music_pane(ctx: dict) -> None:
    C, S = ctx['C'], ctx['S']
    frm_right = tk.Frame(ctx['frm_body'], bg=C['BG'])
    frm_right.pack(side='left', fill='both', expand=True)
    frm_frow = tk.Frame(frm_right, bg=C['BG'])
    frm_frow.pack(fill='x', pady=(0, 6))
    tk.Label(frm_frow, text='🔍', bg=C['BG'], fg=C['TEXT'],
             font=('Segoe UI', 11)).pack(side='left')
    search_var = tk.StringVar()
    search_entry = tk.Entry(frm_frow, textvariable=search_var, bg=C['ENTRY_BG'],
                            fg=C['TEXT'], insertbackground=C['TEXT'],
                            relief='flat', font=('Segoe UI', 10), bd=6)
    search_entry.pack(side='left', fill='x', expand=True, padx=6)
    lbl_count = tk.Label(frm_frow, text='0 file', bg=C['BG'], fg=C['SUBTEXT'],
                         font=('Segoe UI', 8), width=14)
    lbl_count.pack(side='left')
    no, ti, sz = S['col_no'], S['col_title'], S['col_size_kb']
    tree = ttk.Treeview(frm_right, columns=(no, ti, sz), show='headings', selectmode='browse')
    for col, anch, w, stretch, key in [
        (no, 'center', 45,  False, 'no'),
        (ti, 'w',      100, True,  'name'),
        (sz, 'e',      80,  False, 'size'),
    ]:
        tree.heading(col, text=col, anchor=anch, command=lambda k=key: ctx['sort_music'](k))
        tree.column(col, width=w, stretch=stretch, anchor=anch)
    vsb = ttk.Scrollbar(frm_right, orient='vertical', command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side='right', fill='y')
    tree.pack(fill='both', expand=True)
    frm_status_bar = tk.Frame(frm_right, bg=C['BORDER'], height=1)
    frm_status_bar.pack(fill='x', pady=(2, 0))
    lbl_status = tk.Label(frm_right, text=S['no_folder_selected'], bg=C['PANEL'],
                          fg=C['SUBTEXT'], font=('Segoe UI', 8), anchor='w', padx=6)
    lbl_status.pack(fill='x')
    ctx.update({
        'frm_right': frm_right, 'frm_frow': frm_frow, 'search_var': search_var,
        'search_entry': search_entry, 'lbl_count': lbl_count,
        'tree': tree, 'vsb': vsb, 'frm_status_bar': frm_status_bar, 'lbl_status': lbl_status,
    })
    search_var.trace_add('write', lambda *_: ctx['refresh_music']())
