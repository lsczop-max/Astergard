import { createContext, useContext, useMemo, useReducer } from 'react';
import type { ReactNode } from 'react';
import type {
  CreatorStepPayload,
  ProtocolEnvelope,
  RoomInfoPayload,
} from '../protocol/webProtocol';
import { parseAnsi } from '../styles/ansi';

export type ConnectionState = 'disconnected' | 'connecting' | 'handshaking' | 'authenticating' | 'ready' | 'closing' | 'error';

export type TerminalLine =
  | { id: string; kind: 'text'; text: string; segments: ReturnType<typeof parseAnsi> }
  | { id: string; kind: 'room'; text: string }
  | { id: string; kind: 'prompt'; text: string }
  | { id: string; kind: 'input'; text: string }
  | { id: string; kind: 'system'; text: string };

const SCROLLBACK_LIMIT = 900;

export type AppState = {
  connectionState: ConnectionState;
  session: {
    username: string | null;
    transport: string | null;
  } | null;
  creator: {
    username: string;
    step: CreatorStepPayload;
  } | null;
  terminalLines: TerminalLine[];
  prompt: string;
  lastRoomInfo: RoomInfoPayload | null;
  pendingRequestIds: string[];
  userError: string | null;
};

type Action =
  | { kind: 'transport-state'; state: ConnectionState }
  | { kind: 'message'; envelope: ProtocolEnvelope }
  | { kind: 'append-terminal-input'; command: string }
  | { kind: 'pending-request'; requestId: string; active: boolean }
  | { kind: 'set-error'; message: string }
  | { kind: 'clear-error' };

export const initialState: AppState = {
  connectionState: 'disconnected',
  session: null,
  creator: null,
  terminalLines: [],
  prompt: '',
  lastRoomInfo: null,
  pendingRequestIds: [],
  userError: null,
};

function uid() {
  return `line-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;
}

function appendTerminalLine(state: AppState, line: TerminalLine): AppState {
  return {
    ...state,
    terminalLines: [...state.terminalLines, line].slice(-SCROLLBACK_LIMIT),
  };
}

function createTextLine(text: string): TerminalLine {
  return {
    id: uid(),
    kind: 'text',
    text,
    segments: parseAnsi(text),
  };
}

function createRoomLine(room: RoomInfoPayload): TerminalLine {
  return {
    id: uid(),
    kind: 'room',
    text: `Pokój: ${room.name} | ${room.area} | ${room.coords.x}, ${room.coords.y}, ${room.coords.z}`,
  };
}

function createInputLine(command: string): TerminalLine {
  return {
    id: uid(),
    kind: 'input',
    text: command,
  };
}

function createSystemLine(text: string): TerminalLine {
  return {
    id: uid(),
    kind: 'system',
    text,
  };
}

export function reducer(state: AppState, action: Action): AppState {
  switch (action.kind) {
    case 'transport-state':
      return {
        ...state,
        connectionState: action.state,
        creator: action.state === 'disconnected' || action.state === 'closing' || action.state === 'error' ? null : state.creator,
        pendingRequestIds: action.state === 'disconnected' || action.state === 'closing' || action.state === 'error' ? [] : state.pendingRequestIds,
      };
    case 'set-error':
      return { ...state, userError: action.message };
    case 'clear-error':
      return { ...state, userError: null };
    case 'pending-request':
      return {
        ...state,
        pendingRequestIds: action.active
          ? [...state.pendingRequestIds, action.requestId]
          : state.pendingRequestIds.filter((requestId) => requestId !== action.requestId),
      };
    case 'append-terminal-input':
      return appendTerminalLine(state, createInputLine(action.command));
    case 'message': {
      const pendingRequestIds = state.pendingRequestIds.filter((requestId) => requestId !== action.envelope.request_id);
      if (action.envelope.type === 'session.ready') {
        return appendTerminalLine({
          ...state,
          creator: null,
          connectionState: 'ready',
          session: {
            username: action.envelope.payload.username ?? state.session?.username ?? null,
            transport: action.envelope.payload.transport,
          },
          pendingRequestIds,
        }, createSystemLine('Sesja gotowa.'));
      }
      if (action.envelope.type === 'auth.result') {
        const nextState = {
          ...state,
          session: action.envelope.payload.success
            ? {
                username: action.envelope.payload.username,
                transport: state.session?.transport ?? 'websocket',
              }
            : state.session,
          userError: action.envelope.payload.success ? null : `Logowanie nie powiodło się: ${action.envelope.payload.reason ?? 'odmowa serwera'}.`,
          pendingRequestIds,
        } satisfies AppState;
        return action.envelope.payload.success ? nextState : appendTerminalLine(nextState, createSystemLine('Logowanie nie powiodło się.'));
      }
      if (action.envelope.type === 'creator.started') {
        return {
          ...state,
          creator: {
            username: action.envelope.payload.username,
            step: action.envelope.payload.step,
          },
          userError: null,
          pendingRequestIds,
        };
      }
      if (action.envelope.type === 'creator.step') {
        return {
          ...state,
          creator: state.creator
            ? {
                ...state.creator,
                step: action.envelope.payload,
              }
            : {
                username: state.session?.username ?? '',
                step: action.envelope.payload,
              },
          userError: null,
          pendingRequestIds,
        };
      }
      if (action.envelope.type === 'creator.validation_error') {
        return {
          ...state,
          userError: action.envelope.payload.message,
          pendingRequestIds,
        };
      }
      if (action.envelope.type === 'creator.cancelled') {
        return {
          ...state,
          creator: null,
          userError: null,
          pendingRequestIds,
        };
      }
      if (action.envelope.type === 'creator.finished') {
        return {
          ...state,
          creator: null,
          userError: null,
          pendingRequestIds,
        };
      }
      if (action.envelope.type === 'output.text') {
        return appendTerminalLine(
          {
            ...state,
            pendingRequestIds,
          },
          createTextLine(action.envelope.payload.text),
        );
      }
      if (action.envelope.type === 'output.prompt') {
        return {
          ...state,
          pendingRequestIds,
          prompt: action.envelope.payload.prompt,
        };
      }
      if (action.envelope.type === 'room.info') {
        return appendTerminalLine(
          {
            ...state,
            lastRoomInfo: action.envelope.payload,
            pendingRequestIds,
          },
          createRoomLine(action.envelope.payload),
        );
      }
      if (action.envelope.type === 'command.result') {
        return {
          ...state,
          pendingRequestIds,
        };
      }
      if (action.envelope.type === 'connection.pong') {
        return {
          ...state,
          pendingRequestIds,
        };
      }
      if (action.envelope.type === 'protocol.error') {
        return appendTerminalLine({
          ...state,
          connectionState: 'error',
          userError: `Błąd protokołu: ${action.envelope.payload.message}`,
          pendingRequestIds,
        }, createSystemLine(`Błąd protokołu: ${action.envelope.payload.message}`));
      }
      return { ...state, pendingRequestIds };
    }
    default:
      return state;
  }
}

type ContextValue = {
  state: AppState;
  dispatch: (action: Action) => void;
};

const AppStoreContext = createContext<ContextValue | null>(null);

export function AppStoreProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  const value = useMemo(() => ({ state, dispatch }), [state, dispatch]);
  return <AppStoreContext.Provider value={value}>{children}</AppStoreContext.Provider>;
}

export function useAppStore(): ContextValue {
  const value = useContext(AppStoreContext);
  if (!value) {
    throw new Error('AppStoreProvider is missing.');
  }
  return value;
}
