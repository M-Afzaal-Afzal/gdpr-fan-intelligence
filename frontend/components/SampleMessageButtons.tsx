'use client';

import { Button } from '@/components/ui/button';
import { SAMPLE_MESSAGES, type SampleMessage } from '@/lib/constants';

export function SampleMessageButtons({
  onPick,
}: {
  onPick: (sample: SampleMessage) => void;
}) {
  return (
    <div className="space-y-2">
      <p className="text-xs font-medium uppercase tracking-wide text-[var(--color-muted-foreground)]">
        Try a sample
      </p>
      <div className="flex flex-wrap gap-2">
        {SAMPLE_MESSAGES.map((sample) => (
          <Button
            key={sample.label}
            variant="outline"
            size="sm"
            title={sample.description}
            onClick={() => onPick(sample)}
          >
            {sample.label}
          </Button>
        ))}
      </div>
    </div>
  );
}
