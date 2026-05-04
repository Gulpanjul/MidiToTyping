# ============================================================
# File: playSong_clean.py
# Date: 2026-04-23
# Author: Gulpanjul
# AI-Assisted: Claude Code (Sonnet 4.6)
# ============================================================
import threading
import src.constants as state
from src.config import load_config
from src.playback import play_next_note, parse_info
from src.gui.splash import show_splash
# process_file + player_popup imported lazily in main()


def on_delete_press(event) -> bool:
    state.is_playing = not state.is_playing
    state._play_gen += 1
    gen = state._play_gen
    if state.is_playing:
        print('\n[PLAY] Playing...')
        threading.Thread(target=play_next_note, args=(gen,), daemon=True).start()
    else:
        print('\n[PAUSE] Paused.')
    return True


def on_home_press(event) -> None:
    state.stored_index = max(0, state.stored_index - 10)
    print(f'[REWIND] --> nada #{state.stored_index}')


def on_end_press(event) -> None:
    limit = len(state.info_tuple[2])
    if state.stored_index + 10 >= limit:
        state.is_playing  = False
        state._play_gen  += 1
        state.stored_index = 0
        print('[SKIP] Melampaui akhir lagu -> reset.')
    else:
        state.stored_index += 10
        print(f'[SKIP] --> nada #{state.stored_index}')


def on_insert_press(event) -> None:
    state._play_gen  += 1
    state.stored_index = 0
    state.is_playing   = True
    gen = state._play_gen
    print('\n[RESTART] Memulai ulang dari awal...')
    threading.Thread(target=play_next_note, args=(gen,), daemon=True).start()


def main() -> None:
    import keyboard
    load_config()
    for key, fn in [('delete', on_delete_press), ('home', on_home_press),
                    ('end', on_end_press), ('insert', on_insert_press)]:
        keyboard.on_press_key(key, fn)
    show_splash()
    from src.gui.process_file import process_file
    from src.gui.player_popup import show_player
    while True:
        result = process_file()
        if result == '__RELOAD__':
            continue
        if not result:
            break
        state.info_tuple   = result
        parsed             = parse_info()
        state.info_tuple   = (state.info_tuple[0], state.info_tuple[1], parsed)
        state.stored_index = 0
        state.is_playing   = False
        state._play_gen   += 1
        try:
            action = show_player(state.current_song)
        finally:
            state.is_playing = False
            state._play_gen += 1
        if action == 'exit':
            break

if __name__ == '__main__':
    main()
