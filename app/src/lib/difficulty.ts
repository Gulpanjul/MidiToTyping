import type { StringsBundle, DiffEntry } from '../i18n/strings';

// Difficulty bands ported verbatim from legacy/src/gui/folder_pane.py:59-66.
// Used by both the sidebar speed slider (FolderPane) and the in-player speed
// slider (PlayerSheet) to keep their labels in sync.
export function difficultyFor(speed: number, S: StringsBundle): DiffEntry {
  if (speed <= 0.45) return S.diff_beginner;
  if (speed <= 0.65) return S.diff_learning;
  if (speed <= 0.85) return S.diff_relaxed;
  if (speed <= 1.05) return S.diff_normal;
  if (speed <= 1.5) return S.diff_advanced;
  if (speed <= 2.25) return S.diff_pro;
  return S.diff_master;
}
