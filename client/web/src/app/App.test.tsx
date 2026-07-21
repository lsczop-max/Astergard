import { render, screen } from '@testing-library/react';
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
