import threading
import src.constants as state
from src.keyboard_sim import press_letter, release_letter


def floor_to_zero(value) -> 'float | None':
    return value if value and value > 0 else None


def parse_info() -> list:
    tempo = state.info_tuple[0]
    notes = [list(n) for n in state.info_tuple[2][1:]]
    i = 0
    while i < len(notes):
        note = notes[i]
        if 'tempo' in note[1]:
            try:
                tempo = 60 / float(note[1].split('=')[1])
            except (ValueError, IndexError):
                pass
            notes.pop(i)
            continue
        if i < len(notes) - 1:
            note[0] = (notes[i + 1][0] - note[0]) * tempo
        else:
            note[0] = 1.0
        i += 1
    return notes


def play_next_note(gen: int = 0) -> None:
    if gen != state._play_gen:
        return
    notes = state.info_tuple[2]
    if not (state.is_playing and state.stored_index < len(notes)):
        if state.stored_index >= len(notes):
            state.is_playing = False
            state.stored_index = 0
            print('\n=== Lagu selesai ===')
        return
    note_info = notes[state.stored_index]
    delay = floor_to_zero(note_info[0])
    keys  = note_info[1]
    if keys[0] == '~':
        for key in keys[1:]:
            release_letter(key)
    else:
        for key in keys:
            press_letter(key)
    if '~' not in keys:
        safe = keys.encode('ascii', errors='replace').decode('ascii')
        print(f'{(delay or 0):8.3f}s  {safe}')
    state.stored_index += 1
    if delay:
        threading.Timer(delay / state.playback_speed, play_next_note, args=(gen,)).start()
    else:
        threading.Thread(target=play_next_note, args=(gen,), daemon=True).start()
