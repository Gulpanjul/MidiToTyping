import type { Palette, Theme } from '../types';

export interface ColorSet {
  BG: string;
  PANEL: string;
  ACCENT: string;
  ACCENT_HOV: string;
  TEXT: string;
  SUBTEXT: string;
  ENTRY_BG: string;
  BTN_HOV: string;
  ROW_ALT: string;
  SEL_BG: string;
  BORDER: string;
}

export const THEMES: Record<Palette, Record<Theme, ColorSet>> = {
  celestial: {
    dark: {
      BG: '#09090B',
      PANEL: '#18181B',
      ACCENT: '#FAFAFA',
      ACCENT_HOV: '#D4D4D8',
      TEXT: '#FAFAFA',
      SUBTEXT: '#71717A',
      ENTRY_BG: '#27272A',
      BTN_HOV: '#27272A',
      ROW_ALT: '#111113',
      SEL_BG: '#3F3F46',
      BORDER: '#27272A',
    },
    light: {
      BG: '#FFFFFF',
      PANEL: '#F4F4F5',
      ACCENT: '#18181B',
      ACCENT_HOV: '#3F3F46',
      TEXT: '#09090B',
      SUBTEXT: '#71717A',
      ENTRY_BG: '#FFFFFF',
      BTN_HOV: '#D4D4D8',
      ROW_ALT: '#FAFAFA',
      SEL_BG: '#E4E4E7',
      BORDER: '#E4E4E7',
    },
  },
  grand_piano: {
    dark: {
      BG: '#020817',
      PANEL: '#0F172A',
      ACCENT: '#818CF8',
      ACCENT_HOV: '#6366F1',
      TEXT: '#F8FAFC',
      SUBTEXT: '#64748B',
      ENTRY_BG: '#1E293B',
      BTN_HOV: '#1E293B',
      ROW_ALT: '#050E1A',
      SEL_BG: '#312E81',
      BORDER: '#1E293B',
    },
    light: {
      BG: '#FFFFFF',
      PANEL: '#F8FAFC',
      ACCENT: '#6366F1',
      ACCENT_HOV: '#4F46E5',
      TEXT: '#0F172A',
      SUBTEXT: '#64748B',
      ENTRY_BG: '#FFFFFF',
      BTN_HOV: '#C7D2FE',
      ROW_ALT: '#F1F5F9',
      SEL_BG: '#E0E7FF',
      BORDER: '#E2E8F0',
    },
  },
};

const KEY_TO_VAR: Record<keyof ColorSet, string> = {
  BG: '--bg',
  PANEL: '--panel',
  ACCENT: '--accent',
  ACCENT_HOV: '--accent-hov',
  TEXT: '--text',
  SUBTEXT: '--subtext',
  ENTRY_BG: '--entry-bg',
  BTN_HOV: '--btn-hov',
  ROW_ALT: '--row-alt',
  SEL_BG: '--sel-bg',
  BORDER: '--border',
};

export function applyTheme(palette: Palette, theme: Theme) {
  const set = THEMES[palette][theme];
  const root = document.documentElement;
  (Object.keys(set) as (keyof ColorSet)[]).forEach((k) => {
    root.style.setProperty(KEY_TO_VAR[k], set[k]);
  });
  root.dataset.theme = theme;
  root.dataset.palette = palette;
}
