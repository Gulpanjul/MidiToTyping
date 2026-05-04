import tkinter as tk
from tkinter import ttk
import src.constants as state
from src.strings import STRINGS
from src.themes import THEMES


def show_splash() -> None:
    C = THEMES[state.PALETTE][state.THEME]
    S = STRINGS[state.LANG]

    splash = tk.Tk()
    splash.overrideredirect(True)
    w, h = 460, 260
    sw, sh = splash.winfo_screenwidth(), splash.winfo_screenheight()
    splash.geometry(f'{w}x{h}+{(sw - w) // 2}+{(sh - h) // 2}')
    splash.configure(bg=C['BORDER'])
    splash.attributes('-topmost', True)

    inner = tk.Frame(splash, bg=C['BG'])
    inner.pack(fill='both', expand=True, padx=1, pady=1)

    # Content area
    content = tk.Frame(inner, bg=C['BG'])
    content.pack(fill='both', expand=True, padx=32, pady=20)

    tk.Label(content, text='🎵', bg=C['BG'], fg=C['ACCENT'],
             font=('Segoe UI Emoji', 44)).pack(pady=(4, 6))
    tk.Label(content, text='Song Auto-Player', bg=C['BG'], fg=C['TEXT'],
             font=('Segoe UI', 17, 'bold')).pack()
    tk.Label(content, text=S['splash_subtitle'], bg=C['BG'], fg=C['SUBTEXT'],
             font=('Segoe UI', 9)).pack(pady=(4, 16))

    # Progress bar
    sty = ttk.Style(splash)
    sty.theme_use('clam')
    sty.configure('Splash.Horizontal.TProgressbar',
                  troughcolor=C['ENTRY_BG'], background=C['ACCENT'],
                  bordercolor=C['BG'], lightcolor=C['ACCENT'], darkcolor=C['ACCENT'])
    pb = ttk.Progressbar(content, style='Splash.Horizontal.TProgressbar',
                         orient='horizontal', length=340, mode='determinate')
    pb.pack()
    tk.Label(content, text=S['splash_loading'], bg=C['BG'], fg=C['SUBTEXT'],
             font=('Segoe UI', 8)).pack(pady=(6, 0))


    steps = 40
    interval = 2000 // steps

    def _animate(step: int = 0) -> None:
        if step <= steps:
            pb['value'] = step * (100 / steps)
            splash.after(interval, _animate, step + 1)
        else:
            splash.destroy()

    splash.after(0, _animate)
    splash.mainloop()
