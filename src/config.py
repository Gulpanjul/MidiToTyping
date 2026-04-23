import os
import sys
import json
import pathlib
import src.constants as state


def _config_path() -> str:
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = str(pathlib.Path(__file__).parent.parent)
    return os.path.join(base, 'playSong_config.json')


def load_config() -> None:
    try:
        with open(_config_path(), 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        if cfg.get('lang') in ('id', 'en'):
            state.LANG = cfg['lang']
        if cfg.get('theme') in ('dark', 'light'):
            state.THEME = cfg['theme']
        if cfg.get('palette') in ('celestial', 'grand_piano'):
            state.PALETTE = cfg['palette']
        if isinstance(cfg.get('folders'), list):
            state.folder_history[:] = [p for p in cfg['folders'] if isinstance(p, str)]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass


def save_config() -> None:
    try:
        with open(_config_path(), 'w', encoding='utf-8') as f:
            json.dump({
                'lang'   : state.LANG,
                'theme'  : state.THEME,
                'palette': state.PALETTE,
                'folders': list(state.folder_history),
            }, f, indent=2, ensure_ascii=False)
    except OSError:
        pass
