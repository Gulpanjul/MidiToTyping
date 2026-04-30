import tkinter as tk
import src.constants as state

_GITHUB_URL = 'https://github.com/Gulpanjul/MidiToTyping'


def _open_github(_event=None):
    import webbrowser
    webbrowser.open(_GITHUB_URL)

_INFO_CONTENT = {
    'id': (
        "playSong — MIDI Auto-Player\n"
        "─────────────────────────────────────\n"
        "Versi      :  {version}\n"
        "Dirilis    :  {date}\n\n"
        "Dibuat oleh  :  {author}\n"
        "Dibantu AI   :  {ai}\n"
        "GitHub       :  {github}\n\n"
        "Stack    :  Python 3.12+  ·  Tkinter  ·  mido  ·  keyboard\n"
        "Platform :  Windows (global keyboard hook)\n\n"
        "Kontrol Saat Bermain\n"
        "─────────────────────────────────────\n"
        "  DELETE    →  Play / Pause\n"
        "  HOME      →  Mundur 10 note\n"
        "  END       →  Maju 10 note\n"
        "  INSERT    →  Restart dari awal"
    ),
    'en': (
        "playSong — MIDI Auto-Player\n"
        "─────────────────────────────────────\n"
        "Version    :  {version}\n"
        "Released   :  {date}\n\n"
        "Made by      :  {author}\n"
        "AI-Assisted  :  {ai}\n"
        "GitHub       :  {github}\n\n"
        "Stack    :  Python 3.12+  ·  Tkinter  ·  mido  ·  keyboard\n"
        "Platform :  Windows (global keyboard hook)\n\n"
        "Playback Controls\n"
        "─────────────────────────────────────\n"
        "  DELETE    →  Play / Pause\n"
        "  HOME      →  Rewind 10 notes\n"
        "  END       →  Skip 10 notes\n"
        "  INSERT    →  Restart from beginning"
    ),
}


def show_info_popup(root, C, S) -> None:
    popup = tk.Toplevel(root)
    popup.title(S['info_title'])
    popup.configure(bg=C['BG'])
    popup.resizable(False, False)
    popup.grab_set()

    content = _INFO_CONTENT[state.LANG].format(
        version=state.APP_VERSION, date=state.APP_DATE,
        author=state.APP_AUTHOR,  ai=state.APP_AI, github=state.APP_GITHUB,
    )
    tk.Label(popup, text=content, bg=C['BG'], fg=C['TEXT'],
             font=('Consolas', 9), justify='left', padx=24, pady=20).pack()
    tk.Frame(popup, bg=C['SUBTEXT'], height=1).pack(fill='x', padx=24)
    lbl_gh = tk.Label(popup, text=state.APP_GITHUB, bg=C['BG'], fg=C['ACCENT'],
                      font=('Segoe UI', 8, 'underline'), cursor='hand2', pady=8)
    lbl_gh.pack()
    lbl_gh.bind('<Button-1>', _open_github)
    tk.Button(
        popup, text='OK', command=popup.destroy, relief='flat',
        bg=C['ACCENT'], fg=C['BG'], font=('Segoe UI', 9, 'bold'),
        padx=20, pady=5, cursor='hand2', bd=0,
        activebackground=C['BTN_HOV'], activeforeground=C['BG'],
    ).pack(pady=(0, 16))

    popup.update_idletasks()
    pw, ph = popup.winfo_reqwidth(), popup.winfo_reqheight()
    rx, ry = root.winfo_x(), root.winfo_y()
    rw, rh = root.winfo_width(), root.winfo_height()
    popup.geometry(f'{pw}x{ph}+{rx + (rw - pw) // 2}+{ry + (rh - ph) // 2}')
