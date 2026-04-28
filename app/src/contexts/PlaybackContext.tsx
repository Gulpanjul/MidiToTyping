import { createContext, useEffect, useState, type ReactNode } from 'react';
import type { PlaybackState } from '../types';
import { api, onPlaybackState, onPlaybackDone } from '../lib/tauri';

const DEFAULT: PlaybackState = {
  is_playing: false,
  index: 0,
  total: 0,
  speed: 1.0,
  song_path: null,
};

interface Ctx {
  state: PlaybackState;
  loadSong: (path: string) => Promise<void>;
  play: () => Promise<void>;
  pause: () => Promise<void>;
  toggle: () => Promise<void>;
  seek: (delta: number) => Promise<void>;
  restart: () => Promise<void>;
  setSpeed: (s: number) => Promise<void>;
}

export const PlaybackContext = createContext<Ctx>({
  state: DEFAULT,
  loadSong: async () => {},
  play: async () => {},
  pause: async () => {},
  toggle: async () => {},
  seek: async () => {},
  restart: async () => {},
  setSpeed: async () => {},
});

export function PlaybackProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<PlaybackState>(DEFAULT);

  useEffect(() => {
    let unsubState: (() => void) | undefined;
    let unsubDone: (() => void) | undefined;
    (async () => {
      try {
        setState(await api.getState());
      } catch {
        // ignore (Tauri not yet ready)
      }
      unsubState = await onPlaybackState(setState);
      unsubDone = await onPlaybackDone(() => {
        setState((prev) => ({ ...prev, is_playing: false, index: 0 }));
      });
    })();
    return () => {
      unsubState?.();
      unsubDone?.();
    };
  }, []);

  const ctx: Ctx = {
    state,
    loadSong: async (path) => {
      setState(await api.loadSong(path));
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
  };
  return <PlaybackContext.Provider value={ctx}>{children}</PlaybackContext.Provider>;
}
