import { useEffect, useRef, useState } from 'react';
import {
  Play,
  Pause,
  ListMusic,
  LogOut,
  Music2,
  Activity,
  Gauge,
  Hash,
} from 'lucide-react';
import { Dialog } from './ui/Dialog';
import { Button } from './ui/Button';
import { useConfig } from '../hooks/useConfig';
import { usePlayback } from '../hooks/usePlayback';
import { STRINGS } from '../i18n/strings';
import { onPlaybackTick } from '../lib/tauri';

interface Props {
  open: boolean;
  /** Dialog dismissal (Esc / X / backdrop). Behaves the same as "Pilih Lagu Lain": pause + close. */
  onClose: () => void;
  /** "🎵 Pilih Lagu Lain" — pause + close popup, return to song browser. */
  onPickAnother: () => void;
  /** "✕ Keluar" — pause + close popup + close the app window (mirrors Python main loop break). */
  onExit: () => void;
  songName: string;
}

interface LogLine {
  index: number;
  key: string;
}

const MAX_LOG_LINES = 200;

// Strip leading symbol/whitespace from i18n labels so we can pair the text
// with a Lucide icon (e.g. "▶  Mainkan" -> "Mainkan").
function stripPrefix(s: string): string {
  return s.replace(/^[\+\-−×✕▶⏸🎵←]\s*/, '').trim();
}

const HOTKEY_CHIPS = [
  { key: 'DEL', id: 'Play / Jeda', en: 'Play / Pause' },
  { key: 'HOME', id: '−10', en: '−10' },
  { key: 'END', id: '+10', en: '+10' },
  { key: 'INS', id: 'Restart', en: 'Restart' },
];

export function PlayerSheet({ open, onClose, onPickAnother, onExit, songName }: Props) {
  const { config } = useConfig();
  const { state, toggle } = usePlayback();
  const S = STRINGS[config.lang];
  const lang = config.lang;
  const [log, setLog] = useState<LogLine[]>([]);
  const logRef = useRef<HTMLDivElement | null>(null);

  // Subscribe to playback:tick events while popup is open.
  // Mirrors src/playback.py:52 -- print(f'{delay}s  {keys}') for each press.
  // Releases (~prefix) are filtered out to match Python's "if '~' not in keys".
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

  // Auto-scroll log to bottom on new entries.
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

  const progress = state.total ? (state.index / state.total) * 100 : 0;

  return (
    <Dialog open={open} onClose={onClose} title={S.player_title} size="lg">
      <div className="space-y-4">
        {/* Now-playing card */}
        <div
          className={`flex items-start gap-3 p-3 rounded-lg border transition-all ${
            state.is_playing
              ? 'bg-[var(--accent)]/10 border-[var(--accent)]/30 shadow-[0_0_18px_-6px_var(--accent)]'
              : 'bg-[var(--entry-bg)]/40 border-[var(--border)]'
          }`}
        >
          <div
            className={`shrink-0 w-10 h-10 rounded-md flex items-center justify-center ${
              state.is_playing
                ? 'bg-[var(--accent)] text-[var(--bg)]'
                : 'bg-[var(--panel)] text-[var(--subtext)] border border-[var(--border)]'
            }`}
          >
            {state.is_playing ? <Activity size={18} /> : <Music2 size={18} />}
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-[10px] font-semibold uppercase tracking-wider text-[var(--subtext)]">
              {state.is_playing
                ? lang === 'id'
                  ? 'Sedang Dimainkan'
                  : 'Now Playing'
                : lang === 'id'
                  ? 'Siap Dimainkan'
                  : 'Ready to Play'}
            </div>
            <div className="text-sm font-medium truncate mt-0.5" title={songName}>
              {songName || '—'}
            </div>
          </div>
        </div>

        {/* Stats row */}
        <div className="flex items-center gap-4 text-[11px]">
          <div className="flex items-center gap-1.5 text-[var(--subtext)]">
            <Hash size={11} />
            <span className="font-mono tabular-nums text-[var(--text)]">
              {state.index}
            </span>
            <span>/</span>
            <span className="font-mono tabular-nums">{state.total}</span>
          </div>
          <div className="flex items-center gap-1.5 text-[var(--subtext)]">
            <Gauge size={11} />
            <span className="font-mono tabular-nums text-[var(--text)]">
              {state.speed.toFixed(2)}×
            </span>
          </div>
          <div className="ml-auto font-mono tabular-nums text-[var(--subtext)]">
            {progress.toFixed(0)}%
          </div>
        </div>

        {/* Progress bar */}
        <div className="h-1.5 bg-[var(--entry-bg)] rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-150 bg-[var(--accent)] ${
              state.is_playing ? 'shadow-[0_0_8px_var(--accent)]' : ''
            }`}
            style={{ width: `${progress}%` }}
          />
        </div>

        {/* Note log */}
        <div>
          <div className="flex items-center gap-1.5 mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-[var(--subtext)]">
            <Activity size={11} />
            {lang === 'id' ? 'Log Note' : 'Note Log'}
          </div>
          <div
            ref={logRef}
            className="h-44 bg-[var(--bg)]/60 rounded-md p-2.5 overflow-y-auto font-mono text-[11px] text-[var(--text)] border border-[var(--border)] leading-relaxed"
          >
            {log.length === 0 ? (
              <div className="text-[var(--subtext)] italic">
                {state.is_playing
                  ? lang === 'id'
                    ? 'Menunggu nada…'
                    : 'Waiting for notes…'
                  : lang === 'id'
                    ? 'Tekan Mainkan atau hotkey DELETE untuk mulai'
                    : 'Press Play or DELETE hotkey to start'}
              </div>
            ) : (
              log.map((line, i) => (
                <div key={`${line.index}-${i}`} className="whitespace-pre tabular-nums">
                  <span className="text-[var(--subtext)]">
                    {String(line.index + 1).padStart(5, ' ')}
                  </span>
                  <span className="text-[var(--accent)]">  {line.key}</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Hotkey legend */}
        <div className="flex items-center gap-1.5 flex-wrap text-[10px]">
          {HOTKEY_CHIPS.map((h) => (
            <div
              key={h.key}
              className="inline-flex items-center gap-1.5 px-2 py-1 rounded bg-[var(--entry-bg)]/60 border border-[var(--border)]"
            >
              <kbd className="px-1.5 py-0.5 text-[9px] font-mono font-semibold rounded bg-[var(--bg)] border border-[var(--border)] text-[var(--text)]">
                {h.key}
              </kbd>
              <span className="text-[var(--subtext)]">{lang === 'id' ? h.id : h.en}</span>
            </div>
          ))}
        </div>

        {/* Action buttons */}
        <div className="flex gap-2 pt-1">
          <Button
            onClick={() => toggle()}
            className="flex-1 gap-2"
            size="md"
          >
            {state.is_playing ? (
              <>
                <Pause size={15} fill="currentColor" />
                {stripPrefix(S.player_pause)}
              </>
            ) : (
              <>
                <Play size={15} fill="currentColor" />
                {stripPrefix(S.player_play)}
              </>
            )}
          </Button>
          <Button variant="secondary" onClick={onPickAnother} size="md" className="gap-2">
            <ListMusic size={14} />
            {stripPrefix(S.player_pick)}
          </Button>
          <Button variant="ghost" onClick={onExit} size="md" className="gap-2">
            <LogOut size={14} />
            {stripPrefix(S.player_exit)}
          </Button>
        </div>
      </div>
    </Dialog>
  );
}
