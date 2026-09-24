import { cn } from '@/lib/utils';

interface BrandMarkProps {
  className?: string;
  showWordmark?: boolean;
  size?: 'sm' | 'md';
}

export function BrandMark({ className, showWordmark = true, size = 'md' }: BrandMarkProps) {
  const iconSize = size === 'sm' ? 'h-7 w-7' : 'h-8 w-8';

  return (
    <div className={cn('flex items-center gap-2.5', className)}>
      <span
        className={cn(
          iconSize,
          'flex shrink-0 items-center justify-center rounded-md bg-[var(--color-primary)] text-[var(--color-primary-foreground)]',
        )}
        aria-hidden
      >
        <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none">
          <path
            d="M12 3 L20 19 H4 Z"
            stroke="currentColor"
            strokeWidth="1.75"
            strokeLinejoin="round"
          />
          <circle cx="12" cy="14" r="1.5" fill="currentColor" />
        </svg>
      </span>
      {showWordmark && (
        <div className="leading-tight">
          <span className="text-sm font-semibold tracking-tight text-[var(--color-foreground)]">
            Raumdeuter
          </span>
          <span className="block text-xs text-[var(--color-muted-foreground)]">
            Fan Intelligence
          </span>
        </div>
      )}
    </div>
  );
}
