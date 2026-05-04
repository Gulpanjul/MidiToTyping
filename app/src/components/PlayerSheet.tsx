import { useEffect, useRef, useState } from 'react';
import {
  Play,
  Pause,
  Music2,
  Activity,
  Gauge,
  Hash,
  Rewind,
  FastForward,
  RotateCcw,
} from 'lucide-react';
import { Dialog } from './ui/Dialog';
import { Button } from './ui/Button';
import { Slider } from './ui/Slider';
import { MarqueeText } from './ui/MarqueeText';
import { useConfig } from '../hooks/useConfig';
import { usePlaybackActions, usePlaybackState } from '../hooks/usePlayback';
import { STRINGS } from '../i18n/strings';
import { onPlaybackTick } from '../lib/tauri';
import { difficultyFor } from '../lib/difficulty';

interface Props {
  open: boolean;
  /** Triggered by Esc key or X button — pauses playback and returns to song browser.
   *  App-level exit is now done via the title bar close button only. */
  onClose: () => void;
  songName: string;
}

interface LogLine {
  index: number;
  key: string;
  /** ms held; null while still pressed (or for keys whose release we never see) */
  durationMs: number | null;
  /** performance.now() at press — needed to compute durationMs on release. */
  startMs: number;
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

export function PlayerSheet({ open, onClose, songName }: Props) {
  const { config } = useConfig();
  const state = usePlaybackState();
  const { toggle, seek, restart, setSpeed } = usePlaybackActions();
  const S = STRINGS[config.lang];
  const lang = config.lang;
  // Log lines live in a mutable ref so press/release events run in O(1) without
  // queueing a setState per tick. Re-renders are coalesced to one per animation
  // frame via `logTick`, so dense MIDIs (50+ notes/sec) no longer back up the
  // React render queue and the duration `ms` updates are visible immediately.
  const linesRef = useRef<LogLine[]>([]);
  // Stack-per-character of LogLine *references* — release events pop the line
  // they refer to and mutate `durationMs` directly, so there's no array scan.
  const pressStacksRef = useRef(new Map<string, LogLine[]>());
  const flushScheduledRef = useRef(false);
  const [logTick, setLogTick] = useState(0);
  const logRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) {
      // Reset on close so the next song starts with a clean slate.
      linesRef.current = [];
      pressStacksRef.current.clear();
      return;
    }
    linesRef.current = [];
    pressStacksRef.current.clear();
    setLogTick((t) => t + 1);

    let unsub: (() => void) | undefined;
    let cancelled = false;

    const requestFlush = () => {
      if (flushScheduledRef.current) return;
      flushScheduledRef.current = true;
      requestAnimationFrame(() => {
        flushScheduledRef.current = false;
        if (!cancelled) setLogTick((t) => t + 1);
      });
    };

    (async () => {
      unsub = await onPlaybackTick(({ index, key }) => {
        const now = performance.now();
        if (key.startsWith('~')) {
          // Release: pop the most recent unresolved press line per char and
          // patch durationMs in place. No array scan, no setState.
          for (const ch of key.slice(1)) {
            const stack = pressStacksRef.current.get(ch);
            if (!stack || stack.length === 0) continue;
            const line = stack.pop()!;
            if (line.durationMs === null) {
              line.durationMs = Math.round(now - line.startMs);
            }
          }
          requestFlush();
          return;
        }
        // Press: append a new line, push its reference onto each chord
        // char's stack so the matching release is O(1).
        const line: LogLine = { index, key, durationMs: null, startMs: now };
        linesRef.current.push(line);
        if (linesRef.current.length > MAX_LOG_LINES) {
          linesRef.current.splice(0, linesRef.current.length - MAX_LOG_LINES);
        }
        for (const ch of key) {
          let stack = pressStacksRef.current.get(ch);
          if (!stack) {
            stack = [];
            pressStacksRef.current.set(ch, stack);
          }
          stack.push(line);
        }
        requestFlush();
      });
    })();

    return () => {
      cancelled = true;
      unsub?.();
    };
  }, [open]);

  // Auto-scroll log to bottom whenever a flush ran.
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logTick]);

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
            <MarqueeText
              text={songName || '—'}
              className="text-sm font-medium mt-0.5"
            />
          </div>
        </div>

        {/* Stats row — speed moved into the dedicated control block below. */}
        <div className="flex items-center gap-4 text-[11px]">
          <div className="flex items-center gap-1.5 text-[var(--subtext)]">
            <Hash size={11} />
            <span className="font-mono tabular-nums text-[var(--text)]">
              {state.index}
            </span>
            <span>/</span>
            <span className="font-mono tabular-nums">{state.total}</span>
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

        {/* Speed control — same range/step as the sidebar slider, kept in
            sync via the shared playback context. Difficulty label mirrors
            FolderPane so users get consistent feedback wherever they adjust. */}
        {(() => {
          const diff = difficultyFor(state.speed, S);
          return (
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-[var(--subtext)]">
                  <Gauge size={11} />
                  {S.speed_label}
                </div>
                <div className="flex items-center gap-2 text-[11px]">
                  <span
                    className="font-semibold"
                    style={{ color: diff.color }}
                  >
                    {diff.label}
                  </span>
                  <span className="font-mono text-[var(--accent)] tabular-nums">
                    {state.speed.toFixed(2)}×
                  </span>
                </div>
              </div>
              <Slider
                min={0.25}
                max={3.0}
                step={0.05}
                value={state.speed}
                onChange={(v) => setSpeed(v)}
              />
              <div className="flex justify-between text-[9px] text-[var(--subtext)]/70 mt-0.5 font-mono">
                <span>0.25×</span>
                <span>3.00×</span>
              </div>
            </div>
          );
        })()}

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
            {linesRef.current.length === 0 ? (
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
              linesRef.current.map((line, i) => {
                const durStr =
                  line.durationMs === null
                    ? '   ···'
                    : line.durationMs < 1000
                      ? `${String(line.durationMs).padStart(4, ' ')}ms`
                      : `${(line.durationMs / 1000).toFixed(2)}s `;
                return (
                  <div key={`${line.index}-${i}`} className="whitespace-pre tabular-nums">
                    <span className="text-[var(--subtext)]">
                      {String(line.index + 1).padStart(5, ' ')}
                    </span>
                    <span className="text-[var(--accent)]">  {line.key}</span>
                    <span className="text-[var(--subtext)]">  {durStr}</span>
                  </div>
                );
              })
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

        {/* Transport row — Play/Pause + rewind/skip/restart for keyboards
            without HOME/END/INSERT keys (e.g. 65% / TKL-no-nav / laptops). */}
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
          <Button
            variant="secondary"
            size="md"
            onClick={() => seek(-10)}
            aria-label={lang === 'id' ? 'Mundur 10 nada (HOME)' : 'Rewind 10 notes (HOME)'}
            title={lang === 'id' ? 'Mundur 10 nada (HOME)' : 'Rewind 10 notes (HOME)'}
            className="gap-1.5 px-3"
          >
            <Rewind size={14} fill="currentColor" />
            <span className="font-mono text-[11px]">−10</span>
          </Button>
          <Button
            variant="secondary"
            size="md"
            onClick={() => seek(10)}
            aria-label={lang === 'id' ? 'Maju 10 nada (END)' : 'Skip 10 notes (END)'}
            title={lang === 'id' ? 'Maju 10 nada (END)' : 'Skip 10 notes (END)'}
            className="gap-1.5 px-3"
          >
            <span className="font-mono text-[11px]">+10</span>
            <FastForward size={14} fill="currentColor" />
          </Button>
          <Button
            variant="secondary"
            size="md"
            onClick={() => restart()}
            aria-label={lang === 'id' ? 'Mulai ulang (INSERT)' : 'Restart (INSERT)'}
            title={lang === 'id' ? 'Mulai ulang (INSERT)' : 'Restart (INSERT)'}
            className="gap-1.5 px-3"
          >
            <RotateCcw size={14} />
          </Button>
        </div>
      </div>
    </Dialog>
  );
}
