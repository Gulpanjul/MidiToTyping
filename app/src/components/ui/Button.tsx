import { type ButtonHTMLAttributes, forwardRef } from 'react';

type Variant = 'primary' | 'secondary' | 'ghost' | 'destructive';
type Size = 'sm' | 'md' | 'lg';

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

const variantClass: Record<Variant, string> = {
  primary:
    'bg-[var(--accent)] text-[var(--bg)] hover:bg-[var(--accent-hov)] shadow-[0_0_12px_-4px_var(--accent)] hover:shadow-[0_0_16px_-2px_var(--accent)]',
  secondary:
    'bg-[var(--panel)] text-[var(--text)] border border-[var(--border)] hover:bg-[var(--btn-hov)] hover:border-[var(--accent)]/40',
  ghost: 'bg-transparent text-[var(--text)] hover:bg-[var(--btn-hov)]',
  destructive: 'bg-red-600 text-white hover:bg-red-700',
};
const sizeClass: Record<Size, string> = {
  sm: 'h-8 px-3 text-xs',
  md: 'h-9 px-4 text-sm',
  lg: 'h-11 px-6 text-base',
};

export const Button = forwardRef<HTMLButtonElement, Props>(function Button(
  { variant = 'primary', size = 'md', className = '', ...rest },
  ref,
) {
  return (
    <button
      ref={ref}
      {...rest}
      className={`inline-flex items-center justify-center rounded-md font-medium transition-all duration-150 active:scale-[0.97] disabled:opacity-50 disabled:pointer-events-none disabled:shadow-none ${variantClass[variant]} ${sizeClass[size]} ${className}`}
    />
  );
});
