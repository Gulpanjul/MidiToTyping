import { useState, type ReactNode } from 'react';
import { Music4, Moon, Sun, Info } from 'lucide-react';
import { useConfig } from '../hooks/useConfig';
import { STRINGS } from '../i18n/strings';
import { InfoPopup } from './InfoPopup';
import type { Lang, Palette, Theme } from '../types';

export function Header() {
  const { config, setConfig } = useConfig();
  const S = STRINGS[config.lang];
  const [showInfo, setShowInfo] = useState(false);

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-[var(--border)] bg-[var(--panel)]/30">
      <div className="flex items-center gap-3 min-w-0">
        <div className="shrink-0 w-9 h-9 rounded-lg bg-[var(--accent)]/10 border border-[var(--accent)]/30 flex items-center justify-center text-[var(--accent)]">
          <Music4 size={18} strokeWidth={2} />
        </div>
        <div className="min-w-0">
          <h1 className="text-base font-semibold leading-tight truncate">{S.header_title}</h1>
          <p className="text-[11px] text-[var(--subtext)] mt-0.5 truncate">{S.header_subtitle}</p>
        </div>
      </div>

      <div className="flex items-center gap-2 shrink-0">
        <SegToggle
          ariaLabel="Theme"
          options={[
            { v: 'dark', l: <Moon size={13} />, title: 'Dark' },
            { v: 'light', l: <Sun size={13} />, title: 'Light' },
          ]}
          value={config.theme}
          onChange={(v) => setConfig({ theme: v as Theme })}
        />
        <SegToggle
          ariaLabel="Palette"
          options={[
            { v: 'celestial', l: S.palette_celestial },
            { v: 'grand_piano', l: S.palette_grand },
          ]}
          value={config.palette}
          onChange={(v) => setConfig({ palette: v as Palette })}
        />
        <SegToggle
          ariaLabel="Language"
          options={[
            { v: 'id', l: 'ID' },
            { v: 'en', l: 'EN' },
          ]}
          value={config.lang}
          onChange={(v) => setConfig({ lang: v as Lang })}
        />
        <button
          onClick={() => setShowInfo(true)}
          aria-label={S.info_btn}
          title={S.info_btn}
          className="inline-flex items-center justify-center w-8 h-8 rounded-md text-[var(--subtext)] hover:text-[var(--text)] hover:bg-[var(--btn-hov)] transition-colors active:scale-95"
        >
          <Info size={15} />
        </button>
      </div>
      <InfoPopup open={showInfo} onClose={() => setShowInfo(false)} />
    </header>
  );
}

interface SegOption {
  v: string;
  l: ReactNode;
  title?: string;
}

function SegToggle({
  options,
  value,
  onChange,
  ariaLabel,
}: {
  options: SegOption[];
  value: string;
  onChange: (v: string) => void;
  ariaLabel?: string;
}) {
  return (
    <div
      role="group"
      aria-label={ariaLabel}
      className="inline-flex rounded-md border border-[var(--border)] bg-[var(--panel)] p-0.5"
    >
      {options.map((o) => {
        const active = o.v === value;
        return (
          <button
            key={o.v}
            onClick={() => onChange(o.v)}
            title={o.title}
            className={`inline-flex items-center justify-center min-w-[32px] px-2.5 h-7 text-xs rounded transition-all duration-150 active:scale-95 ${
              active
                ? 'bg-[var(--accent)] text-[var(--bg)] shadow-[0_0_10px_-2px_var(--accent)]'
                : 'text-[var(--subtext)] hover:text-[var(--text)] hover:bg-[var(--btn-hov)]'
            }`}
          >
            {o.l}
          </button>
        );
      })}
    </div>
  );
}
