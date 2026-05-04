import { useState } from 'react';
import { open as openDialog } from '@tauri-apps/plugin-dialog';
import { FolderPlus, FolderMinus, Folder, FolderOpen, Gauge } from 'lucide-react';
import { Button } from './ui/Button';
import { Slider } from './ui/Slider';
import { useConfig } from '../hooks/useConfig';
import { usePlaybackActions, usePlaybackState } from '../hooks/usePlayback';
import { STRINGS } from '../i18n/strings';
import { difficultyFor } from '../lib/difficulty';

interface Props {
  selectedFolder: string | null;
  onSelectFolder: (p: string) => void;
}

// Strip leading symbol/whitespace from i18n labels (e.g. "+ Tambah" -> "Tambah")
// since we now show a Lucide icon next to them.
function stripPrefix(s: string): string {
  return s.replace(/^[\+\-−×✕▶⏸🎵←]\s*/, '').trim();
}

export function FolderPane({ selectedFolder, onSelectFolder }: Props) {
  const { config, setConfig } = useConfig();
  const state = usePlaybackState();
  const { setSpeed } = usePlaybackActions();
  const S = STRINGS[config.lang];
  const [busy, setBusy] = useState(false);

  async function handleAdd() {
    if (busy) return;
    setBusy(true);
    try {
      const picked = await openDialog({
        directory: true,
        multiple: false,
        title: S.add_folder_dialog,
      });
      if (typeof picked === 'string' && !config.folders.includes(picked)) {
        setConfig({ folders: [...config.folders, picked] });
        onSelectFolder(picked);
      }
    } finally {
      setBusy(false);
    }
  }

  function handleRemove() {
    if (!selectedFolder) return;
    setConfig({ folders: config.folders.filter((f) => f !== selectedFolder) });
    onSelectFolder('');
  }

  return (
    <aside className="w-64 shrink-0 border-r border-[var(--border)] bg-[var(--panel)] flex flex-col">
      <div className="p-3 border-b border-[var(--border)]">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-[var(--subtext)] mb-2">
          {S.folder_nav_panel}
        </div>
        <div className="flex gap-1.5">
          <Button
            size="sm"
            variant="secondary"
            onClick={handleAdd}
            disabled={busy}
            className="flex-1 gap-1.5"
          >
            <FolderPlus size={13} />
            {stripPrefix(S.add_folder_btn)}
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={handleRemove}
            disabled={!selectedFolder}
            className="gap-1.5"
          >
            <FolderMinus size={13} />
          </Button>
        </div>
      </div>
      <ul className="flex-1 overflow-y-auto py-1">
        {config.folders.length === 0 && (
          <li className="px-3 py-6 text-center">
            <Folder size={20} className="mx-auto text-[var(--subtext)] mb-2 opacity-50" />
            <div className="text-[11px] text-[var(--subtext)] leading-relaxed">
              {stripPrefix(S.no_folder_selected)}
            </div>
          </li>
        )}
        {config.folders.map((f) => {
          const active = f === selectedFolder;
          return (
            <li key={f}>
              <button
                onClick={() => onSelectFolder(f)}
                className={`w-full flex items-center gap-2 text-left px-3 py-1.5 text-xs truncate transition-colors ${
                  active
                    ? 'bg-[var(--sel-bg)] text-[var(--text)]'
                    : 'text-[var(--subtext)] hover:text-[var(--text)] hover:bg-[var(--btn-hov)]'
                }`}
                title={f}
              >
                {active ? (
                  <FolderOpen size={13} className="shrink-0 text-[var(--accent)]" />
                ) : (
                  <Folder size={13} className="shrink-0" />
                )}
                <span className="truncate">{f.split(/[\\/]/).pop() || f}</span>
              </button>
            </li>
          );
        })}
      </ul>
      <div className="p-3 border-t border-[var(--border)]">
        {(() => {
          const diff = difficultyFor(state.speed, S);
          return (
            <>
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-wider text-[var(--subtext)]">
                  <Gauge size={11} />
                  {S.speed_label}
                </div>
                <div className="text-xs font-mono text-[var(--accent)]">
                  {state.speed.toFixed(2)}×
                </div>
              </div>
              <div
                className="text-center text-xs font-semibold mb-1"
                style={{ color: diff.color }}
              >
                {diff.label}
              </div>
              <Slider
                min={0.25}
                max={3.0}
                step={0.05}
                value={state.speed}
                onChange={(v) => setSpeed(v)}
              />
              <div className="flex justify-between text-[9px] text-[var(--subtext)]/70 mt-1 font-mono">
                <span>0.25×</span>
                <span>3.00×</span>
              </div>
            </>
          );
        })()}
      </div>
    </aside>
  );
}
