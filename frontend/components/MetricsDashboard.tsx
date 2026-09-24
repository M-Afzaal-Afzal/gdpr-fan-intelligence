'use client';

import { useEffect, useState } from 'react';
import {
  Activity,
  AlertCircle,
  Ban,
  Clock,
  Languages,
  ListChecks,
  ShieldAlert,
} from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { getMetrics } from '@/lib/api';
import type { MetricsResponse } from '@/lib/types';
import { PrivacyStatusBadge } from './PrivacyStatusBadge';

function StatCard({
  icon,
  label,
  value,
  hint,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  hint?: string;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-[var(--color-muted-foreground)]">
          {label}
        </CardTitle>
        <span className="text-[var(--color-muted-foreground)]">{icon}</span>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold tabular-nums">{value}</div>
        {hint && <p className="mt-1 text-xs text-[var(--color-muted-foreground)]">{hint}</p>}
      </CardContent>
    </Card>
  );
}

function DistributionCard({
  title,
  icon,
  data,
}: {
  title: string;
  icon: React.ReactNode;
  data: Record<string, number>;
}) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const total = entries.reduce((acc, [, n]) => acc + n, 0) || 1;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-sm">
          {icon}
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {entries.length === 0 && (
          <p className="text-sm text-[var(--color-muted-foreground)]">No data yet.</p>
        )}
        {entries.map(([key, count]) => (
          <div key={key} className="space-y-1">
            <div className="flex justify-between text-sm">
              <span className="capitalize">{key.replace(/_/g, ' ')}</span>
              <span className="tabular-nums text-[var(--color-muted-foreground)]">{count}</span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-[var(--color-muted)]">
              <div
                className="h-full rounded-full bg-[var(--color-primary)]"
                style={{ width: `${(count / total) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

export function MetricsDashboard() {
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getMetrics()
      .then((m) => !cancelled && setMetrics(m))
      .catch((e) => !cancelled && setError(e?.message ?? 'Failed to load metrics'))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-28" />
        ))}
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Could not load metrics</AlertTitle>
        <AlertDescription>
          {error ?? 'Unknown error'}. Is the backend running on the configured API URL?
        </AlertDescription>
      </Alert>
    );
  }

  const avgLatency =
    metrics.average_latency_ms != null ? `${Math.round(metrics.average_latency_ms)} ms` : '—';

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          icon={<ListChecks className="h-4 w-4" />}
          label="Total analyzed"
          value={metrics.total_messages}
        />
        <StatCard
          icon={<ShieldAlert className="h-4 w-4" />}
          label="With PII detected"
          value={metrics.pii_detected_count}
        />
        <StatCard
          icon={<Ban className="h-4 w-4" />}
          label="Blocked before LLM"
          value={metrics.blocked_count}
        />
        <StatCard
          icon={<Clock className="h-4 w-4" />}
          label="Avg latency"
          value={avgLatency}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <DistributionCard
          title="Sentiment"
          icon={<Activity className="h-4 w-4" />}
          data={metrics.sentiment_distribution}
        />
        <DistributionCard
          title="Top topics"
          icon={<ListChecks className="h-4 w-4" />}
          data={metrics.topic_distribution}
        />
        <DistributionCard
          title="Language"
          icon={<Languages className="h-4 w-4" />}
          data={metrics.language_distribution}
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent safe results</CardTitle>
          <CardDescription>
            Only masked messages and analysis are stored — never raw PII.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {metrics.recent_results.length === 0 ? (
            <p className="text-sm text-[var(--color-muted-foreground)]">
              No results yet. Analyze a message on the home page.
            </p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Masked message</TableHead>
                  <TableHead>Lang</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Topic</TableHead>
                  <TableHead>Sentiment</TableHead>
                  <TableHead className="text-right">PII</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {metrics.recent_results.map((r) => (
                  <TableRow key={r.id}>
                    <TableCell className="max-w-[320px] truncate font-mono text-xs">
                      {r.masked_message}
                    </TableCell>
                    <TableCell className="uppercase">{r.language}</TableCell>
                    <TableCell>
                      <PrivacyStatusBadge status={r.privacy_status} />
                    </TableCell>
                    <TableCell className="capitalize">
                      {r.topic ? r.topic.replace(/_/g, ' ') : '—'}
                    </TableCell>
                    <TableCell className="capitalize">{r.sentiment ?? '—'}</TableCell>
                    <TableCell className="text-right tabular-nums">{r.pii_count}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
