import { useEffect, useRef, useState } from 'react';
import { Dialog } from './ui/Dialog';
import { Button } from './ui/Button';
import { useConfig } from '../hooks/useConfig';
import { usePlayback } from '../hooks/usePlayback';
import { STRINGS, fmt } from '../i18n/strings';
import { onPlaybackTick } from '../lib/tauri';

interface Props {
  open: boolean;
  onClose: () => void;
  onPickAnother: () => void;
  songName: string;
}

interface LogLine {
  index: number;
  key: string;
}

const MAX_LOG_LINES = 200;

export function PlayerSheet({ open, onClose, onPickAnother, songName }: Props) {
  const { config } = useConfig();
  const { state, toggle } = usePlayback();
  const S = STRINGS[config.lang];
  const [log, setLog] = useState<LogLine[]>([]);
  const logRef = useRef<HTMLDivElement | null>(null);

  // Subscribe to playback:tick events while popup is open.
  // Mirrors src/playback.py:52 -- print(f'{delay}s  {keys}') for each press.
  // Releases (~prefix) are filtered out to match the Python "if '~' not in keys" guard.
  useEffect(() => {
    if (!open) return;
    setLog([]);
    let unsub: (() => void) | undefined;
    (async () => {
      unsub = await onPlaybackTick(({ index, key }) => {
        if (key.startsWith('~')) return;
        setLog((prev) => {
          const next = [...prev, { index, key }];
          return next.length > MAX_LOG_LINES ? next.slice(-MAX_LOG_LINES) : next;
        });
      });
    })();
    return () => {
      unsub?.();
    };
  }, [open]);

  // Auto-scroll log to bottom on new entries (mirrors txt.see('end') in player_popup.py:80).
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [log]);

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
        <div
          ref={logRef}
          className="h-48 bg-[var(--entry-bg)] rounded p-2 overflow-y-auto font-mono text-[11px] text-[var(--text)] border border-[var(--border)]"
        >
          {log.length === 0 ? (
            <div className="text-[var(--subtext)] italic">
              {state.is_playing ? '...' : '—'}
            </div>
          ) : (
            log.map((line, i) => (
              <div key={`${line.index}-${i}`} className="whitespace-pre">
                {String(line.index + 1).padStart(5, ' ')}  {line.key}
              </div>
            ))
          )}
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
