export type Lang = 'id' | 'en';
export type Theme = 'dark' | 'light';
export type Palette = 'celestial' | 'grand_piano';

export interface Config {
  lang: Lang;
  theme: Theme;
  palette: Palette;
  folders: string[];
}

export interface NoteEvent {
  delay_secs: number;
  keys: string;
}

export interface NoteSchedule {
  initial_tempo_bpm: number;
  events: NoteEvent[];
}

export interface PlaybackState {
  is_playing: boolean;
  index: number;
  total: number;
  speed: number;
  song_path: string | null;
}

export interface MidiFile {
  name: string;
  size: number;
  path: string;
}

export type HotkeyName = 'play_pause' | 'rewind' | 'skip' | 'restart';
