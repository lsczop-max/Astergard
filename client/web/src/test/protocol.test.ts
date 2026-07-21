import { describe, expect, it } from 'vitest';
import { parseProtocolEnvelope, serializeWebEnvelope } from '../protocol/webProtocol';

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
