import { useState } from 'react';
import { open as openDialog } from '@tauri-apps/plugin-dialog';
import { Button } from './ui/Button';
import { Slider } from './ui/Slider';
import { useConfig } from '../hooks/useConfig';
import { usePlayback } from '../hooks/usePlayback';
import { STRINGS } from '../i18n/strings';

interface Props {
  selectedFolder: string | null;
  onSelectFolder: (p: string) => void;
}

export function FolderPane({ selectedFolder, onSelectFolder }: Props) {
  const { config, setConfig } = useConfig();
  const { state, setSpeed } = usePlayback();
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
        <div className="text-xs uppercase tracking-wide text-[var(--subtext)] mb-2">
          {S.folder_nav_panel}
        </div>
        <div className="flex gap-2">
          <Button size="sm" variant="secondary" onClick={handleAdd} disabled={busy}>
            {S.add_folder_btn}
          </Button>
          <Button size="sm" variant="ghost" onClick={handleRemove} disabled={!selectedFolder}>
            {S.remove_folder_btn}
          </Button>
        </div>
      </div>
      <ul className="flex-1 overflow-y-auto py-2">
        {config.folders.length === 0 && (
          <li className="px-3 py-4 text-xs text-[var(--subtext)]">{S.no_folder_selected}</li>
        )}
        {config.folders.map((f) => (
          <li key={f}>
            <button
              onClick={() => onSelectFolder(f)}
              className={`w-full text-left px-3 py-2 text-sm truncate ${
                f === selectedFolder ? 'bg-[var(--sel-bg)]' : 'hover:bg-[var(--btn-hov)]'
              }`}
              title={f}
            >
              {f.split(/[\\/]/).pop() || f}
            </button>
          </li>
        ))}
      </ul>
      <div className="p-3 border-t border-[var(--border)]">
        <Slider
          label={`${S.speed_label} — ${state.speed.toFixed(2)}×`}
          min={0.25}
          max={3.0}
          step={0.05}
          value={state.speed}
          onChange={(v) => setSpeed(v)}
        />
        <div className="text-[10px] text-[var(--subtext)] text-center mt-1">{S.speed_range}</div>
      </div>
    </aside>
  );
}
