import tkinter as tk
import src.constants as state
from src.gui.widgets import make_btn


def build_folder_pane(ctx: dict) -> None:
    root, C, S = ctx['root'], ctx['C'], ctx['S']

    frm_body = tk.Frame(root, bg=C['BG'])
    frm_body.pack(fill='both', expand=True, padx=12, pady=8)

    frm_left = tk.Frame(frm_body, bg=C['BG'], width=240)
    frm_left.pack(side='left', fill='y', padx=(0, 10))
    frm_left.pack_propagate(False)

    lbl_folder_nav = tk.Label(frm_left, text=S['folder_nav_panel'], bg=C['BG'],
                              fg=C['SUBTEXT'], font=('Segoe UI', 8, 'bold'))
    lbl_folder_nav.pack(anchor='w', pady=(0, 2))

    frm_back_row = tk.Frame(frm_left, bg=C['BG'])
    frm_back_row.pack(fill='x', pady=(2, 0))
    btn_back = tk.Button(
        frm_back_row, text=S['back_btn'], relief='flat', bg=C['BG'], fg=C['SUBTEXT'],
        font=('Segoe UI', 8, 'bold'), padx=4, pady=2, cursor='hand2', bd=0,
        state='disabled', activebackground=C['PANEL'], activeforeground=C['TEXT'],
        command=lambda: ctx['on_back_click'](),
    )
    btn_back.pack(side='left')
    lbl_breadcrumb = tk.Label(frm_back_row, text='/', bg=C['BG'], fg=C['SUBTEXT'],
                              font=('Segoe UI', 8), anchor='w')
    lbl_breadcrumb.pack(side='left', padx=(4, 0), fill='x', expand=True)

    folder_lb = tk.Listbox(frm_left, bg=C['ENTRY_BG'], fg=C['TEXT'],
                           selectbackground=C['ACCENT'], selectforeground=C['BG'],
                           font=('Segoe UI', 9), relief='flat', bd=0, activestyle='none')
    folder_lb.pack(fill='both', expand=True, pady=4)
    folder_lb.bind('<<ListboxSelect>>', lambda e: ctx['on_folder_click'](e))

    frm_folder_btns = tk.Frame(frm_left, bg=C['BG'])
    frm_folder_btns.pack(fill='x')
    btn_add    = make_btn(frm_folder_btns, S['add_folder_btn'],    lambda: ctx['on_add_folder'](),    C, accent=True)
    btn_remove = make_btn(frm_folder_btns, S['remove_folder_btn'], lambda: ctx['on_remove_folder'](), C)
    btn_add.pack(side='left', padx=(0, 4), fill='x', expand=True)
    btn_remove.pack(side='left', fill='x', expand=True)

    frm_sep = tk.Frame(frm_left, bg=C['BORDER'], height=1)
    frm_sep.pack(fill='x', pady=(10, 4))

    lbl_speed_section = tk.Label(frm_left, text=S['speed_label'], bg=C['BG'],
                                 fg=C['SUBTEXT'], font=('Segoe UI', 8, 'bold'))
    lbl_speed_section.pack(anchor='w', pady=(0, 2))

    speed_var = tk.DoubleVar(value=state.playback_speed)

    def _diff(v):
        s = S
        if v <= 0.45: return s['diff_beginner']
        if v <= 0.65: return s['diff_learning']
        if v <= 0.85: return s['diff_relaxed']
        if v <= 1.05: return s['diff_normal']
        if v <= 1.50: return s['diff_advanced']
        if v <= 2.25: return s['diff_pro']
        return s['diff_master']

    lbl_speed = tk.Label(frm_left, text=f'{state.playback_speed:.2f}×',
                         bg=C['BG'], fg=C['ACCENT'], font=('Segoe UI', 12, 'bold'))
    lbl_speed.pack()
    _d0_text, _d0_color = _diff(state.playback_speed)
    lbl_diff = tk.Label(frm_left, text=_d0_text, fg=_d0_color, bg=C['BG'],
                        font=('Segoe UI', 9, 'bold'))
    lbl_diff.pack(pady=(0, 2))

    def on_speed(*_):
        v = speed_var.get()
        lbl_speed.config(text=f'{v:.2f}×')
        label, color = _diff(v)
        lbl_diff.config(text=label, fg=color)

    slider_w = tk.Scale(frm_left, variable=speed_var, from_=0.25, to=3.0, resolution=0.05,
                        orient='horizontal', bg=C['BG'], fg=C['SUBTEXT'],
                        troughcolor=C['ENTRY_BG'], activebackground=C['BTN_HOV'],
                        highlightthickness=0, showvalue=False, command=on_speed, length=200)
    slider_w.pack()
    lbl_speed_range = tk.Label(frm_left, text=S['speed_range'], bg=C['BG'],
                               fg=C['SUBTEXT'], font=('Segoe UI', 7))
    lbl_speed_range.pack()

    ctx.update({
        'frm_body': frm_body, 'frm_left': frm_left, 'lbl_folder_nav': lbl_folder_nav,
        'frm_back_row': frm_back_row, 'btn_back': btn_back, 'lbl_breadcrumb': lbl_breadcrumb,
        'folder_lb': folder_lb, 'frm_folder_btns': frm_folder_btns,
        'btn_add': btn_add, 'btn_remove': btn_remove, 'frm_sep': frm_sep,
        'lbl_speed_section': lbl_speed_section, 'lbl_speed': lbl_speed,
        'lbl_diff': lbl_diff, 'slider_w': slider_w, 'lbl_speed_range': lbl_speed_range,
        'speed_var': speed_var,
    })
