import { afterEach, describe, expect, it, vi } from 'vitest';
import { buildWebSocketUrl } from './url';

afterEach(() => {
  vi.unstubAllEnvs();
});

describe('buildWebSocketUrl', () => {
  it('uses the developer fallback when env is unset', () => {
    vi.stubEnv('VITE_ASTERGARD_WS_URL', '');
    expect(buildWebSocketUrl()).toBe('ws://127.0.0.1:4001');
  });

  it('uses the explicit websocket URL', () => {
    vi.stubEnv('VITE_ASTERGARD_WS_URL', 'wss://example.org/astergard');
    expect(buildWebSocketUrl()).toBe('wss://example.org/astergard');
  });
});
