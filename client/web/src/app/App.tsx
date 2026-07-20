import { useEffect, useRef } from 'react';
import { LoginForm } from '../features/auth/LoginForm';
import { CommandBar } from '../features/terminal/CommandBar';
import { ConnectionStatus } from '../features/terminal/ConnectionStatus';
import { RoomInfoPanel } from '../features/terminal/RoomInfoPanel';
import { TerminalView } from '../features/terminal/TerminalView';
import { AppStoreProvider, useAppStore } from '../store/AppStore';
import { AstergardWebSocketTransport } from '../transport/AstergardWebSocketTransport';
import { buildWebSocketUrl } from '../transport/url';
import { StatusBanner } from '../components/StatusBanner';

function AppShell() {
  const { state, dispatch } = useAppStore();
  const transportRef = useRef<AstergardWebSocketTransport | null>(null);

  if (transportRef.current === null) {
    transportRef.current = new AstergardWebSocketTransport(buildWebSocketUrl());
  }

  useEffect(() => {
    const transport = transportRef.current;
    if (!transport) {
      return;
    }

    const unsubscribe = transport.subscribe((event) => {
      if (event.kind === 'state') {
        dispatch({ kind: 'transport-state', state: event.state });
        return;
      }
      if (event.kind === 'message') {
        dispatch({ kind: 'message', envelope: event.message });
        return;
      }
      if (event.kind === 'error') {
        dispatch({ kind: 'set-error', message: event.message });
        return;
      }
      if (event.kind === 'request') {
        dispatch({ kind: 'pending-request', requestId: event.requestId, active: event.active });
      }
    });
    transport.connect();

    return () => {
      unsubscribe();
      transport.dispose();
    };
  }, [dispatch]);

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Astergard</p>
          <h1>Shell klienta webowego</h1>
        </div>
        <ConnectionStatus state={state.connectionState} />
      </header>

      <StatusBanner message={state.userError} kind={state.connectionState === 'error' ? 'error' : 'info'} />

      <section className="layout">
        <aside className="sidebar">
          <LoginForm transportRef={transportRef} />
          <RoomInfoPanel room={state.lastRoomInfo} />
        </aside>

        <section className="terminal-pane">
          <TerminalView lines={state.terminalLines} prompt={state.prompt} />
          <CommandBar transportRef={transportRef} disabled={state.connectionState !== 'ready'} />
        </section>
      </section>
    </main>
  );
}

export function App() {
  return (
    <AppStoreProvider>
      <AppShell />
    </AppStoreProvider>
  );
}
