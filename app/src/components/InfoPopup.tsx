import { Dialog } from './ui/Dialog';
import { useConfig } from '../hooks/useConfig';
import { STRINGS } from '../i18n/strings';
import {
  Music4,
  User,
  Calendar,
  Github,
  Cpu,
  Keyboard,
  Play,
  Rewind,
  FastForward,
  RotateCcw,
} from 'lucide-react';

const APP = {
  version: '0.2.0',
  date: '2026-05-02',
  author: 'Gulpanjul',
  github: 'github.com/Gulpanjul/MidiToTyping',
  stack: 'Tauri v2  ·  React 19  ·  Rust  ·  midly  ·  enigo',
};

type HkLabelKey = 'hk_play_pause' | 'hk_rewind' | 'hk_skip' | 'hk_restart';
const HOTKEYS: { key: string; icon: typeof Play; labelKey: HkLabelKey }[] = [
  { key: 'DELETE', icon: Play, labelKey: 'hk_play_pause' },
  { key: 'HOME', icon: Rewind, labelKey: 'hk_rewind' },
  { key: 'END', icon: FastForward, labelKey: 'hk_skip' },
  { key: 'INSERT', icon: RotateCcw, labelKey: 'hk_restart' },
];

export function InfoPopup({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { config } = useConfig();
  const S = STRINGS[config.lang];

  return (
    <Dialog open={open} onClose={onClose} title={S.info_title} size="md">
      <div className="space-y-5">
        {/* App identity row */}
        <div className="flex items-start gap-3">
          <div className="shrink-0 w-12 h-12 rounded-xl bg-[var(--accent)]/10 border border-[var(--accent)]/30 flex items-center justify-center text-[var(--accent)]">
            <Music4 size={22} strokeWidth={2} />
          </div>
          <div className="min-w-0">
            <div className="text-base font-semibold leading-tight">playSong</div>
            <div className="text-xs text-[var(--subtext)] mt-0.5">
              {S.app_tagline}
            </div>
            <div className="inline-flex items-center gap-1.5 mt-2 px-2 py-0.5 rounded-md bg-[var(--entry-bg)] border border-[var(--border)] text-[10px] font-mono text-[var(--subtext)]">
              v{APP.version}
            </div>
          </div>
        </div>

        {/* Metadata grid */}
        <div className="grid grid-cols-[auto_1fr] gap-x-3 gap-y-2 text-xs">
          <Meta icon={User} label={S.made_by} value={APP.author} />
          <Meta icon={Calendar} label={S.released} value={APP.date} />
          <Meta icon={Cpu} label="Stack" value={APP.stack} mono />
          <Meta
            icon={Github}
            label="GitHub"
            value={
              <a
                href={`https://${APP.github}`}
                target="_blank"
                rel="noreferrer"
                className="text-[var(--accent)] hover:underline"
              >
                {APP.github}
              </a>
            }
          />
        </div>

        {/* Hotkeys section */}
        <div>
          <div className="flex items-center gap-2 mb-2 text-xs font-semibold uppercase tracking-wider text-[var(--subtext)]">
            <Keyboard size={13} />
            {S.playback_controls}
          </div>
          <ul className="space-y-1.5">
            {HOTKEYS.map(({ key, icon: Icon, labelKey }) => (
              <li
                key={key}
                className="flex items-center gap-3 px-3 py-2 rounded-md bg-[var(--entry-bg)]/40 border border-[var(--border)]"
              >
                <kbd className="shrink-0 px-2 py-0.5 text-[10px] font-mono font-semibold rounded bg-[var(--bg)] border border-[var(--border)] text-[var(--text)] min-w-[60px] text-center">
                  {key}
                </kbd>
                <Icon size={14} className="text-[var(--subtext)] shrink-0" />
                <span className="text-xs">{S[labelKey]}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Dialog>
  );
}

function Meta({
  icon: Icon,
  label,
  value,
  mono,
}: {
  icon: typeof User;
  label: string;
  value: React.ReactNode;
  mono?: boolean;
}) {
  return (
    <>
      <div className="flex items-center gap-1.5 text-[var(--subtext)]">
        <Icon size={12} />
        <span>{label}</span>
      </div>
      <div className={mono ? 'font-mono text-[11px]' : ''}>{value}</div>
    </>
  );
}
