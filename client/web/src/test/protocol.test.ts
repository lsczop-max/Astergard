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
});
