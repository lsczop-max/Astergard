import { MAX_COMMAND_BYTES } from '../../protocol/webProtocol';
import { utf8ByteLength as encodeUtf8ByteLength } from '../../protocol/utf8';

export function utf8ByteLength(value: string): number {
  return encodeUtf8ByteLength(value);
}

export function isWithinCommandByteLimit(value: string): boolean {
  return utf8ByteLength(value) <= MAX_COMMAND_BYTES;
}
