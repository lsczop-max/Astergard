import { describe, expect, it } from 'vitest';
import { utf8ByteLength } from '../protocol/utf8';
import { MAP_CONTRACT_VERSION, MAX_CREATOR_STEP_ID_BYTES, MAX_SAFE_INTEGER, parseProtocolEnvelope, serializeWebEnvelope } from '../protocol/webProtocol';

describe('protocol validation', () => {
  it('rejects sequence duplicate and regression fields', () => {
    expect(() =>
      parseProtocolEnvelope('{"version":1,"type":"output.text","payload":{"text":"a"},"sequence":0}'),
    ).toThrow(/positive integer/);

    const serialized = serializeWebEnvelope({
      version: 1,
      type: 'session.hello',
      payload: {
        client: 'Astergard Web',
        client_version: 'D59.4',
        transport: 'websocket',
      },
      request_id: 'req-hello',
    });

    expect(serialized).toBe(
      '{"version":1,"type":"session.hello","payload":{"client":"Astergard Web","client_version":"D59.4","transport":"websocket"},"request_id":"req-hello"}',
    );

    const parsed = parseProtocolEnvelope(serialized);
    expect(parsed).toEqual({
      version: 1,
      type: 'session.hello',
      payload: {
        client: 'Astergard Web',
        client_version: 'D59.4',
        transport: 'websocket',
      },
      request_id: 'req-hello',
    });
    expect(Object.prototype.hasOwnProperty.call(parsed, 'sequence')).toBe(false);
  });

  it('rejects empty and whitespace-only command.execute payloads', () => {
    expect(() =>
      serializeWebEnvelope({
        version: 1,
        type: 'command.execute',
        payload: { command: '' },
        request_id: 'req-1',
      }),
    ).toThrow(/non-empty string/);

    expect(() =>
      serializeWebEnvelope({
        version: 1,
        type: 'command.execute',
        payload: { command: '   ' },
        request_id: 'req-2',
      }),
    ).toThrow(/non-whitespace characters/);

    const serialized = serializeWebEnvelope({
      version: 1,
      type: 'command.execute',
      payload: { command: 'spojrz' },
      request_id: 'req-3',
    });
    expect(serialized).toContain('"command":"spojrz"');
  });

  it('round-trips creator.validation_error with an optional code', () => {
    const serialized = serializeWebEnvelope({
      version: 1,
      type: 'creator.validation_error',
      payload: {
        step_id: 'special_feature',
        field: 'value',
        code: 'creator_value_too_long',
        message: 'Odpowiedź jest zbyt długa.',
      },
      request_id: 'creator-1',
    });

    const parsed = parseProtocolEnvelope(serialized);
    expect(parsed).toEqual({
      version: 1,
      type: 'creator.validation_error',
      payload: {
        step_id: 'special_feature',
        field: 'value',
        code: 'creator_value_too_long',
        message: 'Odpowiedź jest zbyt długa.',
      },
      request_id: 'creator-1',
    });
  });

  it('accepts only the exact creator.submit shape and rejects invalid payloads', () => {
    const valid = parseProtocolEnvelope(
      JSON.stringify({
        version: 1,
        type: 'creator.submit',
        payload: {
          step_id: 'special_feature',
          value: 'blizna_policzek',
        },
        request_id: 'creator-submit-1',
      }),
    );

    expect(valid).toEqual({
      version: 1,
      type: 'creator.submit',
      payload: {
        step_id: 'special_feature',
        value: 'blizna_policzek',
      },
      request_id: 'creator-submit-1',
    });

    const invalidPayloads = [
      JSON.stringify({ version: 1, type: 'creator.submit', payload: { value: 'blizna_policzek' }, request_id: 'missing-step-id' }),
      JSON.stringify({ version: 1, type: 'creator.submit', payload: { step_id: 'special_feature' }, request_id: 'missing-value' }),
      JSON.stringify({
        version: 1,
        type: 'creator.submit',
        payload: { step_id: 'special_feature', value: 'blizna_policzek', extra: true },
        request_id: 'extra-field',
      }),
      JSON.stringify({ version: 1, type: 'creator.submit', payload: { step_id: 123, value: 'blizna_policzek' }, request_id: 'bad-step-id' }),
      JSON.stringify({ version: 1, type: 'creator.submit', payload: { step_id: 'special_feature', value: 123 }, request_id: 'bad-value' }),
    ];

    for (const raw of invalidPayloads) {
      expect(() => parseProtocolEnvelope(raw)).toThrow();
    }
  });

  it('accepts public room.info special_exits and rejects hidden metadata', () => {
    const valid = JSON.stringify({
      version: 1,
      type: 'room.info',
      payload: {
        num: 7,
        name: 'Most przy bramie',
        area: 'Centrum_Twierdza',
        coords: { x: 1, y: 2, z: 0 },
        exits: { n: 8 },
        special_exits: [
          {
            direction: 'sekretny-most',
            target: 61,
            kind: 'most',
            visible: true,
            door: true,
            locked: false,
          },
        ],
      },
      sequence: 1,
    });
    expect(parseProtocolEnvelope(valid)).toEqual({
      version: 1,
      type: 'room.info',
      payload: {
        num: 7,
        name: 'Most przy bramie',
        area: 'Centrum_Twierdza',
        coords: { x: 1, y: 2, z: 0 },
        exits: { n: 8 },
        special_exits: [
          {
            direction: 'sekretny-most',
            target: 61,
            kind: 'most',
            visible: true,
            door: true,
            locked: false,
          },
        ],
      },
      sequence: 1,
    });

    expect(() =>
      parseProtocolEnvelope(
        JSON.stringify({
          version: 1,
          type: 'room.info',
          payload: {
            num: 7,
            name: 'Most przy bramie',
            area: 'Centrum_Twierdza',
            coords: { x: 1, y: 2, z: 0 },
            exits: { n: 8 },
            special_exits: [
              {
                direction: 'sekretny-most',
                target: 61,
                kind: 'most',
                visible: true,
                door: true,
                locked: false,
                hidden: true,
              },
            ],
          },
          sequence: 1,
        }),
      ),
    ).toThrow(/unknown fields/);
  });

  it('round-trips public map.snapshot and map.update payloads with strict shapes', () => {
    const snapshot = {
      map_version: MAP_CONTRACT_VERSION,
      sync_id: 'sync-1',
      chunk_index: 0,
      complete: false,
      current_room_id: 1,
      rooms: [
        { room_id: 1, name: 'Start', region: 'Astergard', x: 0, y: 0, z: 0 },
        { room_id: 2, name: 'Ścieżka', region: 'Astergard', x: 1, y: 0, z: 0 },
      ],
      edges: [{ from_room_id: 1, to_room_id: 2, direction: 'wschod' }],
    } as const;
    expect(parseProtocolEnvelope(JSON.stringify({ version: 1, type: 'map.snapshot', payload: snapshot, sequence: 1 }))).toEqual({
      version: 1,
      type: 'map.snapshot',
      payload: snapshot,
      sequence: 1,
    });

    const update = {
      map_version: MAP_CONTRACT_VERSION,
      sync_id: 'sync-1',
      current_room_id: 2,
      rooms: [{ room_id: 2, name: 'Ścieżka', region: 'Astergard', x: 1, y: 0, z: 0 }],
      edges: [{ from_room_id: 1, to_room_id: 2, direction: 'wschod' }],
    } as const;
    expect(parseProtocolEnvelope(JSON.stringify({ version: 1, type: 'map.update', payload: update, sequence: 2 }))).toEqual({
      version: 1,
      type: 'map.update',
      payload: update,
      sequence: 2,
    });

    const invalidSnapshotPayloads = [
      JSON.stringify({ version: 1, type: 'map.snapshot', payload: { ...snapshot, rooms: [{ room_id: 1, name: 'Start', region: 'Astergard', x: 0, y: 0, z: 0 }, { room_id: 1, name: 'Dup', region: 'Astergard', x: 1, y: 0, z: 0 }] }, sequence: 1 }),
      JSON.stringify({ version: 1, type: 'map.snapshot', payload: { ...snapshot, rooms: [{ room_id: '1', name: 'Start', region: 'Astergard', x: 0, y: 0, z: 0 }] }, sequence: 1 }),
      JSON.stringify({ version: 1, type: 'map.snapshot', payload: { ...snapshot, rooms: [{ room_id: Number.MAX_SAFE_INTEGER + 1, name: 'Start', region: 'Astergard', x: 0, y: 0, z: 0 }] }, sequence: 1 }),
      JSON.stringify({ version: 1, type: 'map.snapshot', payload: { ...snapshot, rooms: [{ room_id: 1.5, name: 'Start', region: 'Astergard', x: 0, y: 0, z: 0 }] }, sequence: 1 }),
      '{"version":1,"type":"map.snapshot","payload":{"map_version":1,"sync_id":"sync-1","chunk_index":0,"complete":false,"current_room_id":1,"rooms":[{"room_id":NaN,"name":"Start","region":"Astergard","x":0,"y":0,"z":0}],"edges":[]},"sequence":1}',
      '{"version":1,"type":"map.snapshot","payload":{"map_version":1,"sync_id":"sync-1","chunk_index":0,"complete":false,"current_room_id":1,"rooms":[{"room_id":Infinity,"name":"Start","region":"Astergard","x":0,"y":0,"z":0}],"edges":[]},"sequence":1}',
      '{"version":1,"type":"map.snapshot","payload":{"map_version":1,"sync_id":"sync-1","chunk_index":0,"complete":false,"current_room_id":1,"rooms":[{"room_id":1,"name":"Start","region":"Astergard","x":0,"y":0,"z":0},{"room_id":null,"name":"Dup","region":"Astergard","x":1,"y":0,"z":0}],"edges":[]},"sequence":1}',
      '{"version":1,"type":"map.snapshot","payload":{"map_version":1,"sync_id":"sync-1","chunk_index":0,"complete":false,"current_room_id":1,"rooms":[{"room_id":1,"name":"Start","region":"Astergard","x":0,"y":0,"z":0},{"room_id":2,"name":"Dup","region":"Astergard","x":1,"y":0,"z":0.5}],"edges":[]},"sequence":1}',
      JSON.stringify({ version: 1, type: 'map.snapshot', payload: { ...snapshot, edges: [{ from_room_id: 1, to_room_id: 2, direction: 'sekret' }] }, sequence: 1 }),
      JSON.stringify({ version: 1, type: 'map.snapshot', payload: { ...snapshot, current_room_id: '1' }, sequence: 1 }),
      JSON.stringify({ version: 1, type: 'map.snapshot', payload: { ...snapshot, chunk_index: 1.5 }, sequence: 1 }),
      JSON.stringify({ version: 1, type: 'map.snapshot', payload: { ...snapshot, extra: true }, sequence: 1 }),
    ];
    for (const raw of invalidSnapshotPayloads) {
      expect(() => parseProtocolEnvelope(raw)).toThrow();
    }

    const invalidUpdatePayloads = [
      JSON.stringify({ version: 1, type: 'map.update', payload: { ...update, current_room_id: '2' }, sequence: 2 }),
      JSON.stringify({ version: 1, type: 'map.update', payload: { ...update, edges: [{ from_room_id: 1, to_room_id: '2', direction: 'wschod' }] }, sequence: 2 }),
      JSON.stringify({ version: 1, type: 'map.update', payload: { ...update, edges: [{ from_room_id: 1, to_room_id: 2.5, direction: 'wschod' }] }, sequence: 2 }),
      JSON.stringify({ version: 1, type: 'map.update', payload: { ...update, edges: [{ from_room_id: Number.MAX_SAFE_INTEGER + 1, to_room_id: 2, direction: 'wschod' }] }, sequence: 2 }),
      '{"version":1,"type":"map.update","payload":{"map_version":1,"sync_id":"sync-1","current_room_id":2,"rooms":[{"room_id":1,"name":"Start","region":"Astergard","x":0,"y":0,"z":0},{"room_id":2,"name":"Ścieżka","region":"Astergard","x":1,"y":0,"z":Infinity}],"edges":[{"from_room_id":1,"to_room_id":2,"direction":"wschod"}]},"sequence":2}',
      '{"version":1,"type":"map.update","payload":{"map_version":1,"sync_id":"sync-1","current_room_id":2,"rooms":[{"room_id":1,"name":"Start","region":"Astergard","x":0,"y":0,"z":0},{"room_id":2,"name":"Ścieżka","region":"Astergard","x":1.25,"y":0,"z":0}],"edges":[{"from_room_id":1,"to_room_id":2,"direction":"wschod"}]},"sequence":2}',
    ];
    for (const raw of invalidUpdatePayloads) {
      expect(() => parseProtocolEnvelope(raw)).toThrow();
    }

    expect(() =>
      parseProtocolEnvelope(
        JSON.stringify({
          version: 1,
          type: 'map.update',
          payload: { ...update, hidden: true },
          sequence: 2,
        }),
      ),
    ).toThrow(/unknown fields/);
  });

  it('enforces safe integer bounds for public map payloads', () => {
    const snapshot = {
      map_version: MAP_CONTRACT_VERSION,
      sync_id: 'sync-safe',
      chunk_index: MAX_SAFE_INTEGER,
      complete: false,
      current_room_id: MAX_SAFE_INTEGER,
      rooms: [
        {
          room_id: MAX_SAFE_INTEGER,
          name: 'Pokój bezpieczny',
          region: 'Astergard',
          x: -MAX_SAFE_INTEGER,
          y: 0,
          z: MAX_SAFE_INTEGER,
        },
      ],
      edges: [],
    } as const;
    expect(parseProtocolEnvelope(JSON.stringify({ version: 1, type: 'map.snapshot', payload: snapshot, sequence: 1 }))).toEqual({
      version: 1,
      type: 'map.snapshot',
      payload: snapshot,
      sequence: 1,
    });

    const update = {
      map_version: MAP_CONTRACT_VERSION,
      sync_id: 'sync-safe',
      current_room_id: MAX_SAFE_INTEGER,
      rooms: [
        {
          room_id: MAX_SAFE_INTEGER,
          name: 'Pokój bezpieczny',
          region: 'Astergard',
          x: -MAX_SAFE_INTEGER,
          y: 0,
          z: MAX_SAFE_INTEGER,
        },
      ],
      edges: [],
    } as const;
    expect(parseProtocolEnvelope(JSON.stringify({ version: 1, type: 'map.update', payload: update, sequence: 2 }))).toEqual({
      version: 1,
      type: 'map.update',
      payload: update,
      sequence: 2,
    });

    const invalidPayloads = [
      JSON.stringify({ version: 1, type: 'map.snapshot', payload: { ...snapshot, chunk_index: MAX_SAFE_INTEGER + 1 }, sequence: 1 }),
      JSON.stringify({ version: 1, type: 'map.snapshot', payload: { ...snapshot, current_room_id: MAX_SAFE_INTEGER + 1 }, sequence: 1 }),
      JSON.stringify({ version: 1, type: 'map.snapshot', payload: { ...snapshot, rooms: [{ room_id: MAX_SAFE_INTEGER + 1, name: 'Start', region: 'Astergard', x: 0, y: 0, z: 0 }] }, sequence: 1 }),
      JSON.stringify({ version: 1, type: 'map.snapshot', payload: { ...snapshot, rooms: [{ room_id: 1, name: 'Start', region: 'Astergard', x: -MAX_SAFE_INTEGER - 1, y: 0, z: 0 }] }, sequence: 1 }),
      JSON.stringify({ version: 1, type: 'map.snapshot', payload: { ...snapshot, map_version: 2 }, sequence: 1 }),
      JSON.stringify({ version: 1, type: 'map.snapshot', payload: { ...snapshot, rooms: [{ room_id: true, name: 'Start', region: 'Astergard', x: 0, y: 0, z: 0 }] }, sequence: 1 }),
      JSON.stringify({ version: 1, type: 'map.snapshot', payload: { ...snapshot, rooms: [{ room_id: 1.5, name: 'Start', region: 'Astergard', x: 0, y: 0, z: 0 }] }, sequence: 1 }),
      JSON.stringify({ version: 1, type: 'map.update', payload: { ...update, current_room_id: MAX_SAFE_INTEGER + 1 }, sequence: 2 }),
      JSON.stringify({ version: 1, type: 'map.update', payload: { ...update, rooms: [{ room_id: MAX_SAFE_INTEGER + 1, name: 'Start', region: 'Astergard', x: 0, y: 0, z: 0 }] }, sequence: 2 }),
      '{"version":1,"type":"map.update","payload":{"map_version":1,"sync_id":"sync-safe","current_room_id":1,"rooms":[{"room_id":1,"name":"Start","region":"Astergard","x":0,"y":0,"z":Infinity}],"edges":[]},"sequence":2}',
    ];
    for (const raw of invalidPayloads) {
      expect(() => parseProtocolEnvelope(raw)).toThrow();
    }
  });

  it('enforces 64-byte UTF-8 step_id limits across creator messages', () => {
    const stepId64 = 'ż'.repeat(32);
    const stepId65 = `${stepId64}a`;
    expect(utf8ByteLength(stepId64)).toBe(MAX_CREATOR_STEP_ID_BYTES);
    expect(utf8ByteLength(stepId65)).toBe(MAX_CREATOR_STEP_ID_BYTES + 1);

    const submit64 = JSON.stringify({
      version: 1,
      type: 'creator.submit',
      payload: { step_id: stepId64, value: 'blizna_policzek' },
      request_id: 'submit-64',
    });
    expect(parseProtocolEnvelope(submit64)).toEqual({
      version: 1,
      type: 'creator.submit',
      payload: { step_id: stepId64, value: 'blizna_policzek' },
      request_id: 'submit-64',
    });
    expect(() =>
      parseProtocolEnvelope(
        JSON.stringify({
          version: 1,
          type: 'creator.submit',
          payload: { step_id: stepId65, value: 'blizna_policzek' },
          request_id: 'submit-65',
        }),
      ),
    ).toThrow(/step_id/);

    const step64 = JSON.stringify({
      version: 1,
      type: 'creator.step',
      payload: {
        step_id: stepId64,
        title: 'Cechy szczególne',
        prompt: 'Wybierz cechę szczególną.',
        input_type: 'choice',
        choices: [{ value: 'blizna_policzek', label: 'wąska blizna na policzku' }],
        back_available: true,
        cancel_available: true,
      },
      request_id: 'step-64',
      sequence: 1,
    });
    expect(parseProtocolEnvelope(step64)).toEqual({
      version: 1,
      type: 'creator.step',
      payload: {
        step_id: stepId64,
        title: 'Cechy szczególne',
        prompt: 'Wybierz cechę szczególną.',
        input_type: 'choice',
        choices: [{ value: 'blizna_policzek', label: 'wąska blizna na policzku' }],
        back_available: true,
        cancel_available: true,
      },
      request_id: 'step-64',
      sequence: 1,
    });
    expect(() =>
      parseProtocolEnvelope(
        JSON.stringify({
          version: 1,
          type: 'creator.step',
          payload: {
            step_id: stepId65,
            title: 'Cechy szczególne',
            prompt: 'Wybierz cechę szczególną.',
            input_type: 'choice',
            choices: [{ value: 'blizna_policzek', label: 'wąska blizna na policzku' }],
            back_available: true,
            cancel_available: true,
          },
          request_id: 'step-65',
          sequence: 1,
        }),
      ),
    ).toThrow(/step_id/);

    const validationError64 = JSON.stringify({
      version: 1,
      type: 'creator.validation_error',
      payload: {
        step_id: stepId64,
        field: 'value',
        code: 'creator_value_too_long',
        message: 'Odpowiedź jest zbyt długa.',
      },
      request_id: 'validation-64',
      sequence: 2,
    });
    expect(parseProtocolEnvelope(validationError64)).toEqual({
      version: 1,
      type: 'creator.validation_error',
      payload: {
        step_id: stepId64,
        field: 'value',
        code: 'creator_value_too_long',
        message: 'Odpowiedź jest zbyt długa.',
      },
      request_id: 'validation-64',
      sequence: 2,
    });
    expect(() =>
      parseProtocolEnvelope(
        JSON.stringify({
          version: 1,
          type: 'creator.validation_error',
          payload: {
            step_id: stepId65,
            field: 'value',
            code: 'creator_value_too_long',
            message: 'Odpowiedź jest zbyt długa.',
          },
          request_id: 'validation-65',
          sequence: 2,
        }),
      ),
    ).toThrow(/step_id/);
  });

  it('rejects null, arrays and invalid character vitals', () => {
    expect(() =>
      parseProtocolEnvelope('{"version":1,"type":"command.execute","payload":null,"request_id":"req-1"}'),
    ).toThrow(/Protocol payload must be an object/);

    expect(() =>
      parseProtocolEnvelope('{"version":1,"type":"command.execute","payload":[],"request_id":"req-1"}'),
    ).toThrow(/Protocol payload must be an object/);

    expect(() =>
      parseProtocolEnvelope(
        '{"version":1,"type":"character.vitals","payload":{"condition_current":1,"condition_max":12,"stamina_current":1,"stamina_max":100},"sequence":1}',
      ),
    ).not.toThrow();

    expect(() =>
      parseProtocolEnvelope(
        '{"version":1,"type":"character.vitals","payload":{"condition_current":true,"condition_max":12,"stamina_current":1,"stamina_max":100},"sequence":1}',
      ),
    ).toThrow(/must be an integer/);

    expect(() =>
      parseProtocolEnvelope(
        '{"version":1,"type":"character.vitals","payload":{"condition_current":1,"condition_max":12,"stamina_current":1,"stamina_max":100,"condition_label":"ok","stamina_label":"ok"},"sequence":1}',
      ),
    ).not.toThrow();
  });
});
