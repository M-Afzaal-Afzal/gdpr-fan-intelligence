/** Zod schemas for client-side form validation only. */

import { z } from 'zod';

export const SourceSchema = z.enum([
  'support_ticket',
  'email',
  'social_media',
  'app_review',
  'forum',
  'other',
]);

export const AnalyzeRequestSchema = z.object({
  message: z
    .string()
    .min(5, 'Message must be at least 5 characters')
    .max(5000, 'Message must be at most 5000 characters'),
  source: SourceSchema.default('other'),
});

export type AnalyzeRequest = z.infer<typeof AnalyzeRequestSchema>;
