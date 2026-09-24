import { ShieldCheck, ShieldX } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import type { PrivacyStatus } from '@/lib/types';

export function PrivacyStatusBadge({ status }: { status: PrivacyStatus }) {
  if (status === 'safe_for_llm') {
    return (
      <Badge
        variant="outline"
        className="gap-1.5 border-[var(--color-privacy-safe)]/40 bg-[var(--color-privacy-safe)]/10 py-1 text-[var(--color-privacy-safe)]"
      >
        <ShieldCheck className="h-3.5 w-3.5" />
        Safe for LLM
      </Badge>
    );
  }
  return (
    <Badge
      variant="outline"
      className="gap-1.5 border-[var(--color-privacy-blocked)]/40 bg-[var(--color-privacy-blocked)]/10 py-1 text-[var(--color-privacy-blocked)]"
    >
      <ShieldX className="h-3.5 w-3.5" />
      Blocked
    </Badge>
  );
}
