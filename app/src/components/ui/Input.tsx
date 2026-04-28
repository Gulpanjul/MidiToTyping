import { type InputHTMLAttributes, forwardRef } from 'react';

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  function Input({ className = '', ...rest }, ref) {
    return (
      <input
        ref={ref}
        {...rest}
        className={`h-9 px-3 rounded-md bg-[var(--entry-bg)] text-[var(--text)] border border-[var(--border)] outline-none focus:ring-2 focus:ring-[var(--accent)]/30 ${className}`}
      />
    );
  },
);
