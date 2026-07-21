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
});
