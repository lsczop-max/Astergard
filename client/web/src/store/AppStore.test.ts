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

    const afterCommandResult = reducer(afterRoom, {
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
  });
});
