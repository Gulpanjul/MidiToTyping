import type { Lang } from '../types';

export interface DiffEntry {
  label: string;
  color: string;
}
export interface StringsBundle {
  splash_loading: string;
  splash_subtitle: string;
  window_title: string;
  header_title: string;
  header_subtitle: string;
  folder_nav_panel: string;
  back_btn: string;
  add_folder_btn: string;
  remove_folder_btn: string;
  add_folder_dialog: string;
  no_folder_selected: string;
  speed_label: string;
  speed_range: string;
  diff_beginner: DiffEntry;
  diff_learning: DiffEntry;
  diff_relaxed: DiffEntry;
  diff_normal: DiffEntry;
  diff_advanced: DiffEntry;
  diff_pro: DiffEntry;
  diff_master: DiffEntry;
  col_no: string;
  col_title: string;
  col_size_kb: string;
  file_count_fmt: string;
  file_count_all: string;
  status_file: string;
  play_btn: string;
  cancel_btn: string;
  warn_title: string;
  warn_msg: string;
  no_file_msg: string;
  mido_title: string;
  mido_msg: string;
  palette_celestial: string;
  palette_grand: string;
  info_btn: string;
  info_title: string;
  player_title: string;
  player_play: string;
  player_pause: string;
  player_pick: string;
  player_exit: string;
  player_hotkeys: string;
  player_ready: string;
  player_stats: string;
}

export const STRINGS: Record<Lang, StringsBundle> = {
  id: {
    splash_loading: 'Memuat aplikasi...',
    splash_subtitle: 'Auto-Player Piano · Sky & Piano Tiles',
    window_title: 'Song Player – Pilih File Lagu',
    header_title: '🎵  Song Auto-Player',
    header_subtitle: 'Pilih folder → pilih lagu → mainkan',
    folder_nav_panel: 'Navigasi Folder',
    back_btn: '← Kembali',
    add_folder_btn: '+ Tambah',
    remove_folder_btn: '− Hapus',
    add_folder_dialog: 'Pilih Folder Lagu',
    no_folder_selected: '  Pilih folder untuk melihat file lagu...',
    speed_label: 'Kecepatan Putar',
    speed_range: '0.25×  ──────  3.00×',
    diff_beginner: { label: 'Pemula', color: '#6BCB77' },
    diff_learning: { label: 'Belajar', color: '#74C0FC' },
    diff_relaxed: { label: 'Santai', color: '#A9C0D6' },
    diff_normal: { label: 'Normal', color: '#CDD6F4' },
    diff_advanced: { label: 'Mahir', color: '#FFA94D' },
    diff_pro: { label: 'Pro', color: '#FF6B6B' },
    diff_master: { label: 'Master', color: '#DA77F2' },
    col_no: 'No',
    col_title: 'Judul',
    col_size_kb: 'Ukuran',
    file_count_fmt: '{shown}/{total} file',
    file_count_all: '{total} file',
    status_file: '  {path}  |  {size} bytes  |  {mtime}',
    play_btn: '▶  Mainkan File Ini',
    cancel_btn: 'Batal',
    warn_title: 'Pilih File',
    warn_msg: 'Silakan pilih file dari daftar terlebih dahulu.',
    no_file_msg: 'Tidak ada file yang dipilih. Keluar.',
    mido_title: 'Mido Missing',
    mido_msg: "Library 'mido' tidak ditemukan.\nJalankan: pip install mido",
    palette_celestial: 'Zinc',
    palette_grand: 'Slate',
    info_btn: 'Info',
    info_title: 'Tentang Aplikasi',
    player_title: 'Song Player',
    player_play: '▶  Mainkan',
    player_pause: '⏸  Jeda',
    player_pick: '🎵  Pilih Lagu Lain',
    player_exit: '✕  Keluar',
    player_hotkeys: 'Hotkey: DEL=Play/Jeda · HOME=−10 · END=+10 · INSERT=Restart',
    player_ready: '[SIAP] {name}',
    player_stats: '  Total nada : {n}   ·   Kecepatan : {s}×',
  },
  en: {
    splash_loading: 'Loading application...',
    splash_subtitle: 'Piano Auto-Player · Sky & Piano Tiles',
    window_title: 'Song Player – Select Song File',
    header_title: '🎵  Song Auto-Player',
    header_subtitle: 'Select folder → choose song → play',
    folder_nav_panel: 'Folder Navigator',
    back_btn: '← Back',
    add_folder_btn: '+ Add',
    remove_folder_btn: '− Remove',
    add_folder_dialog: 'Select Song Folder',
    no_folder_selected: '  Select a folder on the left to view song files...',
    speed_label: 'Playback Speed',
    speed_range: '0.25×  ──────  3.00×',
    diff_beginner: { label: 'Beginner', color: '#6BCB77' },
    diff_learning: { label: 'Learning', color: '#74C0FC' },
    diff_relaxed: { label: 'Relaxed', color: '#A9C0D6' },
    diff_normal: { label: 'Normal', color: '#CDD6F4' },
    diff_advanced: { label: 'Advanced', color: '#FFA94D' },
    diff_pro: { label: 'Pro', color: '#FF6B6B' },
    diff_master: { label: 'Master', color: '#DA77F2' },
    col_no: 'No',
    col_title: 'Title',
    col_size_kb: 'Size',
    file_count_fmt: '{shown}/{total} files',
    file_count_all: '{total} files',
    status_file: '  {path}  |  {size} bytes  |  {mtime}',
    play_btn: '▶  Play This File',
    cancel_btn: 'Cancel',
    warn_title: 'Select File',
    warn_msg: 'Please select a file from the list first.',
    no_file_msg: 'No file selected. Exiting.',
    mido_title: 'Mido Missing',
    mido_msg: "Library 'mido' not found.\nRun: pip install mido",
    palette_celestial: 'Zinc',
    palette_grand: 'Slate',
    info_btn: 'Info',
    info_title: 'About',
    player_title: 'Song Player',
    player_play: '▶  Play',
    player_pause: '⏸  Pause',
    player_pick: '🎵  Pick Another Song',
    player_exit: '✕  Exit',
    player_hotkeys: 'Hotkeys: DEL=Play/Pause · HOME=−10 · END=+10 · INSERT=Restart',
    player_ready: '[READY] {name}',
    player_stats: '  Total notes : {n}   ·   Speed : {s}×',
  },
};

export function fmt(template: string, vars: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (_, k) => String(vars[k] ?? ''));
}
