import { useEffect, useMemo, useRef, useState } from 'react';
import { Search, Music2, FolderSearch, FileMusic } from 'lucide-react';
import { Input } from './ui/Input';
import { useConfig } from '../hooks/useConfig';
import { STRINGS, fmt } from '../i18n/strings';
import { api } from '../lib/tauri';
import type { MidiFile } from '../types';

interface Props {
  folder: string | null;
  selectedFile: MidiFile | null;
  onSelectFile: (f: MidiFile) => void;
  /** Triggered by Enter key or double-click on a row — selects + plays. */
  onPlayFile: (f: MidiFile) => void;
  /** Suppress arrow/Enter capture (e.g. when player popup is open). */
  disableNav?: boolean;
}

export function MusicPane({ folder, selectedFile, onSelectFile, onPlayFile, disableNav }: Props) {
  const { config } = useConfig();
  const S = STRINGS[config.lang];
  const [files, setFiles] = useState<MidiFile[]>([]);
  const [query, setQuery] = useState('');
  const [debounced, setDebounced] = useState('');

  useEffect(() => {
    if (!folder) {
      setFiles([]);
      return;
    }
    api
      .listMidisInFolder(folder)
      .then(setFiles)
      .catch(() => setFiles([]));
  }, [folder]);

  useEffect(() => {
    const t = setTimeout(() => setDebounced(query), 200);
    return () => clearTimeout(t);
  }, [query]);

  const filtered = useMemo(() => {
    if (!debounced) return files;
    const q = debounced.toLowerCase();
    return files.filter((f) => f.name.toLowerCase().includes(q));
  }, [files, debounced]);

  const rowRefs = useRef<Map<string, HTMLTableRowElement>>(new Map());

  // Keyboard navigation: ArrowUp/Down moves the selected song,
  // Enter triggers playback. We listen at window level but bail out when
  // the user is typing in an input/textarea (e.g. the search box).
  useEffect(() => {
    if (disableNav || !folder || filtered.length === 0) return;
    const onKey = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null;
      const tag = target?.tagName;
      const isTyping =
        tag === 'INPUT' || tag === 'TEXTAREA' || target?.isContentEditable === true;
      // Allow Enter from the search input to play the highlighted row,
      // but ignore arrow keys (caret movement should stay native there).
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        if (isTyping) return;
        e.preventDefault();
        const idx = selectedFile
          ? filtered.findIndex((f) => f.path === selectedFile.path)
          : -1;
        let next: number;
        if (idx === -1) {
          next = e.key === 'ArrowDown' ? 0 : filtered.length - 1;
        } else {
          next = e.key === 'ArrowDown' ? idx + 1 : idx - 1;
          if (next < 0) next = 0;
          if (next >= filtered.length) next = filtered.length - 1;
        }
        const target = filtered[next];
        if (target && target.path !== selectedFile?.path) onSelectFile(target);
      } else if (e.key === 'Enter') {
        if (!selectedFile) return;
        // Don't steal Enter from buttons / non-search controls.
        if (isTyping && tag !== 'INPUT') return;
        e.preventDefault();
        onPlayFile(selectedFile);
      }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [disableNav, folder, filtered, selectedFile, onSelectFile, onPlayFile]);

  // Scroll the selected row into view when selection changes via keyboard.
  useEffect(() => {
    if (!selectedFile) return;
    const row = rowRefs.current.get(selectedFile.path);
    row?.scrollIntoView({ block: 'nearest' });
  }, [selectedFile]);

  const counter = debounced
    ? fmt(S.file_count_fmt, { shown: filtered.length, total: files.length })
    : fmt(S.file_count_all, { total: files.length });

  if (!folder) {
    return (
      <section className="flex-1 flex items-center justify-center">
        <div className="text-center max-w-xs">
          <FolderSearch size={36} className="mx-auto text-[var(--subtext)] opacity-50 mb-3" />
          <p className="text-sm text-[var(--subtext)]">{S.no_folder_selected.trim()}</p>
        </div>
      </section>
    );
  }

  return (
    <section className="flex-1 flex flex-col min-w-0">
      <div className="p-3 border-b border-[var(--border)] flex items-center gap-3">
        <div className="relative flex-1">
          <Search
            size={13}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--subtext)] pointer-events-none"
          />
          <Input
            placeholder={config.lang === 'id' ? 'Cari lagu…' : 'Search songs…'}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="pl-8 w-full"
          />
        </div>
        <span className="text-[11px] font-mono text-[var(--subtext)] shrink-0 tabular-nums">
          {counter}
        </span>
      </div>
      <div className="flex-1 overflow-y-auto">
        {filtered.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center px-6 py-12">
            <FileMusic size={32} className="text-[var(--subtext)] opacity-40 mb-2" />
            <p className="text-xs text-[var(--subtext)]">
              {debounced
                ? config.lang === 'id'
                  ? 'Tidak ada lagu yang cocok'
                  : 'No matching songs'
                : config.lang === 'id'
                  ? 'Folder kosong'
                  : 'Folder empty'}
            </p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-[var(--panel)]/95 backdrop-blur-sm text-[var(--subtext)] text-[10px] font-semibold uppercase tracking-wider z-10 border-b border-[var(--border)]">
              <tr>
                <th className="text-left px-3 py-2 w-10">{S.col_no}</th>
                <th className="text-left px-3 py-2">{S.col_title}</th>
                <th className="text-right px-3 py-2 w-20">{S.col_size_kb}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((f, i) => {
                const active = f.path === selectedFile?.path;
                return (
                  <tr
                    key={f.path}
                    ref={(el) => {
                      if (el) rowRefs.current.set(f.path, el);
                      else rowRefs.current.delete(f.path);
                    }}
                    onClick={() => onSelectFile(f)}
                    onDoubleClick={() => onPlayFile(f)}
                    className={`cursor-pointer transition-colors ${
                      active
                        ? 'bg-[var(--accent)]/15 text-[var(--text)]'
                        : i % 2
                          ? 'bg-[var(--row-alt)]/50 hover:bg-[var(--btn-hov)]'
                          : 'hover:bg-[var(--btn-hov)]'
                    }`}
                  >
                    <td className="px-3 py-2 text-[11px] font-mono text-[var(--subtext)] tabular-nums">
                      {i + 1}
                    </td>
                    <td className="px-3 py-2 text-xs truncate" title={f.name}>
                      <span className="inline-flex items-center gap-2">
                        <Music2
                          size={12}
                          className={`shrink-0 ${active ? 'text-[var(--accent)]' : 'text-[var(--subtext)]'}`}
                        />
                        <span className="truncate">{f.name}</span>
                      </span>
                    </td>
                    <td className="px-3 py-2 text-right text-[11px] font-mono text-[var(--subtext)] tabular-nums">
                      {(f.size / 1024).toFixed(1)} KB
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
