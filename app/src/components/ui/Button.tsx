import { type ButtonHTMLAttributes, forwardRef } from 'react';

type Variant = 'primary' | 'secondary' | 'ghost' | 'destructive';
type Size = 'sm' | 'md' | 'lg';

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

const variantClass: Record<Variant, string> = {
  primary: 'bg-[var(--accent)] text-[var(--bg)] hover:bg-[var(--accent-hov)]',
  secondary:
    'bg-[var(--panel)] text-[var(--text)] border border-[var(--border)] hover:bg-[var(--btn-hov)]',
  ghost: 'bg-transparent text-[var(--text)] hover:bg-[var(--btn-hov)]',
  destructive: 'bg-red-600 text-white hover:bg-red-700',
};
const sizeClass: Record<Size, string> = {
  sm: 'h-8 px-3 text-sm',
  md: 'h-10 px-4 text-sm',
  lg: 'h-12 px-6 text-base',
};

export const Button = forwardRef<HTMLButtonElement, Props>(function Button(
  { variant = 'primary', size = 'md', className = '', ...rest },
  ref,
) {
  return (
    <button
      ref={ref}
      {...rest}
      className={`inline-flex items-center justify-center rounded-md font-medium transition-colors disabled:opacity-50 disabled:pointer-events-none ${variantClass[variant]} ${sizeClass[size]} ${className}`}
    />
  );
});
