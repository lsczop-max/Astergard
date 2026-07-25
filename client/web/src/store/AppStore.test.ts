import { describe, expect, it } from 'vitest';
import { initialState, reducer } from './AppStore';

describe('AppStore reducer', () => {
  it('keeps literal line kinds and does not duplicate prompt as text', () => {
    const afterInput = reducer(initialState, {
      kind: 'append-terminal-input',
      command: 'spojrz',
    });
    expect(afterInput.terminalLines.at(-1)?.kind).toBe('input');

    const afterText = reducer(initialState, {
      kind: 'message',
      envelope: { version: 1, type: 'output.text', payload: { text: 'Witaj' }, sequence: 1 },
    });
    expect(afterText.terminalLines.at(-1)?.kind).toBe('text');
    expect(afterText.terminalLines.at(-1)?.text).toBe('Witaj');

    const afterPrompt = reducer(afterText, {
      kind: 'message',
      envelope: { version: 1, type: 'output.prompt', payload: { prompt: '> ' }, sequence: 2 },
    });
    expect(afterPrompt.prompt).toBe('> ');
    expect(afterPrompt.terminalLines).toHaveLength(afterText.terminalLines.length);
    expect(afterPrompt.terminalLines.at(-1)?.kind).toBe('text');

    const afterRoom = reducer(afterPrompt, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'room.info',
        payload: {
          num: 1,
          name: 'Komnata',
          area: 'Zamek',
          coords: { x: 1, y: 2, z: 3 },
          exits: { north: 2 },
        },
        sequence: 3,
      },
    });
    expect(afterRoom.lastRoomInfo?.name).toBe('Komnata');
    expect(afterRoom.terminalLines.at(-1)?.kind).toBe('room');

    const afterVitals = reducer(afterRoom, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'character.vitals',
        payload: {
          condition_current: 9,
          condition_max: 12,
          condition_label: 'jest lekko ranny',
          stamina_current: 88,
          stamina_max: 100,
          stamina_label: 'Jesteś w pełni sił.',
        },
        sequence: 4,
      },
    });
    expect(afterVitals.vitals?.condition_current).toBe(9);
    expect(afterVitals.terminalLines).toHaveLength(afterRoom.terminalLines.length);

    const afterCommandResult = reducer(afterVitals, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'command.result',
        payload: { command: 'spojrz', success: true },
        request_id: 'cmd-1',
        sequence: 4,
      },
    });
    expect(afterCommandResult.terminalLines.at(-1)?.kind).toBe('room');
    expect(afterCommandResult.pendingRequestIds).toEqual([]);

    const protocolError = reducer(afterCommandResult, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'protocol.error',
        payload: { code: 'invalid_state', message: 'Niebezpieczny detal' },
        request_id: 'err-1',
        sequence: 5,
      },
    });
    expect(protocolError.userError).toContain('Błąd protokołu');
    expect(protocolError.terminalLines.at(-1)?.kind).toBe('system');

    const creatorStarted = reducer(initialState, {
      kind: 'message',
      envelope: {
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
        request_id: 'creator-1',
        sequence: 1,
      },
    });
    expect(creatorStarted.creator?.step.step_id).toBe('name');
    expect(creatorStarted.userError).toBeNull();
    expect(creatorStarted.terminalLines).toHaveLength(initialState.terminalLines.length);

    const creatorError = reducer(creatorStarted, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'creator.validation_error',
        payload: {
          step_id: 'name',
          field: 'name',
          message: 'Imię nie może być puste.',
        },
        request_id: 'creator-1',
        sequence: 2,
      },
    });
    expect(creatorError.creator?.step.step_id).toBe('name');
    expect(creatorError.userError).toBe('Imię nie może być puste.');
    expect(creatorError.terminalLines).toHaveLength(initialState.terminalLines.length);

    const creatorCancelled = reducer(creatorError, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'creator.cancelled',
        payload: {
          username: 'nowa',
        },
        request_id: 'creator-1',
        sequence: 3,
      },
    });
    expect(creatorCancelled.creator).toBeNull();
  });

  it('keeps a ready map visible while a new snapshot stages in the background', () => {
    const ready = reducer(initialState, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-ready',
          chunk_index: 0,
          complete: true,
          current_room_id: 1,
          rooms: [{ room_id: 1, name: 'Start', region: 'Astergard', x: 0, y: 0, z: 0 }],
          edges: [],
        },
        sequence: 1,
      },
    });

    const staging = reducer(ready, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-new',
          chunk_index: 0,
          complete: false,
          current_room_id: 2,
          rooms: [{ room_id: 2, name: 'Nowy', region: 'Astergard', x: 2, y: 0, z: 0 }],
          edges: [],
        },
        sequence: 2,
      },
    });

    expect(staging.map.syncStatus).toBe('syncing');
    expect(staging.map.syncId).toBe('sync-ready');
    expect(staging.map.currentRoomId).toBe(1);
    expect(staging.map.roomsById).toEqual(ready.map.roomsById);
    expect(staging.map.pendingSnapshot?.syncId).toBe('sync-new');

    const stale = reducer(staging, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-old',
          chunk_index: 1,
          complete: true,
          current_room_id: 1,
          rooms: [{ room_id: 99, name: 'Stary', region: 'Astergard', x: 99, y: 0, z: 0 }],
          edges: [],
        },
        sequence: 3,
      },
    });

    expect(stale.map.syncStatus).toBe('syncing');
    expect(stale.map.syncId).toBe('sync-ready');
    expect(stale.map.pendingSnapshot?.syncId).toBe('sync-new');
    expect(stale.map.roomsById).toEqual(ready.map.roomsById);
  });

  it('handles missing, repeated, out-of-order and stale snapshot chunks without publishing partial data', () => {
    const firstChunk = reducer(initialState, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-1',
          chunk_index: 0,
          complete: false,
          current_room_id: 1,
          rooms: [{ room_id: 1, name: 'Start', region: 'Astergard', x: 0, y: 0, z: 0 }],
          edges: [],
        },
        sequence: 1,
      },
    });

    const repeated = reducer(firstChunk, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-1',
          chunk_index: 0,
          complete: false,
          current_room_id: 1,
          rooms: [{ room_id: 1, name: 'Start', region: 'Astergard', x: 0, y: 0, z: 0 }],
          edges: [],
        },
        sequence: 2,
      },
    });
    expect(repeated).toEqual(firstChunk);

    const outOfOrder = reducer(firstChunk, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-1',
          chunk_index: 2,
          complete: true,
          current_room_id: 1,
          rooms: [{ room_id: 2, name: 'Ścieżka', region: 'Astergard', x: 1, y: 0, z: 0 }],
          edges: [],
        },
        sequence: 3,
      },
    });
    expect(outOfOrder).toEqual(firstChunk);

    const replaced = reducer(firstChunk, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-new',
          chunk_index: 0,
          complete: false,
          current_room_id: 2,
          rooms: [{ room_id: 2, name: 'Nowy', region: 'Astergard', x: 2, y: 0, z: 0 }],
          edges: [],
        },
        sequence: 4,
      },
    });
    expect(replaced.map.pendingSnapshot?.syncId).toBe('sync-new');
    expect(replaced.map.roomsById).toEqual({});

    const staleComplete = reducer(replaced, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-1',
          chunk_index: 0,
          complete: true,
          current_room_id: 1,
          rooms: [{ room_id: 1, name: 'Stary', region: 'Astergard', x: 0, y: 0, z: 0 }],
          edges: [],
        },
        sequence: 5,
      },
    });
    expect(staleComplete).toEqual(replaced);
  });

  it('finalizes cross-chunk snapshots atomically and preserves the previous ready map on invalid finalization', () => {
    const crossChunkStart = reducer(initialState, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-cross',
          chunk_index: 0,
          complete: false,
          current_room_id: 2,
          rooms: [{ room_id: 1, name: 'Start', region: 'Astergard', x: 0, y: 0, z: 0 }],
          edges: [{ from_room_id: 1, to_room_id: 2, direction: 'wschod' }],
        },
        sequence: 1,
      },
    });

    const crossChunkComplete = reducer(crossChunkStart, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-cross',
          chunk_index: 1,
          complete: true,
          current_room_id: 2,
          rooms: [{ room_id: 2, name: 'Ścieżka', region: 'Astergard', x: 1, y: 0, z: 0 }],
          edges: [{ from_room_id: 1, to_room_id: 2, direction: 'wschod' }],
        },
        sequence: 2,
      },
    });
    expect(crossChunkComplete.map.syncStatus).toBe('ready');
    expect(crossChunkComplete.map.currentRoomId).toBe(2);
    expect(Object.keys(crossChunkComplete.map.roomsById).sort()).toEqual(['1', '2']);
    expect(crossChunkComplete.map.edges).toEqual([{ from_room_id: 1, to_room_id: 2, direction: 'wschod' }]);

    const ready = reducer(initialState, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-ready',
          chunk_index: 0,
          complete: true,
          current_room_id: 1,
          rooms: [{ room_id: 1, name: 'Start', region: 'Astergard', x: 0, y: 0, z: 0 }],
          edges: [],
        },
        sequence: 3,
      },
    });
    const invalidStaging = reducer(ready, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-bad',
          chunk_index: 0,
          complete: false,
          current_room_id: 1,
          rooms: [{ room_id: 1, name: 'Start', region: 'Astergard', x: 0, y: 0, z: 0 }],
          edges: [],
        },
        sequence: 4,
      },
    });
    const invalidCurrentRoom = reducer(invalidStaging, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-bad',
          chunk_index: 1,
          complete: true,
          current_room_id: 999,
          rooms: [{ room_id: 2, name: 'Ścieżka', region: 'Astergard', x: 1, y: 0, z: 0 }],
          edges: [{ from_room_id: 1, to_room_id: 2, direction: 'wschod' }],
        },
        sequence: 5,
      },
    });
    expect(invalidCurrentRoom.map.syncStatus).toBe('ready');
    expect(invalidCurrentRoom.map.currentRoomId).toBe(1);
    expect(invalidCurrentRoom.map.roomsById).toEqual(ready.map.roomsById);
    expect(invalidCurrentRoom.map.pendingSnapshot).toBeNull();

    const invalidEdgeStaging = reducer(ready, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-bad-2',
          chunk_index: 0,
          complete: false,
          current_room_id: 1,
          rooms: [{ room_id: 1, name: 'Start', region: 'Astergard', x: 0, y: 0, z: 0 }],
          edges: [],
        },
        sequence: 6,
      },
    });
    const invalidEdgeFinal = reducer(invalidEdgeStaging, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-bad-2',
          chunk_index: 1,
          complete: true,
          current_room_id: 1,
          rooms: [{ room_id: 2, name: 'Ścieżka', region: 'Astergard', x: 1, y: 0, z: 0 }],
          edges: [{ from_room_id: 1, to_room_id: 999, direction: 'wschod' }],
        },
        sequence: 7,
      },
    });
    expect(invalidEdgeFinal.map.syncStatus).toBe('ready');
    expect(invalidEdgeFinal.map.currentRoomId).toBe(1);
    expect(invalidEdgeFinal.map.roomsById).toEqual(ready.map.roomsById);
  });

  it('ignores staging, foreign and invalid updates while applying valid updates idempotently', () => {
    const ready = reducer(initialState, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-ready',
          chunk_index: 0,
          complete: true,
          current_room_id: 1,
          rooms: [
            { room_id: 1, name: 'Start', region: 'Astergard', x: 0, y: 0, z: 0 },
            { room_id: 2, name: 'Ścieżka', region: 'Astergard', x: 1, y: 0, z: 0 },
          ],
          edges: [{ from_room_id: 1, to_room_id: 2, direction: 'wschod' }],
        },
        sequence: 1,
      },
    });

    const staging = reducer(ready, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-new',
          chunk_index: 0,
          complete: false,
          current_room_id: 3,
          rooms: [{ room_id: 3, name: 'Nowy', region: 'Astergard', x: 2, y: 0, z: 0 }],
          edges: [],
        },
        sequence: 2,
      },
    });

    const updateDuringStaging = reducer(staging, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.update',
        payload: {
          map_version: 1,
          sync_id: 'sync-ready',
          current_room_id: 2,
          rooms: [{ room_id: 2, name: 'Ścieżka', region: 'Astergard', x: 1, y: 0, z: 0 }],
          edges: [{ from_room_id: 1, to_room_id: 2, direction: 'wschod' }],
        },
        sequence: 3,
      },
    });
    expect(updateDuringStaging).toEqual(staging);

    const foreignUpdate = reducer(ready, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.update',
        payload: {
          map_version: 1,
          sync_id: 'sync-foreign',
          current_room_id: 2,
          rooms: [{ room_id: 2, name: 'Ścieżka', region: 'Astergard', x: 1, y: 0, z: 0 }],
          edges: [{ from_room_id: 1, to_room_id: 2, direction: 'wschod' }],
        },
        sequence: 4,
      },
    });
    expect(foreignUpdate).toEqual(ready);

    const validUpdate = reducer(ready, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.update',
        payload: {
          map_version: 1,
          sync_id: 'sync-ready',
          current_room_id: 3,
          rooms: [
            { room_id: 2, name: 'Ścieżka', region: 'Astergard', x: 1, y: 0, z: 0 },
            { room_id: 3, name: 'Nowy', region: 'Astergard', x: 2, y: 0, z: 0 },
          ],
          edges: [
            { from_room_id: 1, to_room_id: 2, direction: 'wschod' },
            { from_room_id: 2, to_room_id: 3, direction: 'poludnie' },
            { from_room_id: 2, to_room_id: 3, direction: 'poludnie' },
          ],
        },
        sequence: 5,
      },
    });
    expect(validUpdate.map.currentRoomId).toBe(3);
    expect(Object.keys(validUpdate.map.roomsById).sort()).toEqual(['1', '2', '3']);
    expect(validUpdate.map.edges).toEqual([
      { from_room_id: 1, to_room_id: 2, direction: 'wschod' },
      { from_room_id: 2, to_room_id: 3, direction: 'poludnie' },
    ]);

    const repeatedUpdate = reducer(validUpdate, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.update',
        payload: {
          map_version: 1,
          sync_id: 'sync-ready',
          current_room_id: 3,
          rooms: [
            { room_id: 2, name: 'Ścieżka', region: 'Astergard', x: 1, y: 0, z: 0 },
            { room_id: 3, name: 'Nowy', region: 'Astergard', x: 2, y: 0, z: 0 },
          ],
          edges: [
            { from_room_id: 1, to_room_id: 2, direction: 'wschod' },
            { from_room_id: 2, to_room_id: 3, direction: 'poludnie' },
          ],
        },
        sequence: 6,
      },
    });
    expect(repeatedUpdate).toEqual(validUpdate);

    const invalidUpdate = reducer(validUpdate, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.update',
        payload: {
          map_version: 1,
          sync_id: 'sync-ready',
          current_room_id: 999,
          rooms: [{ room_id: 3, name: 'Nowy', region: 'Astergard', x: 2, y: 0, z: 0 }],
          edges: [{ from_room_id: 2, to_room_id: 999, direction: 'poludnie' }],
        },
        sequence: 7,
      },
    });
    expect(invalidUpdate).toEqual(validUpdate);

    const disconnected = reducer(validUpdate, { kind: 'transport-state', state: 'disconnected' });
    expect(disconnected.map.syncStatus).toBe('idle');
    expect(disconnected.map.currentRoomId).toBeNull();
    expect(disconnected.map.roomsById).toEqual({});
    expect(disconnected.map.edges).toEqual([]);
  });

  it('assembles a 500-room snapshot without losing rooms or edges', () => {
    const rooms = Array.from({ length: 500 }, (_, index) => ({
      room_id: index + 1,
      name: `Pokój ${index + 1}`,
      region: 'Astergard',
      x: index,
      y: 0,
      z: 0,
    }));

    const firstHalf = reducer(initialState, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-500',
          chunk_index: 0,
          complete: false,
          current_room_id: 1,
          rooms: rooms.slice(0, 250),
          edges: [],
        },
        sequence: 1,
      },
    });
    expect(firstHalf.map.syncStatus).toBe('syncing');
    expect(firstHalf.map.pendingSnapshot).not.toBeNull();
    expect(firstHalf.map.roomsById).toEqual({});

    const completed = reducer(firstHalf, {
      kind: 'message',
      envelope: {
        version: 1,
        type: 'map.snapshot',
        payload: {
          map_version: 1,
          sync_id: 'sync-500',
          chunk_index: 1,
          complete: true,
          current_room_id: 1,
          rooms: rooms.slice(250),
          edges: [],
        },
        sequence: 2,
      },
    });
    expect(completed.map.syncStatus).toBe('ready');
    expect(Object.keys(completed.map.roomsById)).toHaveLength(500);
    expect(completed.map.roomsById[1]?.name).toBe('Pokój 1');
    expect(completed.map.roomsById[500]?.name).toBe('Pokój 500');
    expect(completed.map.pendingSnapshot).toBeNull();
  });
});
