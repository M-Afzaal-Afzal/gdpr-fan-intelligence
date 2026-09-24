/** Human-readable duration formatting for pipeline timings. */

/** Format milliseconds as seconds (e.g. 847 ms → "0.85s", 2400 ms → "2.4s"). */
export function formatDurationSeconds(ms: number): string {
  const seconds = ms / 1000;
  if (seconds < 10) return `${seconds.toFixed(2)}s`;
  return `${seconds.toFixed(1)}s`;
}
