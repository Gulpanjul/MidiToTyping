import { useEffect } from 'react';
import { Dialog } from './ui/Dialog';
import { Button } from './ui/Button';
import { useConfig } from '../hooks/useConfig';
import { usePlayback } from '../hooks/usePlayback';
import { STRINGS, fmt } from '../i18n/strings';

interface Props {
  open: boolean;
  onClose: () => void;
  onPickAnother: () => void;
  songName: string;
}

export function PlayerSheet({ open, onClose, onPickAnother, songName }: Props) {
  const { config } = useConfig();
  const { state, toggle } = usePlayback();
  const S = STRINGS[config.lang];

  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === ' ') {
        e.preventDefault();
        toggle();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, toggle]);

  return (
    <Dialog open={open} onClose={onClose} title={S.player_title}>
      <div className="space-y-3 text-sm">
        <div className="text-[var(--subtext)]">{fmt(S.player_ready, { name: songName })}</div>
        <div className="text-xs text-[var(--subtext)]">
          {fmt(S.player_stats, { n: String(state.total), s: state.speed.toFixed(2) })}
        </div>
        <div className="text-xs text-[var(--subtext)]">{S.player_hotkeys}</div>
        <div className="h-2 bg-[var(--entry-bg)] rounded overflow-hidden">
          <div
            className="h-full bg-[var(--accent)] transition-all"
            style={{ width: `${state.total ? (state.index / state.total) * 100 : 0}%` }}
          />
        </div>
        <div className="flex gap-2 pt-2">
          <Button onClick={() => toggle()} className="flex-1">
            {state.is_playing ? S.player_pause : S.player_play}
          </Button>
          <Button variant="secondary" onClick={onPickAnother}>
            {S.player_pick}
          </Button>
          <Button variant="ghost" onClick={onClose}>
            {S.player_exit}
          </Button>
        </div>
      </div>
    </Dialog>
  );
}
