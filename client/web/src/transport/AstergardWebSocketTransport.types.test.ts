import { expect, expectTypeOf, it, describe } from 'vitest';
import {
  createClientEnvelope,
  type TransportState,
} from './AstergardWebSocketTransport';
import type {
  AuthLoginPayload,
  CommandExecutePayload,
  ConnectionPingPayload,
  SessionHelloPayload,
} from '../protocol/webProtocol';

describe('AstergardWebSocketTransport payload types', () => {
  it('keeps payloads specific to each client message type', () => {
    const hello = createClientEnvelope('session.hello', { client: 'Astergard Web', client_version: 'D59.4', transport: 'websocket' }, 'req-1');
    expectTypeOf(hello.payload).toEqualTypeOf<SessionHelloPayload>();
    expect(hello.request_id).toBe('req-1');

    const auth = createClientEnvelope('auth.login', { username: 'ala', password: 'tajne' }, 'req-2');
    expectTypeOf(auth.payload).toEqualTypeOf<AuthLoginPayload>();

    const command = createClientEnvelope('command.execute', { command: 'look' }, 'req-3');
    expectTypeOf(command.payload).toEqualTypeOf<CommandExecutePayload>();

    const ping = createClientEnvelope('connection.ping', { nonce: 'n-1' }, 'req-4');
    expectTypeOf(ping.payload).toEqualTypeOf<ConnectionPingPayload>();

    const state: TransportState = 'ready';
    expect(state).toBe('ready');

    if (false) {
      // @ts-expect-error wrong payload for auth.login
      createClientEnvelope('auth.login', { command: 'look' }, 'req-x');
      // @ts-expect-error wrong payload for command.execute
      createClientEnvelope('command.execute', { username: 'ala', password: 'tajne' }, 'req-x');
      // @ts-expect-error wrong payload for connection.ping
      createClientEnvelope('connection.ping', { command: 'look' }, 'req-x');
      // @ts-expect-error request_id is required
      createClientEnvelope('session.hello', { client: 'Astergard Web' });
    }
  });
});
