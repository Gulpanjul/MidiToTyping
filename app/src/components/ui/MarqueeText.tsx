import { useLayoutEffect, useRef, useState, type CSSProperties } from 'react';

interface Props {
  text: string;
  className?: string;
  /** Cycle duration in seconds — full back-and-forth sweep. */
  durationSec?: number;
}

// Single-line text that scrolls horizontally only when the content overflows
// its container — short titles stay still. Pure CSS animation, so no per-frame
// JS work while the popup is open.
export function MarqueeText({ text, className, durationSec = 9 }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const innerRef = useRef<HTMLSpanElement | null>(null);
  const [shiftPx, setShiftPx] = useState(0);

  useLayoutEffect(() => {
    const c = containerRef.current;
    const inner = innerRef.current;
    if (!c || !inner) return;
    const measure = () => {
      const overflow = inner.scrollWidth - c.clientWidth;
      setShiftPx(overflow > 0 ? overflow : 0);
    };
    measure();
    const ro = new ResizeObserver(measure);
    ro.observe(c);
    ro.observe(inner);
    return () => ro.disconnect();
  }, [text]);

  const isOverflowing = shiftPx > 0;
  const style: CSSProperties | undefined = isOverflowing
    ? ({
        ['--marquee-shift' as string]: `-${shiftPx}px`,
        animationDuration: `${durationSec}s`,
      } as CSSProperties)
    : undefined;

  return (
    <div
      ref={containerRef}
      className={`overflow-hidden ${className ?? ''}`}
      title={text}
    >
      <span
        ref={innerRef}
        className={`inline-block whitespace-nowrap ${
          isOverflowing ? 'animate-marquee' : ''
        }`}
        style={style}
      >
        {text}
      </span>
    </div>
  );
}
