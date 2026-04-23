import tkinter as tk

FONT_BTN = ('Segoe UI', 9)
FONT_SEG = ('Segoe UI', 8)


def make_btn(parent, text, cmd, C, accent=False, width=None):
    kw = {'width': width} if width else {}
    bg  = C['ACCENT'] if accent else C['PANEL']
    fg  = C['BG']     if accent else C['TEXT']
    hov = C.get('ACCENT_HOV', C['BTN_HOV']) if accent else C['BTN_HOV']
    b = tk.Button(
        parent, text=text, command=cmd, relief='flat',
        bg=bg, fg=fg, font=FONT_BTN,
        padx=12, pady=6, cursor='hand2', bd=0,
        activebackground=hov, activeforeground=fg,
        **kw,
    )
    b.bind('<Enter>', lambda _: b.config(bg=hov))
    b.bind('<Leave>', lambda _: b.config(bg=bg))
    return b


def make_seg_btn(parent, text, active, cmd, C):
    bg  = C['ACCENT'] if active else C['PANEL']
    fg  = C['BG']     if active else C['TEXT']
    hov = C.get('ACCENT_HOV', C['BTN_HOV']) if active else C['BTN_HOV']
    b = tk.Button(
        parent, text=text, command=cmd, relief='flat',
        bg=bg, fg=fg,
        font=FONT_SEG,           # FIXED: same font always, no bold/normal switch
        padx=10, pady=4, cursor='hand2', bd=0,
        activebackground=hov, activeforeground=fg,
    )
    b.bind('<Enter>', lambda _: b.config(bg=hov))
    b.bind('<Leave>', lambda _: b.config(bg=bg))
    return b


def rebuild_seg(frame, items, cur_val, cmd_fn, C) -> None:
    for child in frame.winfo_children():
        child.destroy()
    for val, lbl in items:
        make_seg_btn(frame, lbl, cur_val == val,
                     lambda v=val: cmd_fn(v), C).pack(side='left', padx=1)
