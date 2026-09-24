import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { SAMPLE_MESSAGES } from '@/lib/constants';

export default function DatasetPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Sample dataset</h1>
        <p className="max-w-2xl text-[var(--color-muted-foreground)]">
          The demo ships with representative fan messages: English, German, mixed, a no-PII hard
          negative, and a prompt-injection attempt. Try them on the demo page.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {SAMPLE_MESSAGES.map((sample) => (
          <Card key={sample.label}>
            <CardHeader>
              <div className="flex items-center justify-between gap-2">
                <CardTitle>{sample.label}</CardTitle>
                <Badge variant="outline">{sample.source.replace(/_/g, ' ')}</Badge>
              </div>
              <CardDescription>{sample.description}</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="rounded-lg bg-[var(--color-muted)] p-3 font-mono text-sm leading-relaxed">
                {sample.message}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
