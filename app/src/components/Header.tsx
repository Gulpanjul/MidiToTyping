import { useState } from 'react';
import { useConfig } from '../hooks/useConfig';
import { STRINGS } from '../i18n/strings';
import { Button } from './ui/Button';
import { InfoPopup } from './InfoPopup';
import type { Lang, Palette, Theme } from '../types';

export function Header() {
  const { config, setConfig } = useConfig();
  const S = STRINGS[config.lang];
  const [showInfo, setShowInfo] = useState(false);

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-[var(--border)]">
      <div>
        <h1 className="text-xl font-semibold">{S.header_title}</h1>
        <p className="text-xs text-[var(--subtext)]">{S.header_subtitle}</p>
      </div>
      <div className="flex items-center gap-2">
        <SegToggle
          options={[
            { v: 'dark', l: '🌙' },
            { v: 'light', l: '☀' },
          ]}
          value={config.theme}
          onChange={(v) => setConfig({ theme: v as Theme })}
        />
        <SegToggle
          options={[
            { v: 'celestial', l: S.palette_celestial },
            { v: 'grand_piano', l: S.palette_grand },
          ]}
          value={config.palette}
          onChange={(v) => setConfig({ palette: v as Palette })}
        />
        <SegToggle
          options={[
            { v: 'id', l: 'ID' },
            { v: 'en', l: 'EN' },
          ]}
          value={config.lang}
          onChange={(v) => setConfig({ lang: v as Lang })}
        />
        <Button variant="ghost" size="sm" onClick={() => setShowInfo(true)}>
          {S.info_btn}
        </Button>
      </div>
      <InfoPopup open={showInfo} onClose={() => setShowInfo(false)} />
    </header>
  );
}

function SegToggle({
  options,
  value,
  onChange,
}: {
  options: { v: string; l: string }[];
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="inline-flex rounded-md border border-[var(--border)] bg-[var(--panel)] p-0.5">
      {options.map((o) => (
        <button
          key={o.v}
          onClick={() => onChange(o.v)}
          className={`px-3 h-7 text-xs rounded transition-colors ${
            o.v === value
              ? 'bg-[var(--accent)] text-[var(--bg)]'
              : 'text-[var(--subtext)] hover:text-[var(--text)]'
          }`}
        >
          {o.l}
        </button>
      ))}
    </div>
  );
}
