import { Dialog } from './ui/Dialog';
import { useConfig } from '../hooks/useConfig';
import { STRINGS } from '../i18n/strings';

const APP = {
  version: '0.1.0',
  date: '2026-04-28',
  author: 'Gulpanjul',
  github: 'github.com/Gulpanjul/MidiToTyping',
};

export function InfoPopup({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { config } = useConfig();
  const S = STRINGS[config.lang];
  return (
    <Dialog open={open} onClose={onClose} title={S.info_title}>
      <div className="text-sm space-y-2">
        <div>
          <b>playSong</b> v{APP.version} · {APP.date}
        </div>
        <div className="text-[var(--subtext)]">by {APP.author}</div>
        <div className="text-[var(--subtext)]">{S.player_hotkeys}</div>
        <div className="pt-2">
          <a
            href={`https://${APP.github}`}
            target="_blank"
            rel="noreferrer"
            className="text-[var(--accent)] hover:underline"
          >
            {APP.github}
          </a>
        </div>
      </div>
    </Dialog>
  );
}
