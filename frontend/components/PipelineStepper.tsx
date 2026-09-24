'use client';

import {
  Ban,
  BarChart3,
  Check,
  Circle,
  Loader2,
  Lock,
  MessageSquare,
  Minus,
  ScanSearch,
  ShieldCheck,
} from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { formatDurationSeconds } from '@/lib/format';

export type StepStatus = 'pending' | 'active' | 'complete' | 'blocked' | 'skipped';

export type PipelineStepId = 'received' | 'detect' | 'mask' | 'gate' | 'analysis';

export interface PipelineStepState {
  id: PipelineStepId;
  label: string;
  description: string;
  status: StepStatus;
  timingMs?: number | null;
}

const STEP_ICONS: Record<PipelineStepId, typeof MessageSquare> = {
  received: MessageSquare,
  detect: ScanSearch,
  mask: Lock,
  gate: ShieldCheck,
  analysis: BarChart3,
};

function statusIcon(status: StepStatus) {
  if (status === 'active') return Loader2;
  if (status === 'complete') return Check;
  if (status === 'blocked') return Ban;
  if (status === 'skipped') return Minus;
  return Circle;
}

function statusStyles(status: StepStatus): string {
  switch (status) {
    case 'active':
      return 'border-[var(--color-pipeline-active)] bg-[var(--color-pipeline-active)]/10 text-[var(--color-pipeline-active)]';
    case 'complete':
      return 'border-[var(--color-pipeline-complete)] bg-[var(--color-pipeline-complete)]/10 text-[var(--color-pipeline-complete)]';
    case 'blocked':
      return 'border-[var(--color-privacy-blocked)] bg-[var(--color-privacy-blocked)]/10 text-[var(--color-privacy-blocked)]';
    case 'skipped':
      return 'border-[var(--color-border)] bg-[var(--color-muted)] text-[var(--color-muted-foreground)]';
    default:
      return 'border-[var(--color-border)] bg-[var(--color-card)] text-[var(--color-muted-foreground)]';
  }
}

/** 0–1 for TracingBeam fill based on step statuses. */
export function pipelineProgress(steps: PipelineStepState[]): number {
  if (steps.length === 0) return 0;
  let score = 0;
  for (const step of steps) {
    if (step.status === 'complete' || step.status === 'blocked' || step.status === 'skipped') {
      score += 1;
    } else if (step.status === 'active') {
      score += 0.5;
    }
  }
  return Math.min(1, score / steps.length);
}

interface PipelineStepperProps {
  steps: PipelineStepState[];
  elapsedMs?: number;
}

export function PipelineStepper({ steps, elapsedMs }: PipelineStepperProps) {
  return (
    <div className="space-y-1">
      <div className="mb-4 flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-wider text-[var(--color-muted-foreground)]">
          Privacy pipeline
        </p>
        {elapsedMs !== undefined && (
          <motion.span
            key={elapsedMs}
            initial={{ opacity: 0.5 }}
            animate={{ opacity: 1 }}
            className="font-mono text-xs tabular-nums text-[var(--color-primary)]"
          >
            {formatDurationSeconds(elapsedMs)}
          </motion.span>
        )}
      </div>

      <ol className="relative space-y-0">
        {steps.map((step, index) => {
          const StepIcon = STEP_ICONS[step.id];
          const StatusIcon = statusIcon(step.status);

          return (
            <motion.li
              key={step.id}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.06, duration: 0.28 }}
              className="relative flex gap-3 pb-7 last:pb-0"
            >
              <motion.div
                layout
                className={cn(
                  'relative z-10 flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2 transition-colors duration-300',
                  statusStyles(step.status),
                )}
              >
                {step.status === 'active' ? (
                  <StatusIcon className="h-4 w-4 animate-spin" />
                ) : step.status === 'complete' ? (
                  <StatusIcon className="h-4 w-4" />
                ) : (
                  <StepIcon className="h-3.5 w-3.5" />
                )}
              </motion.div>

              <div className="min-w-0 flex-1 pt-0.5">
                <div className="flex flex-wrap items-center gap-2">
                  <p
                    className={cn(
                      'text-sm font-medium tracking-tight',
                      step.status === 'pending' && 'text-[var(--color-muted-foreground)]',
                    )}
                  >
                    {step.label}
                  </p>
                  {step.timingMs !== undefined &&
                    step.timingMs !== null &&
                    step.status !== 'pending' && (
                      <span className="rounded-sm bg-[var(--color-muted)] px-1.5 py-0.5 font-mono text-[10px] tabular-nums text-[var(--color-muted-foreground)]">
                        {formatDurationSeconds(step.timingMs)}
                      </span>
                    )}
                </div>
                <p className="mt-0.5 text-xs leading-relaxed text-[var(--color-muted-foreground)]">
                  {step.description}
                </p>
              </div>
            </motion.li>
          );
        })}
      </ol>
    </div>
  );
}

export function inferLoadingActiveStep(elapsedMs: number): PipelineStepId {
  if (elapsedMs < 200) return 'received';
  if (elapsedMs < 900) return 'detect';
  if (elapsedMs < 1400) return 'mask';
  if (elapsedMs < 1700) return 'gate';
  return 'analysis';
}

export function buildLoadingSteps(activeStep: PipelineStepId): PipelineStepState[] {
  const order: PipelineStepId[] = ['received', 'detect', 'mask', 'gate', 'analysis'];
  const labels: Record<PipelineStepId, { label: string; description: string }> = {
    received: { label: 'Received', description: 'Message submitted to backend' },
    detect: { label: 'PII scan', description: 'Language + personal data detection' },
    mask: { label: 'Anonymize', description: 'Replace PII with [TYPE_N] placeholders' },
    gate: { label: 'Safety check', description: 'Re-scan masked text before LLM' },
    analysis: { label: 'Analysis', description: 'LLM on masked message only' },
  };

  const activeIndex = order.indexOf(activeStep);

  return order.map((id, index) => {
    let status: StepStatus = 'pending';
    if (index < activeIndex) status = 'complete';
    else if (index === activeIndex) status = 'active';

    return {
      id,
      ...labels[id],
      status,
    };
  });
}
