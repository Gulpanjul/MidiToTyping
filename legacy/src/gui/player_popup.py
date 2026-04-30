import os, queue, sys, threading
import tkinter as tk
import src.constants as state
from src.strings import STRINGS
from src.themes import THEMES
from src.playback import play_next_note


class _Tap:
    """Dup writes to inner stream AND a thread-safe queue (for Tk poll)."""
    def __init__(self, inner, q): self._inner, self._q = inner, q
    def write(self, s):
        if self._inner is not None:
            try: self._inner.write(s)
            except Exception: pass
        try: self._q.put_nowait(s)
        except queue.Full: pass
    def flush(self):
        if self._inner is not None:
            try: self._inner.flush()
            except Exception: pass
    def isatty(self): return False


def show_player(song_path: str) -> str:
    """Show in-app player popup. Returns 'next' (pick another) or 'exit'."""
    C, S = THEMES[state.PALETTE][state.THEME], STRINGS[state.LANG]
    name = os.path.basename(song_path) if song_path else ''
    result = {'action': 'next'}

    root = tk.Tk()
    root.title(f'{S["player_title"]} — {name}')
    root.geometry('620x440'); root.minsize(460, 300); root.configure(bg=C['BG'])

    def refresh_label():
        btn_play.configure(text=S['player_pause'] if state.is_playing else S['player_play'])

    def on_play_pause():
        state.is_playing = not state.is_playing
        state._play_gen += 1
        gen = state._play_gen
        if state.is_playing:
            print('\n[PLAY] Playing...')
            threading.Thread(target=play_next_note, args=(gen,), daemon=True).start()
        else:
            print('\n[PAUSE] Paused.')
        refresh_label()

    def close(action: str):
        result['action'] = action
        state.is_playing = False
        state._play_gen += 1
        root.destroy()

    bar = tk.Frame(root, bg=C['BG']); bar.pack(fill='x', padx=12, pady=(12, 6))
    bkw = dict(relief='flat', cursor='hand2', padx=14, pady=8, borderwidth=0,
               bg=C['PANEL'], fg=C['TEXT'], activebackground=C['BTN_HOV'],
               activeforeground=C['TEXT'], font=('Segoe UI', 10))
    btn_play = tk.Button(bar, text=S['player_play'], command=on_play_pause, **bkw)
    btn_play.pack(side='left', padx=(0, 6))
    tk.Button(bar, text=S['player_pick'], command=lambda: close('next'), **bkw).pack(side='left', padx=6)
    tk.Button(bar, text=S['player_exit'], command=lambda: close('exit'), **bkw).pack(side='right', padx=(6, 0))

    tk.Label(root, text=S['player_hotkeys'], bg=C['BG'], fg=C['SUBTEXT'],
             font=('Segoe UI', 8), anchor='w').pack(fill='x', padx=14)
    tk.Frame(root, bg=C['BORDER'], height=1).pack(fill='x', padx=12, pady=(6, 0))

    txt = tk.Text(root, bg=C['PANEL'], fg=C['TEXT'], relief='flat', state='disabled',
                  wrap='word', borderwidth=0, font=('Consolas', 9), insertbackground=C['TEXT'])
    txt.pack(fill='both', expand=True, padx=12, pady=(8, 12))

    q: queue.Queue = queue.Queue(maxsize=4000)
    old_stdout = sys.stdout
    sys.stdout = _Tap(old_stdout, q)

    def poll():
        try:
            while True:
                s = q.get_nowait()
                txt.configure(state='normal'); txt.insert('end', s); txt.see('end')
                txt.configure(state='disabled')
        except queue.Empty:
            pass
        root.after(80, poll)
    poll()

    print(S['player_ready'].format(name=name))
    print(S['player_stats'].format(n=len(state.info_tuple[2]), s=state.playback_speed))

    root.protocol('WM_DELETE_WINDOW', lambda: close('next'))
    try:
        root.mainloop()
    finally:
        sys.stdout = old_stdout
    return result['action']
