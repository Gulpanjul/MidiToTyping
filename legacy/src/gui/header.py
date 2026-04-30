import tkinter as tk
import src.constants as state
from src.gui.widgets import rebuild_seg, rebuild_seg_icons
from src.gui.icons import moon, sun, info as info_icon, make_icon_button
from src.gui.info_popup import show_info_popup


def palette_items(S: dict) -> list:
    return [
        ('celestial',   S['palette_celestial']),
        ('grand_piano', S['palette_grand']),
    ]


def theme_icon_items() -> list:
    return [('dark', moon), ('light', sun)]


def build_header(ctx: dict) -> None:
    root, C, S = ctx['root'], ctx['C'], ctx['S']

    frm_top = tk.Frame(root, bg=C['PANEL'])
    frm_top.pack(fill='x')

    frm_left = tk.Frame(frm_top, bg=C['PANEL'])
    frm_left.pack(side='left', fill='both', expand=True, padx=(16, 0), pady=12)
    lbl_title = tk.Label(frm_left, text=S['header_title'], bg=C['PANEL'],
                         fg=C['TEXT'], font=('Segoe UI', 14, 'bold'))
    lbl_title.pack(anchor='w')
    lbl_subtitle = tk.Label(frm_left, text=S['header_subtitle'], bg=C['PANEL'],
                            fg=C['SUBTEXT'], font=('Segoe UI', 8))
    lbl_subtitle.pack(anchor='w')

    frm_right = tk.Frame(frm_top, bg=C['PANEL'])
    frm_right.pack(side='right', padx=12, pady=12)

    def _seg(parent):
        f = tk.Frame(parent, bg=C['ENTRY_BG'], padx=1, pady=1)
        f.pack(side='right', padx=(4, 0))
        return f

    frm_theme_seg = _seg(frm_right)
    rebuild_seg_icons(frm_theme_seg, theme_icon_items(), state.THEME, ctx['set_theme'], C)

    frm_palette_seg = _seg(frm_right)
    rebuild_seg(frm_palette_seg, palette_items(S), state.PALETTE, ctx['set_palette'], C)

    frm_lang_seg = _seg(frm_right)
    rebuild_seg(frm_lang_seg, [('id', 'ID'), ('en', 'EN')],
                state.LANG, ctx['set_lang'], C)

    btn_info = make_icon_button(
        frm_right, info_icon,
        lambda: show_info_popup(root, C, S),
        bg=C['PANEL'], color=C['SUBTEXT'], hover=C['BTN_HOV'],
        size=16, pad_x=6, pad_y=4,
    )
    btn_info.pack(side='right', padx=(4, 0))

    frm_border = tk.Frame(root, bg=C['BORDER'], height=1)
    frm_border.pack(fill='x')

    ctx.update({
        'frm_top': frm_top, 'frm_header_left': frm_left, 'frm_header_right': frm_right,
        'lbl_title': lbl_title, 'lbl_subtitle': lbl_subtitle,
        'frm_theme_seg': frm_theme_seg, 'frm_palette_seg': frm_palette_seg,
        'frm_lang_seg': frm_lang_seg, 'btn_info': btn_info,
        'frm_accent': frm_border,
    })
