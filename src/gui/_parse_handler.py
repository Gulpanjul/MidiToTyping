import sys
from tkinter import messagebox
import src.constants as state
from src.midi_parser import parse_song_file, MidoNotAvailable


def safe_parse(filepath: str, S: dict):
    try:
        return parse_song_file(filepath)
    except MidoNotAvailable as e:
        hint = ("Modul MIDI tidak ter-bundle.\nDownload ulang versi terbaru.\n\nDetail: "
                if state.LANG == 'id' else
                "MIDI module not bundled.\nPlease re-download.\n\nDetail: ")
        msg = (hint + str(e)) if getattr(sys, 'frozen', False) else S['mido_msg']
        messagebox.showerror(S['mido_title'], msg)
        return None
