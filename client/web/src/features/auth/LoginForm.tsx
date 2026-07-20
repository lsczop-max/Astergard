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
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (state.session?.username) {
      setUsername(state.session.username);
    }
  }, [state.session?.username]);

  const isBusy = submitting || state.connectionState === 'connecting' || state.connectionState === 'authenticating';

  const helper = useMemo(() => {
    if (state.connectionState === 'ready') {
      return 'Połączenie gotowe. Możesz wysłać komendę.';
    }
    if (state.connectionState === 'authenticating') {
      return 'Logowanie w toku.';
    }
    if (state.connectionState === 'handshaking') {
      return 'Nawiązano połączenie. Podaj dane istniejącego konta.';
    }
    return 'D59.4 obsługuje istniejące konto. Tworzenie postaci będzie później.';
  }, [state.connectionState]);

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
        transport
          .submitLogin(username, currentPassword)
          .catch((error) => {
            dispatch({ kind: 'set-error', message: error instanceof Error ? error.message : 'Nie udało się wysłać logowania.' });
          })
          .finally(() => {
            setSubmitting(false);
          });
      }}
    >
      <h2>Logowanie</h2>
      <p className="muted">{helper}</p>
      <div className="field">
        <label htmlFor="login-username">Nazwa użytkownika</label>
        <input
          id="login-username"
          autoComplete="username"
          name="username"
          value={username}
          onChange={(event) => setUsername(event.target.value)}
        />
      </div>
      <div className="field">
        <label htmlFor="login-password">Hasło</label>
        <input
          id="login-password"
          type="password"
          autoComplete="current-password"
          name="current-password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
      </div>
      <button type="submit" disabled={isBusy || !username || !password || state.connectionState === 'ready'}>
        Połącz / Zaloguj
      </button>
      <p className="caption">Ten klient D59.4 obsługuje tylko istniejące konto. Tworzenie postaci pojawi się później.</p>
      {state.connectionState !== 'ready' ? (
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
