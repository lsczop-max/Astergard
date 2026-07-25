import { createContext, useContext, useMemo, useReducer } from 'react';
import type { ReactNode } from 'react';
import type {
  CharacterVitalsPayload,
  CreatorStepPayload,
  MapEdgePayload,
  MapRoomPayload,
  MapSnapshotPayload,
  MapUpdatePayload,
  ProtocolEnvelope,
  RoomInfoPayload,
} from '../protocol/webProtocol';
import { MAP_CONTRACT_VERSION } from '../protocol/webProtocol';
import { parseAnsi } from '../styles/ansi';

export type ConnectionState = 'disconnected' | 'connecting' | 'handshaking' | 'authenticating' | 'ready' | 'closing' | 'error';

export type TerminalLine =
  | { id: string; kind: 'text'; text: string; segments: ReturnType<typeof parseAnsi> }
  | { id: string; kind: 'room'; text: string }
  | { id: string; kind: 'prompt'; text: string }
  | { id: string; kind: 'input'; text: string }
  | { id: string; kind: 'system'; text: string };

const SCROLLBACK_LIMIT = 900;

export type MapSyncStatus = 'idle' | 'syncing' | 'ready';

type PendingMapSnapshot = {
  syncId: string;
  nextChunkIndex: number;
  chunksByIndex: Record<number, MapSnapshotPayload>;
};

export type MapState = {
  syncStatus: MapSyncStatus;
  syncId: string | null;
  currentRoomId: number | null;
  roomsById: Record<number, MapRoomPayload>;
  edges: MapEdgePayload[];
  pendingSnapshot: PendingMapSnapshot | null;
};

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
  vitals: CharacterVitalsPayload | null;
  terminalLines: TerminalLine[];
  prompt: string;
  lastRoomInfo: RoomInfoPayload | null;
  map: MapState;
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
  vitals: null,
  terminalLines: [],
  prompt: '',
  lastRoomInfo: null,
  map: {
    syncStatus: 'idle',
    syncId: null,
    currentRoomId: null,
    roomsById: {},
    edges: [],
    pendingSnapshot: null,
  },
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

function emptyMapState(): MapState {
  return {
    syncStatus: 'idle',
    syncId: null,
    currentRoomId: null,
    roomsById: {},
    edges: [],
    pendingSnapshot: null,
  };
}

function mapEdgeKey(edge: MapEdgePayload): string {
  return `${edge.from_room_id}:${edge.to_room_id}:${edge.direction}`;
}

function dedupeMapEdges(edges: MapEdgePayload[]): MapEdgePayload[] {
  const seen = new Set<string>();
  const unique: MapEdgePayload[] = [];
  for (const edge of edges) {
    const key = mapEdgeKey(edge);
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    unique.push(edge);
  }
  return unique;
}

function mergeMapRooms(existing: Record<number, MapRoomPayload>, rooms: MapRoomPayload[]): Record<number, MapRoomPayload> {
  const next = { ...existing };
  for (const room of rooms) {
    next[room.room_id] = room;
  }
  return next;
}

function filterValidEdges(roomsById: Record<number, MapRoomPayload>, edges: MapEdgePayload[]): MapEdgePayload[] {
  return dedupeMapEdges(edges).filter((edge) => roomsById[edge.from_room_id] !== undefined && roomsById[edge.to_room_id] !== undefined);
}

function hasPublishedMap(map: MapState): boolean {
  return map.syncId !== null || map.currentRoomId !== null || Object.keys(map.roomsById).length > 0 || map.edges.length > 0;
}

function clearSnapshotStaging(map: MapState): MapState {
  return {
    ...map,
    syncStatus: hasPublishedMap(map) ? 'ready' : 'idle',
    pendingSnapshot: null,
  };
}

function makePendingSnapshot(payload: MapSnapshotPayload): PendingMapSnapshot {
  return {
    syncId: payload.sync_id,
    nextChunkIndex: payload.chunk_index + 1,
    chunksByIndex: {
      [payload.chunk_index]: payload,
    },
  };
}

function appendPendingSnapshot(pendingSnapshot: PendingMapSnapshot, payload: MapSnapshotPayload): PendingMapSnapshot {
  return {
    syncId: pendingSnapshot.syncId,
    nextChunkIndex: pendingSnapshot.nextChunkIndex + 1,
    chunksByIndex: {
      ...pendingSnapshot.chunksByIndex,
      [payload.chunk_index]: payload,
    },
  };
}

function validateSnapshotChunks(pendingSnapshot: PendingMapSnapshot): MapState | null {
  const chunkIndexes = Object.keys(pendingSnapshot.chunksByIndex)
    .map((index) => Number(index))
    .sort((a, b) => a - b);
  if (chunkIndexes.length === 0 || chunkIndexes[0] !== 0) {
    return null;
  }
  const firstChunk = pendingSnapshot.chunksByIndex[0];
  if (!firstChunk) {
    return null;
  }
  const expectedSyncId = pendingSnapshot.syncId;
  const expectedRoomId = firstChunk.current_room_id;
  const lastChunkIndex = chunkIndexes[chunkIndexes.length - 1];
  let expectedChunkIndex = 0;
  let roomsById: Record<number, MapRoomPayload> = {};
  let edges: MapEdgePayload[] = [];
  const seenRoomIds = new Set<number>();
  for (const chunkIndex of chunkIndexes) {
    if (chunkIndex !== expectedChunkIndex) {
      return null;
    }
    const chunk = pendingSnapshot.chunksByIndex[chunkIndex];
    if (
      !chunk ||
      chunk.sync_id !== expectedSyncId ||
      chunk.current_room_id !== expectedRoomId ||
      chunk.map_version !== MAP_CONTRACT_VERSION ||
      (chunk.complete && chunkIndex !== lastChunkIndex)
    ) {
      return null;
    }
    for (const room of chunk.rooms) {
      if (seenRoomIds.has(room.room_id)) {
        return null;
      }
      seenRoomIds.add(room.room_id);
    }
    roomsById = mergeMapRooms(roomsById, chunk.rooms);
    edges = [...edges, ...chunk.edges];
    expectedChunkIndex += 1;
  }
  if (roomsById[expectedRoomId] === undefined) {
    return null;
  }
  const uniqueEdges = dedupeMapEdges(edges);
  if (uniqueEdges.some((edge) => roomsById[edge.from_room_id] === undefined || roomsById[edge.to_room_id] === undefined)) {
    return null;
  }
  return {
    syncStatus: 'ready',
    syncId: expectedSyncId,
    currentRoomId: expectedRoomId,
    roomsById,
    edges: uniqueEdges,
    pendingSnapshot: null,
  };
}

function startMapSnapshot(state: AppState, payload: MapSnapshotPayload): AppState {
  const currentMap = state.map;
  const pendingSnapshot = currentMap.pendingSnapshot;

  if (pendingSnapshot !== null) {
    if (payload.sync_id !== pendingSnapshot.syncId) {
      if (payload.chunk_index !== 0 || payload.complete) {
        return state;
      }
      return {
        ...state,
        map: {
          ...currentMap,
          syncStatus: 'syncing',
          pendingSnapshot: makePendingSnapshot(payload),
        },
      };
    }
    if (payload.chunk_index !== pendingSnapshot.nextChunkIndex) {
      return state;
    }
    const nextPendingSnapshot = appendPendingSnapshot(pendingSnapshot, payload);
    if (!payload.complete) {
      return {
        ...state,
        map: {
          ...currentMap,
          syncStatus: 'syncing',
          pendingSnapshot: nextPendingSnapshot,
        },
      };
    }
    const finalized = validateSnapshotChunks(nextPendingSnapshot);
    if (!finalized) {
      return {
        ...state,
        map: clearSnapshotStaging(currentMap),
      };
    }
    return {
      ...state,
      map: finalized,
    };
  }

  if (payload.chunk_index !== 0) {
    return state;
  }

  if (currentMap.syncStatus === 'ready' && payload.complete) {
    return state;
  }

  const nextPendingSnapshot = makePendingSnapshot(payload);
  if (!payload.complete) {
    return {
      ...state,
      map: {
        ...currentMap,
        syncStatus: 'syncing',
        pendingSnapshot: nextPendingSnapshot,
      },
    };
  }
  const finalized = validateSnapshotChunks(nextPendingSnapshot);
  if (!finalized) {
    return {
      ...state,
      map: clearSnapshotStaging(currentMap),
    };
  }
  return {
    ...state,
    map: finalized,
  };
}

function applyMapUpdate(state: AppState, payload: MapUpdatePayload): AppState {
  if (state.map.syncStatus !== 'ready' || state.map.pendingSnapshot !== null || state.map.syncId !== payload.sync_id) {
    return state;
  }
  const roomIds = new Set<number>();
  for (const room of payload.rooms) {
    if (roomIds.has(room.room_id)) {
      return state;
    }
    roomIds.add(room.room_id);
  }
  const roomsById = mergeMapRooms(state.map.roomsById, payload.rooms);
  if (roomsById[payload.current_room_id] === undefined) {
    return state;
  }
  const edges = filterValidEdges(roomsById, [...state.map.edges, ...payload.edges]);
  if (edges.length !== dedupeMapEdges([...state.map.edges, ...payload.edges]).length) {
    return state;
  }
  return {
    ...state,
    map: {
      ...state.map,
      currentRoomId: payload.current_room_id,
      roomsById,
      edges,
    },
  };
}

export function reducer(state: AppState, action: Action): AppState {
  switch (action.kind) {
    case 'transport-state':
      return {
        ...state,
        connectionState: action.state,
        creator: action.state === 'disconnected' || action.state === 'closing' || action.state === 'error' ? null : state.creator,
        vitals: action.state === 'disconnected' || action.state === 'closing' || action.state === 'error' ? null : state.vitals,
        pendingRequestIds: action.state === 'disconnected' || action.state === 'closing' || action.state === 'error' ? [] : state.pendingRequestIds,
        map: action.state === 'disconnected' || action.state === 'closing' || action.state === 'error' ? emptyMapState() : state.map,
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
          map: action.envelope.payload.success ? emptyMapState() : state.map,
        } satisfies AppState;
        return action.envelope.payload.success ? nextState : appendTerminalLine(nextState, createSystemLine('Logowanie nie powiodło się.'));
      }
      if (action.envelope.type === 'character.vitals') {
        return {
          ...state,
          vitals: action.envelope.payload,
          pendingRequestIds,
        };
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
          map: emptyMapState(),
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
      if (action.envelope.type === 'map.snapshot') {
        return startMapSnapshot(
          {
            ...state,
            pendingRequestIds,
          },
          action.envelope.payload,
        );
      }
      if (action.envelope.type === 'map.update') {
        return applyMapUpdate(
          {
            ...state,
            pendingRequestIds,
          },
          action.envelope.payload,
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
