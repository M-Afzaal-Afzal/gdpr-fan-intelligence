import type { Metadata } from 'next';
import { DM_Sans, JetBrains_Mono } from 'next/font/google';
import './globals.css';
import { SiteNav } from '@/components/SiteNav';

const dmSans = DM_Sans({
  subsets: ['latin'],
  variable: '--font-body',
  weight: ['400', '500', '600', '700'],
  display: 'swap',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono-face',
  weight: ['400', '500'],
  display: 'swap',
});

export const metadata: Metadata = {
  title: 'Raumdeuter · Privacy-First Fan Intelligence',
  description:
    'GDPR-safe pipeline for football fan messages. PII is detected and masked before any LLM call.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${dmSans.variable} ${jetbrainsMono.variable}`}>
      <body className="antialiased">
        <SiteNav />
        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
        <footer className="mx-auto max-w-6xl border-t border-[var(--color-border)] px-4 py-6 text-center text-xs text-[var(--color-muted-foreground)]">
          Raw PII never reaches the LLM · never stored
        </footer>
      </body>
    </html>
  );
}
