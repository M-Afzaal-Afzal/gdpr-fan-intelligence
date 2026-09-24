import { Activity, Flag, Lightbulb, MessageSquareText, Tag } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import type { Analysis, Sentiment, Urgency } from '@/lib/types';

function sentimentVariant(s: Sentiment): 'success' | 'secondary' | 'destructive' {
  if (s === 'positive') return 'success';
  if (s === 'negative') return 'destructive';
  return 'secondary';
}

function urgencyVariant(u: Urgency): 'secondary' | 'warning' | 'destructive' {
  if (u === 'high') return 'destructive';
  if (u === 'medium') return 'warning';
  return 'secondary';
}

function humanize(value: string) {
  return value.replace(/_/g, ' ');
}

export function AiInsightCard({ analysis }: { analysis: Analysis }) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap gap-2">
        <Badge variant={sentimentVariant(analysis.sentiment)} className="gap-1">
          <Activity className="h-3 w-3" />
          {analysis.sentiment}
        </Badge>
        <Badge variant="outline" className="gap-1">
          <Tag className="h-3 w-3" />
          {humanize(analysis.topic)}
        </Badge>
        <Badge variant="outline" className="gap-1">
          <MessageSquareText className="h-3 w-3" />
          {humanize(analysis.intent)}
        </Badge>
        <Badge variant={urgencyVariant(analysis.urgency)} className="gap-1">
          <Flag className="h-3 w-3" />
          {analysis.urgency} urgency
        </Badge>
      </div>

      <Separator />

      <div className="space-y-1">
        <p className="text-xs font-medium uppercase tracking-wide text-[var(--color-muted-foreground)]">
          Summary
        </p>
        <p className="text-sm leading-relaxed">{analysis.summary}</p>
      </div>

      <div className="space-y-1 rounded-lg border border-[var(--color-border)] bg-[var(--color-muted)]/50 p-3">
        <p className="flex items-center gap-1.5 text-xs font-medium uppercase tracking-wide text-[var(--color-muted-foreground)]">
          <Lightbulb className="h-3.5 w-3.5" />
          Recommended action
        </p>
        <p className="text-sm leading-relaxed">{analysis.recommended_action}</p>
      </div>
    </div>
  );
}
