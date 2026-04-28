import { Button } from './ui/Button';
import { useConfig } from '../hooks/useConfig';
import { STRINGS } from '../i18n/strings';
import type { MidiFile } from '../types';

interface Props {
  selectedFile: MidiFile | null;
  onPlay: () => void;
  onCancel: () => void;
}

export function BottomBar({ selectedFile, onPlay, onCancel }: Props) {
  const { config } = useConfig();
  const S = STRINGS[config.lang];
  return (
    <footer className="px-6 py-3 border-t border-[var(--border)] flex items-center justify-between">
      <span className="text-xs text-[var(--subtext)] truncate">{selectedFile?.path ?? ''}</span>
      <div className="flex gap-2">
        <Button variant="ghost" onClick={onCancel}>
          {S.cancel_btn}
        </Button>
        <Button onClick={onPlay} disabled={!selectedFile}>
          {S.play_btn}
        </Button>
      </div>
    </footer>
  );
}
