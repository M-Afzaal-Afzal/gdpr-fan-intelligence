import { MetricsDashboard } from '@/components/MetricsDashboard';

export const dynamic = 'force-dynamic';

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-[var(--color-muted-foreground)]">
          Aggregated, privacy-safe analytics across every analyzed message.
        </p>
      </div>
      <MetricsDashboard />
    </div>
  );
}
