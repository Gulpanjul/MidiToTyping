import { useEffect, useState } from 'react';
import { Minus, Square, Copy, X } from 'lucide-react';
import { getCurrentWindow } from '@tauri-apps/api/window';

/**
 * Custom title bar replacing the default Windows chrome.
 * Tauri config sets decorations: false; this component provides:
 *   - draggable region (data-tauri-drag-region)
 *   - app icon + title text
 *   - min / max-restore / close buttons matching theme accent
 *
 * Drag is wired by Tauri purely via the data-tauri-drag-region attribute,
 * no JS handler needed. The buttons call window APIs directly.
 */
export function TitleBar() {
  const [isMaximized, setIsMaximized] = useState(false);

  useEffect(() => {
    const win = getCurrentWindow();
    let unlisten: (() => void) | undefined;
    (async () => {
      try {
        setIsMaximized(await win.isMaximized());
        unlisten = await win.onResized(async () => {
          try {
            setIsMaximized(await win.isMaximized());
          } catch {
            // ignore
          }
        });
      } catch {
        // running in browser dev mode (no Tauri runtime)
      }
    })();
    return () => {
      unlisten?.();
    };
  }, []);

  const onMinimize = async () => {
    try {
      await getCurrentWindow().minimize();
    } catch {
      /* ignore */
    }
  };
  const onToggleMax = async () => {
    try {
      await getCurrentWindow().toggleMaximize();
    } catch {
      /* ignore */
    }
  };
  const onClose = async () => {
    try {
      await getCurrentWindow().close();
    } catch {
      /* ignore */
    }
  };

  return (
    <div
      data-tauri-drag-region
      className="h-9 flex items-center justify-between bg-[var(--bg)] border-b border-[var(--border)] select-none shrink-0"
    >
      <div
        data-tauri-drag-region
        className="flex items-center gap-2 px-3 text-[11px] font-medium text-[var(--subtext)] flex-1 min-w-0"
      >
        <img src="/playsong-icon.png" alt="" className="w-4 h-4 rounded-sm pointer-events-none" />
        <span data-tauri-drag-region className="truncate">
          playSong
        </span>
      </div>
      <div className="flex h-full shrink-0">
        <TitleBarBtn onClick={onMinimize} aria-label="Minimize">
          <Minus size={13} />
        </TitleBarBtn>
        <TitleBarBtn onClick={onToggleMax} aria-label={isMaximized ? 'Restore' : 'Maximize'}>
          {isMaximized ? <Copy size={11} /> : <Square size={11} />}
        </TitleBarBtn>
        <TitleBarBtn onClick={onClose} aria-label="Close" danger>
          <X size={13} />
        </TitleBarBtn>
      </div>
    </div>
  );
}

function TitleBarBtn({
  children,
  onClick,
  danger,
  ...rest
}: {
  children: React.ReactNode;
  onClick: () => void;
  danger?: boolean;
} & React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      onClick={onClick}
      {...rest}
      className={`inline-flex items-center justify-center w-11 h-full text-[var(--subtext)] hover:text-[var(--text)] transition-colors ${
        danger ? 'hover:bg-red-600 hover:text-white' : 'hover:bg-[var(--btn-hov)]'
      }`}
    >
      {children}
    </button>
  );
}
