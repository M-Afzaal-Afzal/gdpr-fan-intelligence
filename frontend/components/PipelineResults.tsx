'use client';

import { useEffect, useMemo, useState } from 'react';
import { Ban, FileText, Lock, ScanSearch } from 'lucide-react';
import { motion } from 'framer-motion';
import { HighlightCard } from '@/components/aceternity/moving-border';
import { AiInsightCard } from '@/components/AiInsightCard';
import { MaskedMessageCard } from '@/components/MaskedMessageCard';
import { PiiEntityTable } from '@/components/PiiEntityTable';
import {
  buildLoadingSteps,
  inferLoadingActiveStep,
  PipelineStepper,
  type PipelineStepState,
} from '@/components/PipelineStepper';
import { PrivacyStatusBadge } from '@/components/PrivacyStatusBadge';
import { TimingBadges } from '@/components/TimingBadges';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { formatDurationSeconds } from '@/lib/format';
import type { AnalyzeResponse } from '@/lib/types';

export type RevealPhase = 'idle' | 'loading' | 'masked' | 'complete';

interface PipelineResultsProps {
  rawShown: string;
  result: AnalyzeResponse | null;
  revealPhase: RevealPhase;
}

function modelLabel(result: AnalyzeResponse): string {
  if (!result.llm_provider) return 'stub';
  const model = result.llm_model ?? '';
  const shortModel = model.includes('/') ? model.split('/').pop()! : model;
  return shortModel ? `${result.llm_provider} · ${shortModel}` : result.llm_provider;
}

function buildResultSteps(result: AnalyzeResponse, revealPhase: RevealPhase): PipelineStepState[] {
  const { pipeline_timing: t } = result;
  const blocked = result.privacy_status === 'blocked';
  const analysisSkipped = !result.llm_called;

  const analysisStatus = (): PipelineStepState['status'] => {
    if (revealPhase === 'masked') {
      if (blocked) return 'blocked';
      if (analysisSkipped) return 'skipped';
      return 'active';
    }
    if (blocked) return 'blocked';
    if (analysisSkipped) return 'skipped';
    return 'complete';
  };

  return [
    {
      id: 'received',
      label: 'Received',
      description: 'Message submitted to backend',
      status: 'complete',
    },
    {
      id: 'detect',
      label: 'PII scan',
      description: `${result.detected_pii.length} entit${result.detected_pii.length === 1 ? 'y' : 'ies'} found`,
      status: 'complete',
      timingMs: t.detect_ms,
    },
    {
      id: 'mask',
      label: 'Anonymize',
      description: 'PII replaced with [TYPE_N] placeholders',
      status: 'complete',
      timingMs: t.mask_ms,
    },
    {
      id: 'gate',
      label: 'Safety check',
      description: blocked
        ? (result.reason ?? 'PII still detected after masking')
        : 'Re-scan passed — LLM allowed',
      status: blocked ? 'blocked' : 'complete',
      timingMs: t.safety_gate_ms,
    },
    {
      id: 'analysis',
      label: 'Analysis',
      description: blocked
        ? 'LLM not called — gate blocked'
        : analysisSkipped
          ? 'LLM unavailable or failed'
          : `${modelLabel(result)} · masked text only`,
      status: analysisStatus(),
      timingMs: t.llm_ms,
    },
  ];
}

function revealDelayMs(result: AnalyzeResponse): number {
  if (result.privacy_status === 'blocked') return 0;
  const llmMs = result.pipeline_timing.llm_ms;
  if (llmMs === null || llmMs === 0) return 200;
  return Math.min(400, Math.max(200, Math.round(llmMs * 0.05)));
}

export function useRevealPhase(
  loading: boolean,
  result: AnalyzeResponse | null,
): { revealPhase: RevealPhase } {
  const [revealPhase, setRevealPhase] = useState<RevealPhase>('idle');

  useEffect(() => {
    if (loading) {
      setRevealPhase('loading');
      return;
    }
    if (!result) {
      setRevealPhase('idle');
      return;
    }

    setRevealPhase('masked');
    const delay = revealDelayMs(result);
    const timer = window.setTimeout(() => setRevealPhase('complete'), delay);
    return () => window.clearTimeout(timer);
  }, [loading, result]);

  return { revealPhase };
}

export function PipelineResults({ rawShown, result, revealPhase }: PipelineResultsProps) {
  const [elapsedMs, setElapsedMs] = useState(0);

  useEffect(() => {
    if (revealPhase !== 'loading') {
      setElapsedMs(0);
      return;
    }

    const start = performance.now();
    const tick = () => setElapsedMs(Math.round(performance.now() - start));
    tick();
    const id = window.setInterval(tick, 50);
    return () => window.clearInterval(id);
  }, [revealPhase]);

  const steps = useMemo(() => {
    if (revealPhase === 'loading') {
      return buildLoadingSteps(inferLoadingActiveStep(elapsedMs));
    }
    if (result) {
      return buildResultSteps(result, revealPhase);
    }
    return [];
  }, [revealPhase, elapsedMs, result]);

  if (revealPhase === 'idle') return null;

  const showMaskedContent = result && (revealPhase === 'masked' || revealPhase === 'complete');
  const showAnalysis = result && revealPhase === 'complete';
  const blocked = result?.privacy_status === 'blocked';

  return (
    <div className="grid gap-6 lg:grid-cols-[minmax(240px,280px)_1fr]">
      <div className="h-fit rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] p-4 lg:sticky lg:top-16">
        <PipelineStepper
          steps={steps}
          elapsedMs={revealPhase === 'loading' ? elapsedMs : undefined}
        />
      </div>

      <div className="space-y-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-base font-semibold">
              <FileText className="h-4 w-4 text-[var(--color-muted-foreground)]" />
              Raw input
            </CardTitle>
            <CardDescription>Processed in-memory only — never stored.</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="whitespace-pre-wrap break-words text-sm leading-relaxed">{rawShown}</p>
          </CardContent>
        </Card>

        {showMaskedContent && result && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-4"
          >
            <div className="flex flex-wrap items-center gap-3 rounded-xl border border-[var(--color-border)] bg-[var(--color-card)] p-4">
              <PrivacyStatusBadge status={result.privacy_status} />
              <Badge variant="outline">{result.language}</Badge>
              <TimingBadges timing={result.pipeline_timing} compact />
            </div>

            {blocked && (
              <Alert variant="warning">
                <Ban className="h-4 w-4" />
                <AlertTitle>LLM call blocked by safety gate</AlertTitle>
                <AlertDescription>
                  {result.reason ?? 'PII still detected after masking.'} The masked message was not
                  sent to the LLM.
                </AlertDescription>
              </Alert>
            )}

            <HighlightCard accent="mask">
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base font-semibold">
                  <Lock className="h-4 w-4 text-[var(--color-mask-highlight)]" />
                  Masked safe message
                </CardTitle>
                <CardDescription>
                  Anonymized in {formatDurationSeconds(result.pipeline_timing.mask_ms)} — only
                  text the LLM can see.
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-0">
                <MaskedMessageCard message={result.masked_message} />
              </CardContent>
            </HighlightCard>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base font-semibold">
                  <ScanSearch className="h-4 w-4 text-[var(--color-muted-foreground)]" />
                  Detected PII
                </CardTitle>
                <CardDescription>
                  {result.detected_pii.length} entit
                  {result.detected_pii.length === 1 ? 'y' : 'ies'} — values are not stored.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <PiiEntityTable entities={result.detected_pii} />
              </CardContent>
            </Card>
          </motion.div>
        )}

        {revealPhase === 'loading' && (
          <Card className="border-dashed bg-transparent">
            <CardContent className="py-10 text-center text-sm text-[var(--color-muted-foreground)]">
              Running privacy pipeline on the server…
            </CardContent>
          </Card>
        )}

        {showAnalysis && result && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base font-semibold">Fan intelligence</CardTitle>
                <CardDescription>
                  {result.analysis
                    ? `Analysis result · ${modelLabel(result)}`
                    : 'Not available for this message.'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                {result.analysis ? (
                  <AiInsightCard analysis={result.analysis} />
                ) : (
                  <p className="text-sm text-[var(--color-muted-foreground)]">
                    {blocked
                      ? 'No analysis — the safety gate blocked the LLM call.'
                      : 'No analysis — the LLM was unavailable or returned an error.'}
                  </p>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}

        {revealPhase === 'masked' && result && !blocked && (
          <Card className="border-dashed bg-transparent">
            <CardContent className="flex items-center justify-center gap-2 py-8 text-sm text-[var(--color-muted-foreground)]">
              <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-[var(--color-pipeline-active)] border-t-transparent" />
              Preparing analysis result…
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
