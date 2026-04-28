import { useEffect, useMemo, useState } from 'react';
import { Input } from './ui/Input';
import { useConfig } from '../hooks/useConfig';
import { STRINGS, fmt } from '../i18n/strings';
import { api } from '../lib/tauri';
import type { MidiFile } from '../types';

interface Props {
  folder: string | null;
  selectedFile: MidiFile | null;
  onSelectFile: (f: MidiFile) => void;
}

export function MusicPane({ folder, selectedFile, onSelectFile }: Props) {
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

  const counter = debounced
    ? fmt(S.file_count_fmt, { shown: filtered.length, total: files.length })
    : fmt(S.file_count_all, { total: files.length });

  if (!folder) {
    return (
      <section className="flex-1 flex items-center justify-center text-[var(--subtext)]">
        {S.no_folder_selected}
      </section>
    );
  }

  return (
    <section className="flex-1 flex flex-col">
      <div className="p-3 border-b border-[var(--border)] flex items-center gap-3">
        <Input
          placeholder="search…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="flex-1"
        />
        <span className="text-xs text-[var(--subtext)]">{counter}</span>
      </div>
      <div className="flex-1 overflow-y-auto">
        <table className="w-full text-sm">
          <thead className="sticky top-0 bg-[var(--panel)] text-[var(--subtext)] text-xs uppercase">
            <tr>
              <th className="text-left px-3 py-2 w-10">{S.col_no}</th>
              <th className="text-left px-3 py-2">{S.col_title}</th>
              <th className="text-right px-3 py-2 w-24">{S.col_size_kb}</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((f, i) => (
              <tr
                key={f.path}
                onClick={() => onSelectFile(f)}
                onDoubleClick={() => onSelectFile(f)}
                className={`cursor-pointer ${
                  f.path === selectedFile?.path
                    ? 'bg-[var(--sel-bg)]'
                    : i % 2
                      ? 'bg-[var(--row-alt)]'
                      : ''
                }`}
              >
                <td className="px-3 py-1.5">{i + 1}</td>
                <td className="px-3 py-1.5 truncate" title={f.name}>
                  {f.name}
                </td>
                <td className="px-3 py-1.5 text-right">{(f.size / 1024).toFixed(1)} KB</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
