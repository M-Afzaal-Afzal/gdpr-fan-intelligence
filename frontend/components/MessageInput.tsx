'use client';

import { Loader2, ShieldCheck } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { SOURCE_OPTIONS } from '@/lib/constants';
import type { LlmProviderId, LlmProviderOption, Source } from '@/lib/types';

interface MessageInputProps {
  message: string;
  source: Source;
  llmProvider: LlmProviderId;
  providerOptions: LlmProviderOption[];
  defaultProvider: LlmProviderId;
  loading: boolean;
  onMessageChange: (value: string) => void;
  onSourceChange: (value: Source) => void;
  onLlmProviderChange: (value: LlmProviderId) => void;
  onAnalyze: () => void;
}

function shortModelName(model: string): string {
  if (model.includes('/')) return model.split('/').pop() ?? model;
  return model;
}

function providerLabel(option: LlmProviderOption): string {
  const model = shortModelName(option.model);
  const suffix = option.configured ? '' : ' · not configured';
  return `${option.label} (${model})${suffix}`;
}

export function MessageInput({
  message,
  source,
  llmProvider,
  providerOptions,
  defaultProvider,
  loading,
  onMessageChange,
  onSourceChange,
  onLlmProviderChange,
  onAnalyze,
}: MessageInputProps) {
  const tooShort = message.trim().length > 0 && message.trim().length < 5;
  const disabled = loading || message.trim().length < 5;

  const options =
    providerOptions.length > 0
      ? providerOptions
      : [{ id: defaultProvider, label: defaultProvider, model: '—', configured: true }];

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <Label htmlFor="message">Fan message</Label>
        <Textarea
          id="message"
          value={message}
          onChange={(e) => onMessageChange(e.target.value)}
          placeholder="Paste one raw fan message. PII is detected and masked on the backend — never here."
          maxLength={5000}
          className="min-h-[160px] text-sm leading-relaxed"
        />
        <div className="flex justify-between text-xs text-[var(--color-muted-foreground)]">
          <span>{tooShort ? 'Minimum 5 characters' : 'Processed in-memory only'}</span>
          <span>{message.length}/5000</span>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="source">Source channel</Label>
          <Select value={source} onValueChange={(v) => onSourceChange(v as Source)}>
            <SelectTrigger id="source">
              <SelectValue placeholder="Select source" />
            </SelectTrigger>
            <SelectContent>
              {SOURCE_OPTIONS.map((opt) => (
                <SelectItem key={opt.value} value={opt.value}>
                  {opt.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="llm-provider">LLM provider</Label>
          <Select
            value={llmProvider}
            onValueChange={(v) => onLlmProviderChange(v as LlmProviderId)}
          >
            <SelectTrigger id="llm-provider">
              <SelectValue placeholder="Select provider" />
            </SelectTrigger>
            <SelectContent>
              {options.map((opt) => (
                <SelectItem
                  key={opt.id}
                  value={opt.id}
                  disabled={!opt.configured}
                  title={
                    opt.configured
                      ? 'API key configured on server'
                      : 'Add API key to backend .env to enable'
                  }
                >
                  {providerLabel(opt)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="text-xs text-[var(--color-muted-foreground)]">
            Server default: {defaultProvider}. Unconfigured providers fall back to stub.
          </p>
        </div>
      </div>

      <div className="flex justify-end border-t border-[var(--color-border)] pt-4">
        <Button onClick={onAnalyze} disabled={disabled} size="lg">
          {loading ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Running privacy pipeline…
            </>
          ) : (
            <>
              <ShieldCheck className="h-4 w-4" />
              Analyze safely
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
