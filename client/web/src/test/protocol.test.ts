import { describe, expect, it } from 'vitest';
import { utf8ByteLength } from '../protocol/utf8';
import { MAX_CREATOR_STEP_ID_BYTES, parseProtocolEnvelope, serializeWebEnvelope } from '../protocol/webProtocol';

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
