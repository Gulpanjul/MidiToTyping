import { invoke } from '@tauri-apps/api/core';
import { listen, type UnlistenFn } from '@tauri-apps/api/event';
import type { Config, MidiFile, NoteSchedule, PlaybackState, HotkeyName } from '../types';

export const api = {
  listMidisInFolder: (path: string) => invoke<MidiFile[]>('list_midis_in_folder', { path }),
  parseMidi: (path: string) => invoke<NoteSchedule>('parse_midi', { path }),
  loadSong: (path: string) => invoke<PlaybackState>('load_song', { path }),
  play: () => invoke<void>('play'),
  pause: () => invoke<void>('pause'),
  toggle: () => invoke<boolean>('toggle'),
  seek: (delta: number) => invoke<number>('seek', { delta }),
  restart: () => invoke<void>('restart'),
  setSpeed: (speed: number) => invoke<void>('set_speed', { speed }),
  getState: () => invoke<PlaybackState>('get_state'),
  getConfig: () => invoke<Config>('get_config'),
  setConfig: (cfg: Config) => invoke<void>('set_config', { cfg }),
  isPlaybackSupported: () => invoke<boolean>('is_playback_supported'),
};

export function onPlaybackState(cb: (s: PlaybackState) => void): Promise<UnlistenFn> {
  return listen<PlaybackState>('playback:state', (e) => cb(e.payload));
}
export function onPlaybackTick(cb: (t: { index: number; key: string }) => void): Promise<UnlistenFn> {
  return listen<{ index: number; key: string }>('playback:tick', (e) => cb(e.payload));
}
export function onPlaybackDone(cb: () => void): Promise<UnlistenFn> {
  return listen<null>('playback:done', () => cb());
}
export function onHotkey(cb: (which: HotkeyName) => void): Promise<UnlistenFn> {
  return listen<{ which: HotkeyName }>('hotkey:fired', (e) => cb(e.payload.which));
}
