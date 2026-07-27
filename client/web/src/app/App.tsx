import { useEffect, useRef } from 'react';
import type { MutableRefObject } from 'react';
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
  return Boolean(target.closest('.login-form, .creator-form'));
}

function isCommandInputTarget(target: EventTarget | null): boolean {
  return target instanceof HTMLElement && target.id === 'command-input';
}

function mapNumpadCommand(event: KeyboardEvent): string | null {
  const direct = NUMPAD_COMMANDS[event.code];
  if (direct) {
    return direct;
  }
  if (event.location !== KeyboardEvent.DOM_KEY_LOCATION_NUMPAD) {
    return null;
  }
  const fallbackByKey: Record<string, string> = {
    ArrowUp: 'polnoc',
    ArrowRight: 'wschod',
    ArrowDown: 'poludnie',
    ArrowLeft: 'zachod',
    Home: 'polnocny-zachod',
    PageUp: 'polnocny-wschod',
    End: 'poludniowy-zachod',
    PageDown: 'poludniowy-wschod',
  };
  return fallbackByKey[event.key] ?? null;
}

type ShellProps = {
  state: ReturnType<typeof useAppStore>['state'];
  transportRef: MutableRefObject<AstergardWebSocketTransport | null>;
};

function AuthShell({ state, transportRef }: ShellProps) {
  return (
    <section className="workspace workspace-auth" aria-label="Ekran logowania">
      <div className="auth-grid">
        <aside className="auth-column" aria-label="Panel logowania">
          {state.creator ? <CreatorForm transportRef={transportRef} /> : <LoginForm transportRef={transportRef} />}
          <RoomInfoPanel room={state.lastRoomInfo} />
        </aside>

        <section className="auth-preview panel" aria-label="Podgląd sesji">
          <p className="eyebrow">Sesja gry</p>
          <h2>Interfejs pojawi się po zalogowaniu</h2>
          <p className="caption">
            Terminal, mapa i stan postaci są odkrywane dopiero po rozpoczęciu sesji.
          </p>
        </section>
      </div>

      <section className="command-region panel" aria-label="Obszar komendy">
        <CommandBar transportRef={transportRef} disabled={state.connectionState !== 'ready'} />
      </section>
    </section>
  );
}

function GameShell({ state, transportRef }: ShellProps) {
  return (
    <section className="workspace workspace-game" aria-label="Widok gry">
      <div className="game-grid">
        <section className="game-terminal-region" aria-label="Terminal gry">
          <TerminalView lines={state.terminalLines} prompt={state.prompt} />
        </section>

        <aside className="game-sidebar" aria-label="Panel boczny gry">
          <WorldMapPanel />
          <section className="game-status-region" aria-label="Informacje o postaci i lokacji">
            <CharacterVitalsPanel vitals={state.vitals} />
            <RoomInfoPanel room={state.lastRoomInfo} />
          </section>
        </aside>
      </div>

      <section className="command-region panel" aria-label="Obszar komendy">
        <CommandBar transportRef={transportRef} disabled={state.connectionState !== 'ready'} />
      </section>
    </section>
  );
}

function AppShell() {
  const { state, dispatch } = useAppStore();
  const transportRef = useRef<AstergardWebSocketTransport | null>(null);
  const sessionActive = state.session !== null;

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
      if (isInteractiveTarget(event.target) && !isCommandInputTarget(event.target)) {
        return;
      }
      const command = mapNumpadCommand(event);
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

      {sessionActive ? (
        <GameShell state={state} transportRef={transportRef} />
      ) : (
        <AuthShell state={state} transportRef={transportRef} />
      )}
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
