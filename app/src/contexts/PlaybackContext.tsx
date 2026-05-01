import {
  createContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import type { PlaybackState } from '../types';
import { api, onPlaybackState, onPlaybackTick, onPlaybackDone } from '../lib/tauri';

const DEFAULT_STATE: PlaybackState = {
  is_playing: false,
  index: 0,
  total: 0,
  speed: 1.0,
  song_path: null,
};

export interface PlaybackActions {
  loadSong: (path: string) => Promise<void>;
  play: () => Promise<void>;
  pause: () => Promise<void>;
  toggle: () => Promise<void>;
  seek: (delta: number) => Promise<void>;
  restart: () => Promise<void>;
  setSpeed: (s: number) => Promise<void>;
}

const NOOP_ACTIONS: PlaybackActions = {
  loadSong: async () => {},
  play: async () => {},
  pause: async () => {},
  toggle: async () => {},
  seek: async () => {},
  restart: async () => {},
  setSpeed: async () => {},
};

// Two contexts so consumers can subscribe to *only* what they need.
// Components reading actions (e.g. App.tsx) won't re-render when index/speed
// change; components reading state (e.g. PlayerSheet) re-render at 60Hz
// max because the tick→state bridge below is rAF-throttled.
export const PlaybackStateContext = createContext<PlaybackState>(DEFAULT_STATE);
export const PlaybackActionsContext = createContext<PlaybackActions>(NOOP_ACTIONS);

export function PlaybackProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<PlaybackState>(DEFAULT_STATE);
  // Holds the most recent index reported by `playback:tick` between flushes.
  // The Rust side stopped emitting `playback:state` per note; the renderer is
  // responsible for pulling `index` out of the tick stream. We coalesce all
  // ticks within a frame into a single setState by deferring to rAF.
  const pendingIndexRef = useRef<number | null>(null);
  const flushScheduledRef = useRef(false);

  useEffect(() => {
    let unsubState: (() => void) | undefined;
    let unsubTick: (() => void) | undefined;
    let unsubDone: (() => void) | undefined;
    let cancelled = false;

    const flushIndex = () => {
      flushScheduledRef.current = false;
      const next = pendingIndexRef.current;
      if (next === null || cancelled) return;
      pendingIndexRef.current = null;
      setState((prev) => (prev.index === next ? prev : { ...prev, index: next }));
    };

    (async () => {
      try {
        setState(await api.getState());
      } catch {
        // Tauri runtime not ready (e.g. Vite dev preview in browser).
      }
      unsubState = await onPlaybackState((s) => {
        // Transition events (load/play/pause/seek/restart/done) are infrequent
        // and authoritative — apply immediately. Drop any pending tick-derived
        // index so the new authoritative state isn't overwritten next frame.
        pendingIndexRef.current = null;
        if (!cancelled) setState(s);
      });
      unsubTick = await onPlaybackTick(({ index }) => {
        pendingIndexRef.current = index + 1; // tick fires *before* index advances in Rust
        if (flushScheduledRef.current) return;
        flushScheduledRef.current = true;
        requestAnimationFrame(flushIndex);
      });
      unsubDone = await onPlaybackDone(() => {
        pendingIndexRef.current = null;
        if (!cancelled) {
          setState((prev) => ({ ...prev, is_playing: false, index: 0 }));
        }
      });
    })();
    return () => {
      cancelled = true;
      unsubState?.();
      unsubTick?.();
      unsubDone?.();
    };
  }, []);

  // Actions never change identity — wrapping in useMemo with [] keeps the
  // reference stable across renders so PlaybackActionsContext consumers
  // don't re-render when state changes.
  const actions = useMemo<PlaybackActions>(
    () => ({
      loadSong: async (path) => {
        const s = await api.loadSong(path);
        setState(s);
      },
      play: () => api.play(),
      pause: () => api.pause(),
      toggle: async () => {
        await api.toggle();
      },
      seek: async (d) => {
        await api.seek(d);
      },
      restart: () => api.restart(),
      setSpeed: (s) => api.setSpeed(s),
    }),
    []
  );

  return (
    <PlaybackActionsContext.Provider value={actions}>
      <PlaybackStateContext.Provider value={state}>
        {children}
      </PlaybackStateContext.Provider>
    </PlaybackActionsContext.Provider>
  );
}
