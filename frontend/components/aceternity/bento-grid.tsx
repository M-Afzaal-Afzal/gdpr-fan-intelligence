'use client';

import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

interface BentoGridProps {
  className?: string;
  children: React.ReactNode;
}

export function BentoGrid({ className, children }: BentoGridProps) {
  return (
    <div className={cn('grid auto-rows-[minmax(7rem,auto)] grid-cols-1 gap-3 sm:grid-cols-3', className)}>
      {children}
    </div>
  );
}

interface BentoGridItemProps {
  className?: string;
  title: string;
  description: string;
  header?: React.ReactNode;
  index?: number;
}

export function BentoGridItem({
  className,
  title,
  description,
  header,
  index = 0,
}: BentoGridItemProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.08, duration: 0.35 }}
      className={cn(
        'group/bento relative row-span-1 overflow-hidden rounded-xl border border-[var(--color-border)]',
        'bg-[var(--color-card)] p-4 transition-shadow hover:shadow-md',
        className,
      )}
    >
      {header}
      <div className="transition duration-200 group-hover/bento:translate-x-0.5">
        <p className="font-mono text-[10px] uppercase tracking-wider text-[var(--color-primary)]">
          {title}
        </p>
        <p className="mt-1.5 text-xs leading-relaxed text-[var(--color-muted-foreground)]">
          {description}
        </p>
      </div>
    </motion.div>
  );
}
