import { ShieldAlert } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import type { DetectedPii } from '@/lib/types';

export function PiiEntityTable({ entities }: { entities: DetectedPii[] }) {
  if (entities.length === 0) {
    return (
      <p className="text-sm text-[var(--color-muted-foreground)]">
        No PII detected in this message.
      </p>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Type</TableHead>
          <TableHead>Replacement</TableHead>
          <TableHead className="text-right">Span</TableHead>
          <TableHead className="text-right">Confidence</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {entities.map((e, i) => (
          <TableRow key={`${e.type}-${e.start}-${i}`}>
            <TableCell>
              <Badge variant="secondary" className="gap-1">
                <ShieldAlert className="h-3 w-3" />
                {e.type}
              </Badge>
            </TableCell>
            <TableCell>
              <code className="rounded bg-[var(--color-muted)] px-1.5 py-0.5 text-xs">
                {e.replacement}
              </code>
            </TableCell>
            <TableCell className="text-right text-xs text-[var(--color-muted-foreground)]">
              {e.start}–{e.end}
            </TableCell>
            <TableCell className="text-right tabular-nums">
              {(e.confidence * 100).toFixed(0)}%
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
