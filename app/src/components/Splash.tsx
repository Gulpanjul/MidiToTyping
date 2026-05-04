import { useEffect, useState } from 'react';
import { useConfig } from '../hooks/useConfig';
import { STRINGS } from '../i18n/strings';

const MIN_VISIBLE_MS = 1100;
const FADE_MS = 280;

export function Splash() {
  const { config, ready } = useConfig();
  const S = STRINGS[config.lang];
  const [minElapsed, setMinElapsed] = useState(false);
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setMinElapsed(true), MIN_VISIBLE_MS);
    return () => clearTimeout(t);
  }, []);

  useEffect(() => {
    if (ready && minElapsed) {
      const t = setTimeout(() => setHidden(true), FADE_MS);
      return () => clearTimeout(t);
    }
  }, [ready, minElapsed]);

  if (hidden) return null;
  const fading = ready && minElapsed;

  return (
    <div
      aria-hidden
      className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-[var(--bg)] transition-opacity"
      style={{
        opacity: fading ? 0 : 1,
        transitionDuration: `${FADE_MS}ms`,
        pointerEvents: fading ? 'none' : 'auto',
      }}
    >
      <div className="flex flex-col items-center gap-5">
        <img
          src="/playsong-icon.png"
          alt="playSong"
          className="w-24 h-24 rounded-2xl shadow-2xl ring-1 ring-[var(--border)] animate-splash-pop"
          draggable={false}
        />
        <div className="text-center">
          <div className="text-2xl font-semibold tracking-tight text-[var(--text)]">
            playSong
          </div>
          <div className="text-[11px] mt-1 text-[var(--subtext)] tracking-wide">
            {S.splash_subtitle}
          </div>
        </div>
        <div className="flex items-center gap-2 mt-2 text-[11px] text-[var(--subtext)]">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-[var(--accent)] animate-splash-pulse" />
          <span>{S.splash_loading}</span>
        </div>
      </div>
    </div>
  );
}
