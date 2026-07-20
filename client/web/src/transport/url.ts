export function buildWebSocketUrl(): string {
  const explicit = import.meta.env.VITE_ASTERGARD_WS_URL as string | undefined;
  if (explicit && explicit.trim()) {
    assertUrl(explicit.trim());
    return explicit.trim();
  }
  const fallback = 'ws://127.0.0.1:4001';
  assertUrl(fallback);
  return fallback;
}

function assertUrl(url: string): void {
  const parsed = new URL(url);
  if (import.meta.env.PROD && parsed.protocol !== 'wss:') {
    throw new Error('Production requires VITE_ASTERGARD_WS_URL to use wss://.');
  }
}
