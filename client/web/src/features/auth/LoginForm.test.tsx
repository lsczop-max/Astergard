import { describe, expect, it, vi, beforeEach } from 'vitest';
import userEvent from '@testing-library/user-event';
import { screen } from '@testing-library/react';
import type { MutableRefObject } from 'react';
import { renderWithStore } from '../../test/render';
import { LoginForm } from './LoginForm';
import type { AstergardWebSocketTransport } from '../../transport/AstergardWebSocketTransport';
import { useAppStore } from '../../store/AppStore';

function makeTransportRef(
  submitLoginImpl: (username: string, password: string) => Promise<void> = async () => undefined,
  startCreatorImpl: (username: string, password: string) => Promise<void> = async () => undefined,
): MutableRefObject<AstergardWebSocketTransport | null> {
  return {
    current: {
      connect: vi.fn(),
      dispose: vi.fn(),
      executeCommand: vi.fn(),
      getState: vi.fn(() => 'handshaking'),
      ping: vi.fn(),
      subscribe: vi.fn(() => vi.fn()),
      submitLogin: submitLoginImpl,
      startCreator: startCreatorImpl,
      goBackInCreator: vi.fn(),
      cancelCreator: vi.fn(),
      close: vi.fn(),
    } as unknown as AstergardWebSocketTransport,
  };
}

function ErrorProbe() {
  const { state } = useAppStore();
  return <div aria-live="polite">{state.userError}</div>;
}

beforeEach(() => {
  vi.restoreAllMocks();
});

describe('LoginForm', () => {
  it('clears the password after submit', async () => {
    const user = userEvent.setup();
    const transportRef = makeTransportRef(async () => undefined);
    renderWithStore(<LoginForm transportRef={transportRef} />);
    const username = screen.getByLabelText('Nazwa użytkownika');
    const password = screen.getByLabelText('Hasło');
    await user.type(username, 'ala');
    await user.type(password, 'tajne');
    await user.click(screen.getByRole('button', { name: 'Zaloguj' }));
    expect(password).toHaveValue('');
  });

  it('shows a safe error on failure and does not use storage or logs', async () => {
    const user = userEvent.setup();
    const setItemSpy = vi.spyOn(Storage.prototype, 'setItem');
    const logSpy = vi.spyOn(console, 'log').mockImplementation(() => undefined);
    const errorSpy = vi.spyOn(console, 'error').mockImplementation(() => undefined);
    const transportRef = makeTransportRef(async () => {
      throw new Error('Błędne hasło');
    });
    renderWithStore(
      <>
        <LoginForm transportRef={transportRef} />
        <ErrorProbe />
      </>,
    );
    await user.type(screen.getByLabelText('Nazwa użytkownika'), 'ala');
    await user.type(screen.getByLabelText('Hasło'), 'tajne');
    await user.click(screen.getByRole('button', { name: 'Zaloguj' }));
    expect(await screen.findByText('Błędne hasło')).toBeInTheDocument();
    expect(setItemSpy).not.toHaveBeenCalled();
    expect(logSpy).not.toHaveBeenCalled();
    expect(errorSpy).not.toHaveBeenCalled();
  });

  it('starts creator mode when switched to new character', async () => {
    const user = userEvent.setup();
    const startCreator = vi.fn().mockResolvedValue(undefined);
    const transportRef = makeTransportRef(async () => undefined, startCreator);
    renderWithStore(<LoginForm transportRef={transportRef} />);

    await user.click(screen.getByLabelText('Nowa postać'));
    await user.type(screen.getByLabelText('Nazwa nowego konta'), 'nowa');
    await user.type(screen.getByLabelText('Nowe hasło'), 'sekret');
    await user.click(screen.getByRole('button', { name: 'Rozpocznij tworzenie' }));

    expect(startCreator).toHaveBeenCalledTimes(1);
    expect(startCreator).toHaveBeenCalledWith('nowa', 'sekret');
  });
});
