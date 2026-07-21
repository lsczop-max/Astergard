import { beforeEach, describe, expect, it } from 'vitest';
import { AstergardWebSocketTransport } from './AstergardWebSocketTransport';
import { MockWebSocket } from '../test/mockWebSocket';
import { parseProtocolEnvelope, serializeWebEnvelope } from '../protocol/webProtocol';

beforeEach(() => {
  MockWebSocket.instances = [];
});

function makeTransport() {
  return new AstergardWebSocketTransport('ws://127.0.0.1:4001', (url, protocol) => new MockWebSocket(url, protocol) as unknown as WebSocket);
}

describe('protocol parser', () => {
  it('rejects wrong version', () => {
    expect(() =>
      parseProtocolEnvelope('{"version":2,"type":"session.ready","payload":{"transport":"websocket"},"sequence":1}'),
    ).toThrow(/Unsupported protocol version/);
  });

  it('rejects unknown type', () => {
    expect(() =>
      parseProtocolEnvelope('{"version":1,"type":"unknown.event","payload":{},"request_id":"1"}'),
    ).toThrow(/Unknown protocol message type/);
  });
});

describe('transport', () => {
  it('sends hello on open and blocks command before ready', async () => {
    const transport = makeTransport();
    transport.connect();
    const socket = MockWebSocket.instances[0];
    socket.open();
    const hello = parseProtocolEnvelope(socket.sent[0]);
    expect(hello).toEqual({
      version: 1,
      type: 'session.hello',
      payload: {
        client: 'Astergard Web',
        client_version: 'D59.4',
        transport: 'websocket',
      },
      request_id: hello.request_id,
    });
    expect(hello.request_id).toMatch(/^req-/);
    expect(Object.prototype.hasOwnProperty.call(hello, 'sequence')).toBe(false);
    await expect(transport.executeCommand('spojrz')).rejects.toThrow(/dopiero po zalogowaniu/);
  });

  it('carries request ids for login, command and ping', async () => {
    const transport = makeTransport();
    transport.connect();
    const socket = MockWebSocket.instances[0];
    socket.open();
    await transport.submitLogin('ala', 'tajne');
    await transport.ping('nonce');
    socket.message(serializeWebEnvelope({ version: 1, type: 'session.ready', payload: { transport: 'websocket' }, sequence: 1 }));
    await transport.executeCommand('spojrz');
    const login = parseProtocolEnvelope(socket.sent[1]);
    const ping = parseProtocolEnvelope(socket.sent[2]);
    const command = parseProtocolEnvelope(socket.sent[3]);
    expect(login.request_id).toMatch(/^req-/);
    expect(login.type).toBe('auth.login');
    expect(login.payload).toEqual({ username: 'ala', password: 'tajne' });
    expect(ping.type).toBe('connection.ping');
    expect(ping.payload).toEqual({ nonce: 'nonce' });
    expect(command.type).toBe('command.execute');
    expect(command.payload).toEqual({ command: 'spojrz' });
  });

  it('rejects whitespace-only command envelopes before sending', async () => {
    const transport = makeTransport();
    transport.connect();
    const socket = MockWebSocket.instances[0];
    socket.open();
    socket.message(serializeWebEnvelope({ version: 1, type: 'session.ready', payload: { transport: 'websocket' }, sequence: 1 }));

    await expect(transport.executeCommand('   ')).rejects.toThrow(/non-whitespace characters/);
    expect(socket.sent).toHaveLength(1);
  });

  it('carries request ids for creator flow and keeps password out of terminal state', async () => {
    const transport = makeTransport();
    const messages: string[] = [];
    transport.subscribe((event) => {
      if (event.kind === 'message') {
        messages.push(event.message.type);
      }
    });
    transport.connect();
    const socket = MockWebSocket.instances[0];
    socket.open();
    await transport.startCreator('nowa', 'sekret');
    const start = parseProtocolEnvelope(socket.sent[1]);
    expect(start.type).toBe('creator.start');
    expect(start.payload).toEqual({ username: 'nowa', password: 'sekret' });
    socket.message(
      serializeWebEnvelope({
        version: 1,
        type: 'creator.started',
        payload: {
          username: 'nowa',
          step: {
            step_id: 'name',
            title: 'Imię',
            prompt: '— Jak cię zwać?',
            input_type: 'text',
            back_available: false,
            cancel_available: true,
          },
        },
        request_id: start.request_id,
        sequence: 1,
      }),
    );
    await transport.submitCreator('name', 'Ala');
    const submit = parseProtocolEnvelope(socket.sent[2]);
    expect(submit.type).toBe('creator.submit');
    expect(submit.payload).toEqual({ step_id: 'name', value: 'Ala' });
    expect(messages).toContain('creator.started');
  });

  it('forwards character.vitals without request correlation noise', () => {
    const transport = makeTransport();
    const messages: string[] = [];
    const errors: string[] = [];
    transport.subscribe((event) => {
      if (event.kind === 'message') {
        messages.push(event.message.type);
      }
      if (event.kind === 'error') {
        errors.push(event.message);
      }
    });
    transport.connect();
    const socket = MockWebSocket.instances[0];
    socket.open();
    socket.message(serializeWebEnvelope({ version: 1, type: 'session.ready', payload: { transport: 'websocket' }, sequence: 1 }));
    socket.message(
      serializeWebEnvelope({
        version: 1,
        type: 'character.vitals',
        payload: {
          condition_current: 12,
          condition_max: 12,
          condition_label: 'jest w pełni sił',
          stamina_current: 100,
          stamina_max: 100,
          stamina_label: 'Jesteś w pełni sił.',
        },
        sequence: 2,
      }),
    );

    expect(errors).toEqual([]);
    expect(messages).toContain('character.vitals');
    expect(transport.getState()).toBe('ready');
  });

  it('correlates creator.finished with the final submit request and reaches ready without auth.result', async () => {
    const transport = makeTransport();
    const messages: string[] = [];
    const errors: string[] = [];
    transport.subscribe((event) => {
      if (event.kind === 'message') {
        messages.push(event.message.type);
      }
      if (event.kind === 'error') {
        errors.push(event.message);
      }
    });
    transport.connect();
    const socket = MockWebSocket.instances[0];
    socket.open();

    await transport.startCreator('nowa', 'sekret');
    const start = parseProtocolEnvelope(socket.sent[1]);
    socket.message(
      serializeWebEnvelope({
        version: 1,
        type: 'creator.started',
        payload: {
          username: 'nowa',
          step: {
            step_id: 'gait',
            title: 'Chód',
            prompt: '— Jak się poruszasz?',
            input_type: 'choice',
            choices: [
              { value: 'spokojny', label: 'spokojny' },
            ],
            back_available: true,
            cancel_available: true,
          },
        },
        request_id: start.request_id,
        sequence: 1,
      }),
    );

    await transport.submitCreator('gait', 'spokojny');
    const submit = parseProtocolEnvelope(socket.sent[2]);
    socket.message(
      serializeWebEnvelope({
        version: 1,
        type: 'creator.finished',
        payload: { username: 'nowa', character_name: 'Ala' },
        request_id: submit.request_id,
        sequence: 2,
      }),
    );
    socket.message(
      serializeWebEnvelope({
        version: 1,
        type: 'output.text',
        payload: { text: 'Witaj' },
        sequence: 3,
      }),
    );
    socket.message(
      serializeWebEnvelope({
        version: 1,
        type: 'room.info',
        payload: {
          num: 1,
          name: 'Start',
          area: 'Astergard',
          coords: { x: 0, y: 0, z: 0 },
          exits: {},
        },
        sequence: 4,
      }),
    );
    socket.message(
      serializeWebEnvelope({
        version: 1,
        type: 'output.prompt',
        payload: { prompt: '> ' },
        sequence: 5,
      }),
    );
    socket.message(
      serializeWebEnvelope({
        version: 1,
        type: 'session.ready',
        payload: { transport: 'websocket', username: 'nowa' },
        sequence: 6,
      }),
    );

    expect(errors).toEqual([]);
    expect(messages).toContain('creator.finished');
    expect(messages).toContain('session.ready');
    expect(messages).not.toContain('auth.result');
    expect(transport.getState()).toBe('ready');
  });

  it('rejects duplicate, gap, and regression sequence', () => {
    const transport = makeTransport();
    const events: string[] = [];
    transport.subscribe((event) => {
      if (event.kind === 'error') {
        events.push(event.message);
      }
    });
    transport.connect();
    const socket = MockWebSocket.instances[0];
    socket.open();
    socket.message(serializeWebEnvelope({ version: 1, type: 'session.ready', payload: { transport: 'websocket' }, sequence: 1 }));
    socket.message(serializeWebEnvelope({ version: 1, type: 'output.text', payload: { text: 'a' }, sequence: 1 }));
    socket.message(serializeWebEnvelope({ version: 1, type: 'output.text', payload: { text: 'b' }, sequence: 3 }));
    expect(events.join(' ')).toMatch(/sekwencję/);
  });

  it('handles login success and failure', () => {
    const successTransport = makeTransport();
    const successStates: string[] = [];
    successTransport.subscribe((event) => {
      if (event.kind === 'state') {
        successStates.push(event.state);
      }
    });
    successTransport.connect();
    const successSocket = MockWebSocket.instances[0];
    successSocket.open();
    void successTransport.submitLogin('ala', 'tajne');
    const successLogin = parseProtocolEnvelope(successSocket.sent[1]);
    successSocket.message(
      serializeWebEnvelope({
        version: 1,
        type: 'auth.result',
        payload: { success: true, username: 'ala' },
        request_id: successLogin.request_id,
        sequence: 1,
      }),
    );
    successSocket.message(
      serializeWebEnvelope({
        version: 1,
        type: 'session.ready',
        payload: { transport: 'websocket', username: 'ala' },
        sequence: 2,
      }),
    );
    expect(successStates).toContain('ready');

    const failureTransport = makeTransport();
    const failureErrors: string[] = [];
    failureTransport.subscribe((event) => {
      if (event.kind === 'error') {
        failureErrors.push(event.message);
      }
    });
    failureTransport.connect();
    const failureSocket = MockWebSocket.instances[1];
    failureSocket.open();
    void failureTransport.submitLogin('ala', 'tajne');
    const failureLogin = parseProtocolEnvelope(failureSocket.sent[1]);
    failureSocket.message(
      serializeWebEnvelope({
        version: 1,
        type: 'auth.result',
        payload: { success: false, username: 'ala', reason: 'invalid_credentials' },
        request_id: failureLogin.request_id,
        sequence: 1,
      }),
    );
    expect(failureErrors.join(' ')).toMatch(/Logowanie nie powiodło się/);
  });

  it('cleans up listeners on reconnect', () => {
    const transport = makeTransport();
    transport.connect();
    const first = MockWebSocket.instances[0];
    first.open();
    transport.connect();
    const second = MockWebSocket.instances[1];
    expect(first.closeCalls.length).toBeGreaterThan(0);
    expect(second.url).toBe('ws://127.0.0.1:4001');
  });

  it('moves through close and error states', () => {
    const transport = makeTransport();
    const states: string[] = [];
    transport.subscribe((event) => {
      if (event.kind === 'state') {
        states.push(event.state);
      }
    });
    transport.connect();
    const socket = MockWebSocket.instances[0];
    socket.open();
    transport.close();
    expect(states).toContain('closing');
    expect(states).toContain('disconnected');
    transport.connect();
    const secondSocket = MockWebSocket.instances[1];
    secondSocket.open();
    secondSocket.dispatch('close', { code: 1011, reason: 'boom' });
    expect(states).toContain('error');
  });
});
