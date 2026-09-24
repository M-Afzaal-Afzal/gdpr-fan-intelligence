import { Clock } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { formatDurationSeconds } from '@/lib/format';
import type { PipelineTiming } from '@/lib/types';

interface TimingBadgesProps {
  timing: PipelineTiming;
  compact?: boolean;
}

/** Human-readable stage labels — "mask" = anonymize PII; "gate" = re-scan before LLM. */
const STAGE_LABELS: { key: keyof PipelineTiming | 'total'; label: string; hint: string }[] = [
  {
    key: 'detect_ms',
    label: 'PII scan',
    hint: 'Language detection + finding personal data',
  },
  {
    key: 'mask_ms',
    label: 'Anonymize',
    hint: 'Replace names, emails, IDs with [TYPE_N] placeholders',
  },
  {
    key: 'safety_gate_ms',
    label: 'Safety check',
    hint: 'Re-scan masked text — block LLM if PII still present',
  },
  {
    key: 'llm_ms',
    label: 'Analysis',
    hint: 'LLM call on masked message only',
  },
  {
    key: 'total_ms',
    label: 'Total',
    hint: 'End-to-end server time',
  },
];

function stageValue(timing: PipelineTiming, key: string): number | null {
  if (key === 'llm_ms') return timing.llm_ms;
  if (key === 'total_ms') return timing.total_ms;
  return timing[key as keyof PipelineTiming] as number;
}

export function TimingBadges({ timing, compact = false }: TimingBadgesProps) {
  const items = STAGE_LABELS.filter((stage) => {
    if (stage.key === 'llm_ms') return timing.llm_ms !== null;
    return true;
  }).map((stage) => ({
    ...stage,
    value: formatDurationSeconds(stageValue(timing, stage.key)!),
  }));

  if (compact) {
    return (
      <div className="flex flex-wrap items-center gap-1.5 font-mono text-xs text-[var(--color-muted-foreground)]">
        <Clock className="h-3.5 w-3.5 shrink-0" />
        {items.map((item, i) => (
          <span key={item.label} title={item.hint}>
            {i > 0 && <span className="mx-1 opacity-40">·</span>}
            <span className="text-[var(--color-foreground)]">{item.label}</span> {item.value}
          </span>
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item) => (
        <Badge
          key={item.label}
          variant="outline"
          className="gap-1 font-mono text-xs"
          title={item.hint}
        >
          <span className="font-sans font-medium">{item.label}</span>
          {item.value}
        </Badge>
      ))}
    </div>
  );
}
