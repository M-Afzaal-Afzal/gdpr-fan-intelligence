'use client';

import { useEffect, useState } from 'react';
import { AlertCircle } from 'lucide-react';
import { MessageInput } from '@/components/MessageInput';
import { PipelineResults, useRevealPhase } from '@/components/PipelineResults';
import { SampleMessageButtons } from '@/components/SampleMessageButtons';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { analyzeMessage, getLlmProviders } from '@/lib/api';
import type { AnalyzeResponse, LlmProviderId, LlmProviderOption, Source } from '@/lib/types';

const STEPS = [
  { n: '1', title: 'Scan', desc: 'Detect PII in raw messages' },
  { n: '2', title: 'Anonymize', desc: 'Replace with safe placeholders' },
  { n: '3', title: 'Analyze', desc: 'LLM sees masked text only' },
] as const;

export default function HomePage() {
  const [message, setMessage] = useState('');
  const [source, setSource] = useState<Source>('support_ticket');
  const [llmProvider, setLlmProvider] = useState<LlmProviderId>('stub');
  const [providerOptions, setProviderOptions] = useState<LlmProviderOption[]>([]);
  const [defaultProvider, setDefaultProvider] = useState<LlmProviderId>('stub');
  const [providersError, setProvidersError] = useState<string | null>(null);
  const [rawShown, setRawShown] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { revealPhase } = useRevealPhase(loading, result);

  useEffect(() => {
    getLlmProviders()
      .then((res) => {
        setProviderOptions(res.providers);
        setDefaultProvider(res.default);
        setLlmProvider(res.default);
        setProvidersError(null);
      })
      .catch(() => {
        setProvidersError('Could not load LLM providers — using server default.');
      });
  }, []);

  async function handleAnalyze() {
    setLoading(true);
    setError(null);
    setResult(null);
    setRawShown(message);
    try {
      const res = await analyzeMessage(message, source, llmProvider);
      setResult(res);
    } catch (e) {
      setError(
        e instanceof Error
          ? `${e.message}. Make sure the backend is running.`
          : 'Unexpected error',
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-8">
      <section className="space-y-4">
        <p className="text-xs font-medium uppercase tracking-wider text-[var(--color-primary)]">
          Privacy pipeline demo
        </p>
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">
          Analyze fan messages privately
        </h1>
        <p className="max-w-2xl text-sm leading-relaxed text-[var(--color-muted-foreground)]">
          PII is detected and anonymized on the server, re-scanned by a safety check, then only the
          masked text is sent to your chosen LLM. Keys never leave the backend.
        </p>

        <div className="grid gap-3 sm:grid-cols-3">
          {STEPS.map((step) => (
            <div
              key={step.n}
              className="rounded-lg border border-[var(--color-border)] bg-[var(--color-card)] px-4 py-3"
            >
              <p className="text-xs font-medium text-[var(--color-primary)]">{step.n}</p>
              <p className="mt-1 text-sm font-medium">{step.title}</p>
              <p className="mt-0.5 text-xs text-[var(--color-muted-foreground)]">{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      <Card>
        <CardHeader className="border-b border-[var(--color-border)]">
          <CardTitle className="text-lg font-semibold">Message intake</CardTitle>
          <CardDescription>
            Raw text, source channel, and LLM backend for this run.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6 pt-6">
          {providersError && (
            <Alert variant="warning">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{providersError}</AlertDescription>
            </Alert>
          )}
          <MessageInput
            message={message}
            source={source}
            llmProvider={llmProvider}
            providerOptions={providerOptions}
            defaultProvider={defaultProvider}
            loading={loading}
            onMessageChange={setMessage}
            onSourceChange={setSource}
            onLlmProviderChange={setLlmProvider}
            onAnalyze={handleAnalyze}
          />
          <SampleMessageButtons
            onPick={(sample) => {
              setMessage(sample.message);
              setSource(sample.source);
              setResult(null);
              setError(null);
            }}
          />
        </CardContent>
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Analysis failed</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <PipelineResults rawShown={rawShown} result={result} revealPhase={revealPhase} />
    </div>
  );
}
