'use client';

import { cn } from '@/lib/utils';

interface HighlightCardProps {
  children: React.ReactNode;
  className?: string;
  /** Accent color on the left edge — static, no broken corner animation. */
  accent?: 'primary' | 'mask';
}

/** Clean emphasis card with a solid left accent (replaces broken rotating border). */
export function HighlightCard({
  children,
  className,
  accent = 'primary',
}: HighlightCardProps) {
  const accentColor =
    accent === 'mask' ? 'var(--color-mask-highlight)' : 'var(--color-primary)';

  return (
    <div
      className={cn(
        'overflow-hidden rounded-xl border border-[var(--color-border)] bg-[var(--color-card)]',
        className,
      )}
    >
      <div className="flex min-h-full">
        <div className="w-1 shrink-0" style={{ backgroundColor: accentColor }} aria-hidden />
        <div className="min-w-0 flex-1">{children}</div>
      </div>
    </div>
  );
}

/** @deprecated Use HighlightCard — rotating conic borders break on rounded corners. */
export function MovingBorder({
  children,
  className,
  containerClassName,
}: {
  children: React.ReactNode;
  className?: string;
  containerClassName?: string;
}) {
  return (
    <HighlightCard className={cn(containerClassName, className)} accent="mask">
      {children}
    </HighlightCard>
  );
}
