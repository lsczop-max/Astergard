import { fireEvent, render, screen } from '@testing-library/react';
import { StrictMode, act } from 'react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { App } from './App';
import { MockWebSocket } from '../test/mockWebSocket';
import { parseProtocolEnvelope } from '../protocol/webProtocol';

beforeEach(() => {
  MockWebSocket.instances = [];
  vi.stubGlobal('WebSocket', MockWebSocket as unknown as typeof WebSocket);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('App StrictMode transport lifecycle', () => {
  it('keeps login active after hello and before ready while blocking command bar', async () => {
    const user = userEvent.setup();
    render(<App />);

    const socket = MockWebSocket.instances[0];

    await act(async () => {
      socket.open();
      socket.message(
        JSON.stringify({
          version: 1,
          type: 'output.text',
          payload: { text: 'Karczmarz podnosi wzrok znad kufla. Jak się przedstawiasz?' },
          sequence: 1,
        }),
      );
    });

    expect(parseProtocolEnvelope(socket.sent[0])).toMatchObject({
      version: 1,
      type: 'session.hello',
    });

    expect(screen.getByLabelText('Nazwa użytkownika')).toBeEnabled();
    expect(screen.getByLabelText('Hasło')).toBeEnabled();
    expect(screen.getByLabelText('Nowa postać')).toBeEnabled();
    expect(screen.getByLabelText('Komenda')).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Zaloguj' })).toBeDisabled();

    await user.type(screen.getByLabelText('Nazwa użytkownika'), 'ala');
    await user.type(screen.getByLabelText('Hasło'), 'tajne');

    expect(screen.getByRole('button', { name: 'Zaloguj' })).toBeEnabled();
    expect(screen.getByRole('main')).not.toHaveTextContent('tajne');

    await user.click(screen.getByRole('button', { name: 'Zaloguj' }));

    expect(socket.sent).toHaveLength(2);
    expect(parseProtocolEnvelope(socket.sent[1])).toMatchObject({
      version: 1,
      type: 'auth.login',
      request_id: expect.any(String),
      payload: {
        username: 'ala',
        password: 'tajne',
      },
    });
    expect(screen.getByRole('main')).not.toHaveTextContent('tajne');
  });

  it('maps numpad movement only after ready and ignores interactive focus', async () => {
    const user = userEvent.setup();
    render(<App />);

    const socket = MockWebSocket.instances[0];

    await act(async () => {
      socket.open();
      socket.message(
        JSON.stringify({
          version: 1,
          type: 'output.text',
          payload: { text: 'Karczmarz podnosi wzrok znad kufla. Jak się przedstawiasz?' },
          sequence: 1,
        }),
      );
    });

    await user.type(screen.getByLabelText('Nazwa użytkownika'), 'ala');
    await user.type(screen.getByLabelText('Hasło'), 'tajne');
    await user.click(screen.getByRole('button', { name: 'Zaloguj' }));

    const login = parseProtocolEnvelope(socket.sent[1]);

    await act(async () => {
      socket.message(
        JSON.stringify({
          version: 1,
          type: 'auth.result',
          payload: { success: true, username: 'ala' },
          request_id: login.request_id,
          sequence: 2,
        }),
      );
      socket.message(
        JSON.stringify({
          version: 1,
          type: 'output.text',
          payload: { text: 'Witaj' },
          sequence: 3,
        }),
      );
      socket.message(
        JSON.stringify({
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
        JSON.stringify({
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
          sequence: 5,
        }),
      );
      socket.message(
        JSON.stringify({
          version: 1,
          type: 'output.prompt',
          payload: { prompt: '> ' },
          sequence: 6,
        }),
      );
      socket.message(
        JSON.stringify({
          version: 1,
          type: 'session.ready',
          payload: { transport: 'websocket', username: 'ala' },
          sequence: 7,
        }),
      );
    });

    const initialSentLength = socket.sent.length;
    fireEvent.keyDown(document.body, { code: 'Numpad8', key: '8' });
    expect(socket.sent).toHaveLength(initialSentLength + 1);
    expect(parseProtocolEnvelope(socket.sent.at(-1) as string)).toMatchObject({
      version: 1,
      type: 'command.execute',
      payload: { command: 'polnoc' },
    });

    const commandInput = screen.getByLabelText('Komenda');
    commandInput.focus();
    fireEvent.keyDown(commandInput, { code: 'Numpad9', key: '9' });
    expect(socket.sent).toHaveLength(initialSentLength + 1);
  });

  it('replaces the trial transport and keeps the second connection active', () => {
    const { unmount } = render(
      <StrictMode>
        <App />
      </StrictMode>,
    );

    expect(MockWebSocket.instances).toHaveLength(2);

    const firstSocket = MockWebSocket.instances[0];
    const secondSocket = MockWebSocket.instances[1];

    expect(firstSocket.closeCalls).toHaveLength(1);
    expect(firstSocket.closeCalls[0]).toEqual({ code: 1000, reason: 'reconnect' });
    expect(firstSocket.listeners.get('open')?.size ?? 0).toBe(0);
    expect(firstSocket.listeners.get('message')?.size ?? 0).toBe(0);
    expect(firstSocket.listeners.get('close')?.size ?? 0).toBe(0);
    expect(firstSocket.listeners.get('error')?.size ?? 0).toBe(0);

    expect(firstSocket.sent).toHaveLength(0);

    act(() => {
      secondSocket.open();
    });
    expect(secondSocket.sent).toHaveLength(1);
    expect(parseProtocolEnvelope(secondSocket.sent[0])).toMatchObject({
      version: 1,
      type: 'session.hello',
      payload: {
        client: 'Astergard Web',
        client_version: 'D59.4',
        transport: 'websocket',
      },
    });
    expect(MockWebSocket.instances).toHaveLength(2);

    act(() => {
      unmount();
    });

    expect(secondSocket.closeCalls).toHaveLength(1);
    expect(secondSocket.closeCalls[0]).toEqual({ code: 1000, reason: 'reconnect' });
    expect(secondSocket.listeners.get('open')?.size ?? 0).toBe(0);
    expect(secondSocket.listeners.get('message')?.size ?? 0).toBe(0);
    expect(secondSocket.listeners.get('close')?.size ?? 0).toBe(0);
    expect(secondSocket.listeners.get('error')?.size ?? 0).toBe(0);
    expect(MockWebSocket.instances).toHaveLength(2);
  });
});
