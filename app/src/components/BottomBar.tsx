import { Play, X, FileMusic } from 'lucide-react';
import { Button } from './ui/Button';
import { useConfig } from '../hooks/useConfig';
import { STRINGS } from '../i18n/strings';
import type { MidiFile } from '../types';

interface Props {
  selectedFile: MidiFile | null;
  onPlay: () => void;
  onCancel: () => void;
}

// Strip leading symbol/whitespace from i18n labels (e.g. "▶  Mainkan File Ini")
function stripPrefix(s: string): string {
  return s.replace(/^[\+\-−×✕▶⏸🎵←]\s*/, '').trim();
}

export function BottomBar({ selectedFile, onPlay, onCancel }: Props) {
  const { config } = useConfig();
  const S = STRINGS[config.lang];
  return (
    <footer className="px-6 py-3 border-t border-[var(--border)] bg-[var(--panel)]/30 flex items-center justify-between gap-4">
      <div className="flex items-center gap-2 min-w-0 flex-1 text-[11px] text-[var(--subtext)]">
        {selectedFile ? (
          <>
            <FileMusic size={13} className="shrink-0 text-[var(--accent)]" />
            <span className="truncate font-mono" title={selectedFile.path}>
              {selectedFile.name}
            </span>
          </>
        ) : (
          <span className="italic opacity-70">
            {config.lang === 'id' ? 'Belum ada lagu dipilih' : 'No song selected'}
          </span>
        )}
      </div>
      <div className="flex gap-2 shrink-0">
        <Button variant="ghost" size="sm" onClick={onCancel} className="gap-1.5">
          <X size={13} />
          {stripPrefix(S.cancel_btn)}
        </Button>
        <Button onClick={onPlay} disabled={!selectedFile} size="sm" className="gap-1.5 px-4">
          <Play size={14} fill="currentColor" />
          {stripPrefix(S.play_btn)}
        </Button>
      </div>
    </footer>
  );
}
