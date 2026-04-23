import src.constants as state

_ALLOWED = frozenset(
    'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    '0123456789'
    '!@#$%^&*()_+{}|:"<>?'
    "`~-=[]\\;',./ "
)


def is_shifted(char: str) -> bool:
    ascii_val = ord(char)
    if 65 <= ascii_val <= 90:
        return True
    return char in '!@#$%^&*()_+{}|:"<>?'


def _safe(letter: str) -> bool:
    return len(letter) == 1 and letter in _ALLOWED


def press_letter(letter: str) -> None:
    if not _safe(letter):
        return
    import keyboard
    if is_shifted(letter):
        if letter in state.CONVERSION_CASES:
            letter = state.CONVERSION_CASES[letter]
        keyboard.release(letter.lower())
        keyboard.press('left shift')
        keyboard.press(letter.lower())
        keyboard.release('left shift')
    else:
        keyboard.release(letter)
        keyboard.press(letter)


def release_letter(letter: str) -> None:
    if not _safe(letter):
        return
    import keyboard
    if is_shifted(letter):
        if letter in state.CONVERSION_CASES:
            letter = state.CONVERSION_CASES[letter]
        keyboard.release(letter.lower())
    else:
        keyboard.release(letter)
