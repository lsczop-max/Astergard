import { useEffect, useMemo, useState } from 'react';
import type { MutableRefObject } from 'react';
import type { AstergardWebSocketTransport } from '../../transport/AstergardWebSocketTransport';
import { useAppStore } from '../../store/AppStore';

type LoginFormProps = {
  transportRef: MutableRefObject<AstergardWebSocketTransport | null>;
};

export function LoginForm({ transportRef }: LoginFormProps) {
  const { state, dispatch } = useAppStore();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [mode, setMode] = useState<'login' | 'create'>('login');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (state.session?.username) {
      setUsername(state.session.username);
    }
  }, [state.session?.username]);

  const transportState = transportRef.current?.getState() ?? state.connectionState;
  const transportOnline = transportState === 'handshaking' || transportState === 'authenticating';
  const canReconnect = transportState === 'disconnected' || transportState === 'error' || transportState === 'closing';
  const isBusy = submitting || state.connectionState === 'connecting' || !transportOnline;

  const helper = useMemo(() => {
    if (state.connectionState === 'ready') {
      return 'Połączenie gotowe. Możesz wysłać komendę.';
    }
    if (mode === 'create') {
      return transportOnline
        ? 'Tworzysz nową postać. Po starcie kreatora kolejne kroki pojawią się jako osobny formularz.'
        : 'Połącz się z serwerem, aby rozpocząć tworzenie nowej postaci.';
    }
    if (state.connectionState === 'authenticating') {
      return 'Logowanie w toku.';
    }
    if (state.connectionState === 'handshaking') {
      return 'Nawiązano połączenie. Podaj dane istniejącej postaci albo wybierz tworzenie nowej.';
    }
    return 'Wybierz logowanie istniejącą postacią albo rozpocznij tworzenie nowej.';
  }, [mode, state.connectionState, transportOnline]);

  return (
    <form
      className="panel login-form"
      onSubmit={(event) => {
        event.preventDefault();
        if (!username || !password) {
          dispatch({ kind: 'set-error', message: 'Podaj nazwę użytkownika i hasło.' });
          return;
        }
        const transport = transportRef.current;
        if (!transport) {
          dispatch({ kind: 'set-error', message: 'Transport nie jest gotowy.' });
          return;
        }
        setSubmitting(true);
        const currentPassword = password;
        setPassword('');
        dispatch({ kind: 'clear-error' });
        const request = mode === 'create'
          ? transport.startCreator(username, currentPassword)
          : transport.submitLogin(username, currentPassword);
        request
          .catch((error) => {
            dispatch({ kind: 'set-error', message: error instanceof Error ? error.message : 'Nie udało się wysłać żądania.' });
          })
          .finally(() => {
            setSubmitting(false);
          });
      }}
    >
      <h2>{mode === 'create' ? 'Tworzenie postaci' : 'Logowanie'}</h2>
      <p className="muted">{helper}</p>
      <fieldset className="mode-switch" aria-label="Tryb wejścia">
        <label>
          <input type="radio" name="login-mode" checked={mode === 'login'} onChange={() => setMode('login')} />
          Istniejąca postać
        </label>
        <label>
          <input type="radio" name="login-mode" checked={mode === 'create'} onChange={() => setMode('create')} />
          Nowa postać
        </label>
      </fieldset>
      <div className="field">
        <label htmlFor="login-username">{mode === 'create' ? 'Nazwa nowego konta' : 'Nazwa użytkownika'}</label>
        <input
          id="login-username"
          autoComplete="username"
          name="username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
        />
      </div>
      <div className="field">
        <label htmlFor="login-password">{mode === 'create' ? 'Nowe hasło' : 'Hasło'}</label>
        <input
          id="login-password"
          type="password"
          autoComplete={mode === 'create' ? 'new-password' : 'current-password'}
          name="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
      </div>
      <button type="submit" disabled={isBusy || !username || !password || state.connectionState === 'ready'}>
        {mode === 'create' ? 'Rozpocznij tworzenie' : 'Zaloguj'}
      </button>
      <p className="caption">
        {mode === 'create'
          ? 'Po starcie kreatora formularz zmieni się na kroki postaci, bez używania terminala do odpowiedzi.'
          : 'Logowanie dotyczy istniejącej postaci. Jeśli nie masz konta, przełącz na tryb tworzenia.'}
      </p>
      {canReconnect ? (
        <button
          type="button"
          className="ghost-button"
          onClick={() => {
            transportRef.current?.connect();
          }}
        >
          Połącz ponownie
        </button>
      ) : null}
    </form>
  );
}
