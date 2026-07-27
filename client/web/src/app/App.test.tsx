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

    expect(screen.getByRole('region', { name: 'Ekran logowania' })).toBeInTheDocument();
    expect(screen.getByRole('complementary', { name: 'Panel logowania' })).toBeInTheDocument();
    expect(screen.getByRole('region', { name: 'Obszar komendy' })).toBeInTheDocument();
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

  it('maps numpad movement from the command input only after ready and ignores top-row digits', async () => {
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
    const commandInput = screen.getByLabelText('Komenda');

    fireEvent.keyDown(document.body, { code: 'Numpad8', key: '8', location: KeyboardEvent.DOM_KEY_LOCATION_NUMPAD });
    expect(socket.sent).toHaveLength(initialSentLength + 1);
    const firstCommand = parseProtocolEnvelope(socket.sent.at(-1) as string);
    expect(firstCommand).toMatchObject({
      version: 1,
      type: 'command.execute',
      payload: { command: 'polnoc' },
    });

    commandInput.focus();
    fireEvent.keyDown(commandInput, {
      code: 'Numpad9',
      key: '9',
      location: KeyboardEvent.DOM_KEY_LOCATION_NUMPAD,
      buttons: 1,
    });
    expect(socket.sent).toHaveLength(initialSentLength + 1);

    await act(async () => {
      socket.message(
        JSON.stringify({
          version: 1,
          type: 'command.result',
          payload: { command: 'polnoc', success: true },
          request_id: firstCommand.request_id,
          sequence: 8,
        }),
      );
    });

    fireEvent.keyDown(commandInput, {
      code: 'Unidentified',
      key: 'ArrowUp',
      location: KeyboardEvent.DOM_KEY_LOCATION_NUMPAD,
      buttons: 1,
    });
    expect(socket.sent).toHaveLength(initialSentLength + 2);
    expect(parseProtocolEnvelope(socket.sent.at(-1) as string)).toMatchObject({
      version: 1,
      type: 'command.execute',
      payload: { command: 'polnoc' },
    });

    fireEvent.keyDown(commandInput, {
      code: 'Digit8',
      key: '8',
      location: KeyboardEvent.DOM_KEY_LOCATION_STANDARD,
      buttons: 1,
    });
    expect(socket.sent).toHaveLength(initialSentLength + 2);

    fireEvent.keyDown(commandInput, {
      code: 'Numpad8',
      key: '8',
      repeat: true,
      location: KeyboardEvent.DOM_KEY_LOCATION_NUMPAD,
      buttons: 1,
    });
    expect(socket.sent).toHaveLength(initialSentLength + 2);
  });

  it('blocks numpad movement in login and creator forms before ready', async () => {
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

    const beforeReadyLength = socket.sent.length;
    const username = screen.getByLabelText('Nazwa użytkownika');
    username.focus();
    fireEvent.keyDown(username, {
      code: 'Numpad8',
      key: '8',
      location: KeyboardEvent.DOM_KEY_LOCATION_NUMPAD,
      buttons: 1,
    });
    expect(socket.sent).toHaveLength(beforeReadyLength);

    await user.click(screen.getByLabelText('Nowa postać'));
    await user.type(screen.getByLabelText('Nazwa nowego konta'), 'nowa');
    await user.type(screen.getByLabelText('Nowe hasło'), 'sekret');
    await user.click(screen.getByRole('button', { name: 'Rozpocznij tworzenie' }));

    const creatorStartLength = socket.sent.length;

    await act(async () => {
      socket.message(
        JSON.stringify({
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
          request_id: parseProtocolEnvelope(socket.sent.at(-1) as string).request_id,
          sequence: 2,
        }),
      );
    });

    const creatorInput = screen.getByLabelText('Odpowiedź');
    creatorInput.focus();
    fireEvent.keyDown(creatorInput, {
      code: 'Numpad2',
      key: '2',
      location: KeyboardEvent.DOM_KEY_LOCATION_NUMPAD,
      buttons: 1,
    });
    expect(socket.sent).toHaveLength(creatorStartLength);
  });

  it('replaces the trial transport and keeps the second connection active', () => {
    const { unmount } = render(
      <StrictMode>
        <App />
      </StrictMode>,
    );

    expect(screen.getAllByRole('region', { name: 'Ekran logowania' })).toHaveLength(1);
    expect(screen.getAllByRole('region', { name: 'Obszar komendy' })).toHaveLength(1);
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

  it('sends the current creator step id with the selected option id', async () => {
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

    await user.click(screen.getByLabelText('Nowa postać'));
    await user.type(screen.getByLabelText('Nazwa nowego konta'), 'nowa');
    await user.type(screen.getByLabelText('Nowe hasło'), 'sekret');
    await user.click(screen.getByRole('button', { name: 'Rozpocznij tworzenie' }));

    const start = parseProtocolEnvelope(socket.sent.at(-1) as string);
    expect(start.type).toBe('creator.start');

    await act(async () => {
      socket.message(
        JSON.stringify({
          version: 1,
          type: 'creator.started',
          payload: {
            username: 'nowa',
            step: {
              step_id: 'special_feature',
              title: 'Cechy szczególne',
              prompt: 'Wybierz cechę szczególną.',
              input_type: 'choice',
              choices: [
                { value: 'blizna_policzek', label: 'wąska blizna na policzku' },
                { value: 'tatuaż', label: 'tatuaż' },
              ],
              back_available: true,
              cancel_available: true,
            },
          },
          request_id: start.request_id,
          sequence: 2,
        }),
      );
    });

    const specialFeatureSelect = screen.getByLabelText('Wybór');
    await user.selectOptions(specialFeatureSelect, 'blizna_policzek');
    await user.click(screen.getByRole('button', { name: 'Zatwierdź' }));

    const submit = parseProtocolEnvelope(socket.sent.at(-1) as string);
    expect(submit.type).toBe('creator.submit');
    expect(submit.payload).toEqual({ step_id: 'special_feature', value: 'blizna_policzek' });
    expect(Object.keys(submit.payload)).toEqual(['step_id', 'value']);
  });

  it('shows the desktop shell after login with terminal, map, info and command regions', async () => {
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

    await act(async () => {
      socket.message(
        JSON.stringify({
          version: 1,
          type: 'auth.result',
          payload: { success: true, username: 'ala' },
          request_id: parseProtocolEnvelope(socket.sent[1]).request_id,
          sequence: 2,
        }),
      );
      socket.message(
        JSON.stringify({
          version: 1,
          type: 'map.snapshot',
          payload: {
            map_version: 1,
            sync_id: 'sync-1',
            chunk_index: 0,
            complete: true,
            current_room_id: 1,
            rooms: [{ room_id: 1, name: 'Start', region: 'Astergard', x: 0, y: 0, z: 0 }],
            edges: [],
          },
          sequence: 3,
        }),
      );
      socket.message(
        JSON.stringify({
          version: 1,
          type: 'session.ready',
          payload: { transport: 'websocket', username: 'ala' },
          sequence: 4,
        }),
      );
    });

    const terminalRegion = screen.getByRole('region', { name: 'Terminal gry' });
    const mapRegion = screen.getByRole('region', { name: 'Mapa odkrytej okolicy' });
    const infoRegion = screen.getByRole('region', { name: 'Informacje o postaci i lokacji' });
    const commandRegion = screen.getByRole('region', { name: 'Obszar komendy' });

    expect(terminalRegion).toBeInTheDocument();
    expect(mapRegion).toBeInTheDocument();
    expect(infoRegion).toBeInTheDocument();
    expect(commandRegion).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Odkryta mapa' })).toBeInTheDocument();
    expect(screen.queryByText('Mapa pojawi się po wejściu do gry.')).not.toBeInTheDocument();
    expect(screen.getByRole('img', { name: 'Mapa odkrytej okolicy' })).toBeInTheDocument();
    expect(commandRegion).toContainElement(screen.getByLabelText('Komenda'));
    expect(terminalRegion).not.toContainElement(screen.getByLabelText('Komenda'));
    expect(screen.getByLabelText('Komenda')).toBeEnabled();
  });
});
