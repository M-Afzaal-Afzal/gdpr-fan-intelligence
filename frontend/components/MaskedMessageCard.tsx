import { cn } from '@/lib/utils';

const PLACEHOLDER_RE = /(\[[A-Z_]+_\d+\]|\[[A-Z_]+_REDACTED\])/g;

/** Renders a masked message and highlights the placeholder tokens. */
export function MaskedMessageCard({ message }: { message: string }) {
  const parts = message.split(PLACEHOLDER_RE);

  return (
    <p className="whitespace-pre-wrap break-words font-mono text-sm leading-relaxed">
      {parts.map((part, i) =>
        PLACEHOLDER_RE.test(part) ? (
          <span
            key={i}
            className={cn(
              'mx-0.5 rounded px-1.5 py-0.5 font-semibold',
              'bg-[var(--color-mask-highlight-bg)] text-[var(--color-mask-highlight)]',
            )}
          >
            {part}
          </span>
        ) : (
          <span key={i}>{part}</span>
        ),
      )}
    </p>
  );
}
