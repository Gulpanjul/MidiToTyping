LANG:           str   = 'id'
THEME:          str   = 'dark'
PALETTE:        str   = 'celestial'
is_playing:     bool  = False
stored_index:   int   = 0
playback_speed: float = 1.0
info_tuple:     tuple = (1.0, None, [])
_play_gen:      int   = 0
folder_history: list  = []
current_song:   str   = ''

CONVERSION_CASES: dict = {
    '!': '1', '@': '2', '#': '3', '£': '3', '$': '4', '%': '5',
    '^': '6', '&': '7', '*': '8', '(': '9', ')': '0',
}
SUPPORTED_EXTENSIONS: tuple = ('.mid', '.midi')

APP_VERSION: str = '1.0.0'
APP_DATE:    str = '2026-04-21'
APP_AUTHOR:  str = 'Gulpanjul'
APP_GITHUB:  str = 'github.com/Gulpanjul/MidiToTyping'
APP_AI:      str = 'Claude Code (Sonnet 4.6)'
