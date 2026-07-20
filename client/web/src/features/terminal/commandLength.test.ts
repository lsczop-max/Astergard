import { describe, expect, it } from 'vitest';
import { MAX_COMMAND_BYTES } from '../../protocol/webProtocol';
import { utf8ByteLength } from './commandLength';

describe('utf8ByteLength', () => {
  it('counts ASCII, Polish characters, and emoji in UTF-8 bytes', () => {
    expect(utf8ByteLength('a'.repeat(MAX_COMMAND_BYTES))).toBe(MAX_COMMAND_BYTES);
    expect(utf8ByteLength('a'.repeat(MAX_COMMAND_BYTES + 1))).toBe(MAX_COMMAND_BYTES + 1);
    expect(utf8ByteLength('ż')).toBe(2);
    expect(utf8ByteLength('😀')).toBe(4);
  });

  it('distinguishes character count from byte count', () => {
    expect('ż'.repeat(300).length).toBe(300);
    expect(utf8ByteLength('ż'.repeat(300))).toBeGreaterThan(MAX_COMMAND_BYTES);
  });
});
