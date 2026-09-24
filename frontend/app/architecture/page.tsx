import {
  ArrowRight,
  BarChart3,
  Database,
  Globe,
  ScanSearch,
  Server,
  ShieldCheck,
  Sparkles,
  Wand2,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const STEPS = [
  { icon: Globe, label: 'User', sub: 'enters one fan message' },
  { icon: Server, label: 'Next.js', sub: 'sends raw text only' },
  { icon: Server, label: 'FastAPI', sub: 'validates request' },
  { icon: ScanSearch, label: 'PII Detection', sub: 'regex + Presidio + DE rules' },
  { icon: Wand2, label: 'Masking', sub: 'readable placeholders' },
  { icon: ShieldCheck, label: 'Safety Gate', sub: '2nd PII scan' },
  { icon: Sparkles, label: 'LLM', sub: 'masked text only' },
  { icon: Database, label: 'PostgreSQL', sub: 'no raw PII' },
  { icon: BarChart3, label: 'Dashboard', sub: 'safe analytics' },
];

const RULES = [
  'Raw PII never reaches the LLM.',
  'Raw PII is never stored in PostgreSQL.',
  'Logs never contain raw PII.',
  'PII entity values are never persisted (no entity_value column).',
  'Only masked messages, PII metadata, analysis, latency, status, timestamps are stored.',
  'A second PII scan runs on the masked message before the LLM call.',
  'A final PII scan runs on the LLM output before display or storage.',
  'If masking is incomplete, the LLM call is blocked.',
  'The frontend never runs PII detection.',
  'The frontend never holds LLM secrets.',
];

export default function ArchitecturePage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Architecture</h1>
        <p className="max-w-2xl text-[var(--color-muted-foreground)]">
          Privacy is the first step of the pipeline, not a final check. Each stage runs inside one
          controlled Python backend before any LLM call.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Pipeline flow</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-stretch gap-2">
            {STEPS.map((step, i) => (
              <div key={step.label} className="flex items-center gap-2">
                <div className="flex w-[120px] flex-col items-center gap-1 rounded-lg border border-[var(--color-border)] bg-[var(--color-muted)]/40 p-3 text-center">
                  <step.icon className="h-5 w-5 text-[var(--color-primary)]" />
                  <span className="text-sm font-semibold">{step.label}</span>
                  <span className="text-[10px] leading-tight text-[var(--color-muted-foreground)]">
                    {step.sub}
                  </span>
                </div>
                {i < STEPS.length - 1 && (
                  <ArrowRight className="h-4 w-4 shrink-0 text-[var(--color-muted-foreground)]" />
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-[var(--color-success)]" />
              Hard privacy rules
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ol className="space-y-2 text-sm">
              {RULES.map((rule, i) => (
                <li key={i} className="flex gap-2">
                  <span className="font-mono text-[var(--color-muted-foreground)]">{i + 1}.</span>
                  <span>{rule}</span>
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Why a single Python backend?</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm leading-relaxed text-[var(--color-muted-foreground)]">
            <p>
              The privacy engine (Presidio + regex + custom rules) is Python-native. Keeping
              detection, masking, the safety gate, the LLM client, and storage in one FastAPI
              service means raw PII stays inside a single controlled boundary.
            </p>
            <p>
              The Next.js frontend only ever sends the raw message and renders the structured
              response. It holds no secrets and runs no detection — so a compromised browser cannot
              leak the analysis keys or bypass masking.
            </p>
            <p className="rounded-lg bg-[var(--color-accent)]/60 p-3 text-[var(--color-accent-foreground)]">
              Demo line: &ldquo;A fan message is anonymized in the backend; a safety gate confirms no
              PII remains; only then does the LLM see the masked text.&rdquo;
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
