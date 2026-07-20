import { MAX_COMMAND_BYTES } from '../../protocol/webProtocol';

const UTF8_ENCODER = new TextEncoder();

export function utf8ByteLength(value: string): number {
  return UTF8_ENCODER.encode(value).byteLength;
}

export function isWithinCommandByteLimit(value: string): boolean {
  return utf8ByteLength(value) <= MAX_COMMAND_BYTES;
}
