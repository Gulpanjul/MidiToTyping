import src.constants as state
from src.themes import THEMES
from src.gui.widgets import rebuild_seg, rebuild_seg_icons
from src.gui.header import palette_items, theme_icon_items
from src.gui.icons import retint, search as _sicon


def repaint(ctx: dict) -> None:
    C = ctx['C']
    C.clear()
    C.update(THEMES[state.PALETTE][state.THEME])
    S, sty = ctx['S'], ctx['style']

    sty.configure('Treeview',
                  background=C['ENTRY_BG'], foreground=C['TEXT'],
                  fieldbackground=C['ENTRY_BG'], rowheight=26, font=('Segoe UI', 9))
    sty.configure('Treeview.Heading',
                  background=C['PANEL'], foreground=C['SUBTEXT'],
                  font=('Segoe UI', 8, 'bold'), relief='flat')
    sty.map('Treeview', background=[('selected', C['ACCENT'])],
            foreground=[('selected', C['BG'])])
    sty.configure('TScrollbar', background=C['PANEL'], troughcolor=C['BG'], arrowcolor=C['TEXT'])

    ctx['root'].configure(bg=C['BG'])
    ctx['frm_top'].configure(bg=C['PANEL'])
    ctx['frm_header_left'].configure(bg=C['PANEL'])
    ctx['frm_header_right'].configure(bg=C['PANEL'])
    ctx['lbl_title'].configure(bg=C['PANEL'], fg=C['TEXT'])
    ctx['lbl_subtitle'].configure(bg=C['PANEL'], fg=C['SUBTEXT'])

    retint(ctx['btn_info'], C['SUBTEXT'], bg=C['PANEL'], hover=C['BTN_HOV'])

    for frm in (ctx['frm_theme_seg'], ctx['frm_palette_seg'], ctx['frm_lang_seg']):
        frm.configure(bg=C['ENTRY_BG'])
    rebuild_seg_icons(ctx['frm_theme_seg'], theme_icon_items(), state.THEME, ctx['set_theme'], C)
    rebuild_seg(ctx['frm_palette_seg'], palette_items(S), state.PALETTE, ctx['set_palette'], C)
    rebuild_seg(ctx['frm_lang_seg'], [('id', 'ID'), ('en', 'EN')],
                state.LANG, ctx['set_lang'], C)

    ctx['frm_body'].configure(bg=C['BG'])
    ctx['frm_left'].configure(bg=C['BG'])
    ctx['frm_right'].configure(bg=C['BG'])
    ctx['lbl_folder_nav'].configure(bg=C['BG'], fg=C['SUBTEXT'])
    ctx['frm_back_row'].configure(bg=C['BG'])

    can_back = bool(ctx['nav_stack']) or ctx['nav_folder'][0] is not None
    retint(ctx['btn_back'], C['TEXT'] if can_back else C['SUBTEXT'],
           bg=C['BG'], hover=C['ENTRY_BG'])
    ctx['lbl_breadcrumb'].configure(bg=C['BG'], fg=C['SUBTEXT'])
    ctx['folder_lb'].configure(bg=C['ENTRY_BG'], fg=C['TEXT'],
                               selectbackground=C['ACCENT'], selectforeground=C['BG'])
    for i in range(ctx['folder_lb'].size()):
        ctx['folder_lb'].itemconfig(i, foreground=C['TEXT'])

    ctx['frm_folder_btns'].configure(bg=C['BG'])
    ahov = C.get('ACCENT_HOV', C['BTN_HOV'])
    retint(ctx['btn_add'],    C['BG'],   bg=C['ACCENT'], hover=ahov)
    retint(ctx['btn_remove'], C['TEXT'], bg=C['PANEL'],  hover=C['BTN_HOV'])

    ctx['frm_sep'].configure(bg=C['BORDER'])
    ctx['lbl_speed_section'].configure(bg=C['BG'], fg=C['SUBTEXT'])
    ctx['lbl_speed'].configure(bg=C['BG'], fg=C['ACCENT'])
    ctx['lbl_diff'].configure(bg=C['BG'])
    ctx['slider_w'].configure(bg=C['BG'], fg=C['SUBTEXT'],
                              troughcolor=C['ENTRY_BG'], activebackground=C['BTN_HOV'])
    ctx['lbl_speed_range'].configure(bg=C['BG'], fg=C['SUBTEXT'])

    ctx['frm_frow'].configure(bg=C['BG'])
    if 'cvs_search' in ctx:
        ctx['cvs_search'].configure(bg=C['BG'])
        ctx['cvs_search'].delete('icon')
        _sicon(ctx['cvs_search'], C['SUBTEXT'], 16, 'icon')
        ctx['cvs_search'].move('icon', 1, 1)
    ctx['search_entry'].configure(bg=C['ENTRY_BG'], fg=C['TEXT'], insertbackground=C['TEXT'])
    ctx['lbl_count'].configure(bg=C['BG'], fg=C['SUBTEXT'])
    ctx['frm_status_bar'].configure(bg=C['BORDER'])
    ctx['lbl_status'].configure(bg=C['PANEL'], fg=C['SUBTEXT'])

    ctx['frm_bot'].configure(bg=C['BG'])
    ctx['btn_play'].configure(bg=C['ACCENT'], fg=C['BG'],
                              activebackground=ahov, activeforeground=C['BG'])
    retint(ctx['btn_cancel'], C['TEXT'], bg=C['PANEL'], hover=C['BTN_HOV'])
    ctx['tree'].tag_configure('odd',  background=C['ENTRY_BG'], foreground=C['TEXT'])
    ctx['tree'].tag_configure('even', background=C['ROW_ALT'],  foreground=C['TEXT'])
    ctx['frm_accent'].configure(bg=C['BORDER'])
