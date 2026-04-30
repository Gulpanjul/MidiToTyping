import os
import sys
import pathlib
# tempfile imported lazily — only needed when converting .mid files


_SCALE = '1!2@34$5%6^78*9(0qQwWeErtTyYuiIoOpPasSdDfgGhHjJklLzZxcCvVbBnm'
_ALLOWED_KEYS = frozenset(_SCALE + '~')


class MidoNotAvailable(ImportError):
    pass


def _convert_midi_to_txt(filepath: str, txt_path: str) -> None:
    import mido
    mid              = mido.MidiFile(filepath)
    ticks_per_beat   = mid.ticks_per_beat
    merged           = mido.merge_tracks(mid.tracks)
    abs_ticks        = 0
    first_note_ticks = None
    lines            = []
    for msg in merged:
        abs_ticks += msg.time
        if msg.type == 'set_tempo':
            bpm      = round(60_000_000 / msg.tempo)
            beat_pos = abs_ticks / ticks_per_beat
            if first_note_ticks is not None:
                beat_pos = (abs_ticks - first_note_ticks) / ticks_per_beat
            lines.append(f"{beat_pos:.4f} tempo={bpm}")
        elif msg.type in ('note_on', 'note_off'):
            idx = msg.note - 36
            while idx >= len(_SCALE): idx -= 12
            while idx < 0:            idx += 12
            if first_note_ticks is None:
                first_note_ticks = abs_ticks
            beat_pos = (abs_ticks - first_note_ticks) / ticks_per_beat
            char     = _SCALE[idx]
            prefix   = '~' if (msg.type == 'note_off' or msg.velocity == 0) else ''
            lines.append(f"{beat_pos:.4f} {prefix}{char}")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def parse_song_file(filepath: str) -> tuple:
    _temp_file = None
    try:
        if filepath.lower().endswith(('.mid', '.midi')):
            try:
                import mido  # noqa: F401
            except ImportError as _e:
                raise MidoNotAvailable(str(_e)) from _e
            base = (os.path.dirname(sys.executable) if getattr(sys, 'frozen', False)
                    else str(pathlib.Path(__file__).parent.parent))
            import tempfile
            fd, txt_path = tempfile.mkstemp(prefix='~midi_', suffix='.txt', dir=base)
            os.close(fd)
            print(f"\n[MIDI] Membaca {filepath}\n       -> (temp) {txt_path}")
            _temp_file = txt_path
            _convert_midi_to_txt(filepath, txt_path)
            filepath = txt_path

        notes = []
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(None, 1)
                if len(parts) < 2:
                    continue
                try:
                    keys = parts[1].strip()
                    if not all(c in _ALLOWED_KEYS or c.startswith('tempo=')
                               for c in [keys] + list(keys)):
                        pass
                    notes.append([float(parts[0]), keys])
                except ValueError:
                    continue
        return (1.0, None, [[0.0, 'header']] + notes)
    finally:
        if _temp_file:
            try:
                os.remove(_temp_file)
            except OSError:
                pass
