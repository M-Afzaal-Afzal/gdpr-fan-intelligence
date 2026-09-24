'use client';

import { cn } from '@/lib/utils';

interface SpotlightProps {
  className?: string;
}

/** Soft spotlight wash for section headers — 21st.dev / Aceternity hero pattern. */
export function Spotlight({ className }: SpotlightProps) {
  return (
    <div
      className={cn(
        'pointer-events-none absolute -top-24 left-1/2 h-[320px] w-[640px] -translate-x-1/2 rounded-full',
        'bg-[radial-gradient(circle,var(--color-primary)_0%,transparent_65%)] opacity-[0.07]',
        className,
      )}
    />
  );
}
