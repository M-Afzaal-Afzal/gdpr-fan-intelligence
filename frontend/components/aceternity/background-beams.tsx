'use client';

import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

interface BackgroundBeamsProps {
  className?: string;
}

/** Subtle Aceternity-style beam accents for hero sections — low opacity, no purple glow. */
export function BackgroundBeams({ className }: BackgroundBeamsProps) {
  const paths = [
    'M-380 -189C-380 -189 -312 216 152 343C526 442 677 463 877 463',
    'M-403 -189C-403 -189 -335 216 129 343C503 442 654 463 854 463',
    'M-420 -200C-420 -200 -300 180 120 320C480 420 620 440 800 440',
  ];

  return (
    <div
      className={cn(
        'pointer-events-none absolute inset-0 overflow-hidden [mask-image:radial-gradient(ellipse_at_top,black_20%,transparent_75%)]',
        className,
      )}
    >
      <svg
        className="absolute inset-0 h-full w-full stroke-[var(--color-primary)]/15"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 960 540"
        preserveAspectRatio="xMidYMid slice"
      >
        {paths.map((d, i) => (
          <motion.path
            key={i}
            d={d}
            strokeWidth="0.8"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{
              duration: 2.4,
              delay: i * 0.25,
              ease: 'easeInOut',
            }}
          />
        ))}
      </svg>
    </div>
  );
}
