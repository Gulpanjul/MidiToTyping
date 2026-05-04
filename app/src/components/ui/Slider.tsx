import { type ChangeEvent } from 'react';

interface Props {
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (v: number) => void;
  label?: string;
}

export function Slider({ value, min, max, step, onChange, label }: Props) {
  const handle = (e: ChangeEvent<HTMLInputElement>) => onChange(parseFloat(e.target.value));
  return (
    <div className="flex flex-col gap-1">
      {label && <span className="text-[10px] text-[var(--subtext)]">{label}</span>}
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={handle}
        className="ps-slider w-full"
      />
    </div>
  );
}
