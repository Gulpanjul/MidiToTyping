import { type ReactNode, useEffect } from 'react';
import { X } from 'lucide-react';

interface Props {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg';
  showCloseButton?: boolean;
}

const sizeClass: Record<NonNullable<Props['size']>, string> = {
  sm: 'min-w-[360px] max-w-[440px]',
  md: 'min-w-[420px] max-w-[560px]',
  lg: 'min-w-[480px] max-w-[680px]',
};

export function Dialog({
  open,
  onClose,
  title,
  children,
  size = 'md',
  showCloseButton = true,
}: Props) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm animate-fade-in"
      onClick={onClose}
    >
      <div
        className={`relative bg-[var(--panel)] text-[var(--text)] rounded-xl shadow-2xl border border-[var(--border)] p-6 animate-scale-in ${sizeClass[size]}`}
        onClick={(e) => e.stopPropagation()}
      >
        {showCloseButton && (
          <button
            onClick={onClose}
            aria-label="Close"
            className="absolute top-3 right-3 p-1.5 rounded-md text-[var(--subtext)] hover:text-[var(--text)] hover:bg-[var(--btn-hov)] transition-colors"
          >
            <X size={16} />
          </button>
        )}
        {title && <h2 className="text-lg font-semibold mb-4 pr-8">{title}</h2>}
        {children}
      </div>
    </div>
  );
}
