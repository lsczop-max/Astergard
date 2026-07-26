import { useEffect, useRef } from 'react';
import { CreatorForm } from '../features/auth/CreatorForm';
import { LoginForm } from '../features/auth/LoginForm';
import { CharacterVitalsPanel } from '../features/terminal/CharacterVitalsPanel';
import { CommandBar } from '../features/terminal/CommandBar';
import { ConnectionStatus } from '../features/terminal/ConnectionStatus';
import { RoomInfoPanel } from '../features/terminal/RoomInfoPanel';
import { TerminalView } from '../features/terminal/TerminalView';
import { WorldMapPanel } from '../features/map/WorldMapPanel';
import { AppStoreProvider, useAppStore } from '../store/AppStore';
import { AstergardWebSocketTransport } from '../transport/AstergardWebSocketTransport';
import { buildWebSocketUrl } from '../transport/url';
import { StatusBanner } from '../components/StatusBanner';

const NUMPAD_COMMANDS: Record<string, string> = {
  Numpad8: 'polnoc',
  Numpad9: 'polnocny-wschod',
  Numpad6: 'wschod',
  Numpad3: 'poludniowy-wschod',
  Numpad2: 'poludnie',
  Numpad1: 'poludniowy-zachod',
  Numpad4: 'zachod',
  Numpad7: 'polnocny-zachod',
  Numpad5: 'spojrz',
};

function isInteractiveTarget(target: EventTarget | null): boolean {
  if (!(target instanceof Element)) {
    return false;
  }
  return Boolean(target.closest('input, textarea, select, button, [contenteditable="true"], .login-form, .creator-form, .command-bar'));
}

function AppShell() {
  const { state, dispatch } = useAppStore();
  const transportRef = useRef<AstergardWebSocketTransport | null>(null);

  useEffect(() => {
    const transport = new AstergardWebSocketTransport(buildWebSocketUrl());
    transportRef.current = transport;

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

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.repeat || event.ctrlKey || event.altKey || event.metaKey) {
        return;
      }
      if (isInteractiveTarget(event.target)) {
        return;
      }
      const command = NUMPAD_COMMANDS[event.code];
      if (!command) {
        return;
      }
      const currentTransport = transportRef.current;
      if (!currentTransport || !currentTransport.canExecuteCommand()) {
        return;
      }
      event.preventDefault();
      void currentTransport.executeCommand(command).catch((error) => {
        dispatch({ kind: 'set-error', message: error instanceof Error ? error.message : 'Nie udało się wysłać komendy.' });
      });
    };
    document.addEventListener('keydown', onKeyDown);

    return () => {
      document.removeEventListener('keydown', onKeyDown);
      unsubscribe();
      transport.dispose();
      if (transportRef.current === transport) {
        transportRef.current = null;
      }
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
          {state.creator ? <CreatorForm transportRef={transportRef} /> : <LoginForm transportRef={transportRef} />}
          <RoomInfoPanel room={state.lastRoomInfo} />
        </aside>

        <section className="terminal-pane">
          <WorldMapPanel />
          <CharacterVitalsPanel vitals={state.vitals} />
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
