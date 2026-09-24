'use client';

import { useEffect, useRef, useState } from 'react';
import { motion, useSpring, useTransform } from 'framer-motion';
import { cn } from '@/lib/utils';

interface TracingBeamProps {
  children: React.ReactNode;
  className?: string;
  /** 0–1 progress along the beam (pipeline step completion). */
  progress?: number;
}

/** Aceternity-inspired vertical tracing beam — progress-driven for pipeline sidebar. */
export function TracingBeam({ children, className, progress = 0 }: TracingBeamProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [height, setHeight] = useState(0);

  useEffect(() => {
    if (!ref.current) return;
    const ro = new ResizeObserver(([entry]) => {
      setHeight(entry.contentRect.height);
    });
    ro.observe(ref.current);
    return () => ro.disconnect();
  }, []);

  const spring = useSpring(0, { stiffness: 80, damping: 22 });
  const beamHeight = useTransform(spring, (v) => Math.max(0, v * height));

  useEffect(() => {
    spring.set(progress);
  }, [progress, spring]);

  return (
    <div ref={ref} className={cn('relative mx-auto w-full max-w-4xl', className)}>
      <div className="absolute left-4 top-3 md:left-5">
        <div
          className="w-px bg-[var(--color-border)]"
          style={{ height: height > 0 ? height - 12 : '100%' }}
        />
        <motion.div
          className="absolute left-0 top-0 w-px bg-gradient-to-b from-[var(--color-primary)] via-[var(--color-pipeline-active)] to-transparent"
          style={{ height: beamHeight }}
        />
        <motion.div
          className="absolute left-[-3px] h-2 w-2 rounded-full bg-[var(--color-primary)] shadow-[0_0_12px_var(--color-primary)]"
          style={{ top: beamHeight }}
        />
      </div>
      <div className="pl-10 md:pl-12">{children}</div>
    </div>
  );
}
