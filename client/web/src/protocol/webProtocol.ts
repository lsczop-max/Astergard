export const WEB_PROTOCOL_VERSION = 1 as const;
export const MAX_PROTOCOL_MESSAGE_BYTES = 8192;
export const MAX_COMMAND_BYTES = 512;

export type ClientMessageType = 'session.hello' | 'auth.login' | 'command.execute' | 'connection.ping';
export type ServerMessageType =
  | 'session.ready'
  | 'auth.result'
  | 'output.text'
  | 'output.prompt'
  | 'room.info'
  | 'command.result'
  | 'connection.pong'
  | 'protocol.error';

export type RequestMessageType = ClientMessageType;
export type StreamMessageType = 'session.ready' | 'output.text' | 'output.prompt' | 'room.info';
export type ResponseMessageType = 'auth.result' | 'command.result' | 'connection.pong' | 'protocol.error';

export interface SessionHelloPayload {
  client?: string;
  client_version?: string;
  transport?: string;
  capabilities?: string[];
}

export interface AuthLoginPayload {
  username: string;
  password: string;
}

export interface CommandExecutePayload {
  command: string;
}

export interface ConnectionPingPayload {
  nonce?: string;
}

export interface SessionReadyPayload {
  transport: string;
  username?: string;
}

export interface AuthResultPayload {
  success: boolean;
  username: string;
  reason?: string;
}

export interface OutputTextPayload {
  text: string;
}

export interface OutputPromptPayload {
  prompt: string;
}

export interface RoomInfoPayload {
  num: number;
  name: string;
  area: string;
  coords: {
    x: number;
    y: number;
    z: number;
  };
  exits: Record<string, number>;
  area_label?: string;
  terrain?: string;
  special_exits?: unknown[];
}

export interface CommandResultPayload {
  command: string;
  success: boolean;
}

export interface ConnectionPongPayload {
  nonce?: string;
}

export interface ProtocolErrorPayload {
  code: string;
  message: string;
}

type Envelope<TType extends string, TPayload> = {
  version: 1;
  type: TType;
  payload: TPayload;
  request_id?: string;
  sequence?: number;
};

export type ClientEnvelope =
  | Envelope<'session.hello', SessionHelloPayload>
  | Envelope<'auth.login', AuthLoginPayload>
  | Envelope<'command.execute', CommandExecutePayload>
  | Envelope<'connection.ping', ConnectionPingPayload>;

export type ServerEnvelope =
  | Envelope<'session.ready', SessionReadyPayload>
  | Envelope<'auth.result', AuthResultPayload>
  | Envelope<'output.text', OutputTextPayload>
  | Envelope<'output.prompt', OutputPromptPayload>
  | Envelope<'room.info', RoomInfoPayload>
  | Envelope<'command.result', CommandResultPayload>
  | Envelope<'connection.pong', ConnectionPongPayload>
  | Envelope<'protocol.error', ProtocolErrorPayload>;

export type ProtocolEnvelope = ClientEnvelope | ServerEnvelope;

export class ProtocolError extends Error {
  readonly code: string;

  constructor(code: string, message: string) {
    super(message);
    this.code = code;
    this.name = 'ProtocolError';
  }
}

const CLIENT_MESSAGE_TYPES = new Set<ClientMessageType>(['session.hello', 'auth.login', 'command.execute', 'connection.ping']);
const SERVER_MESSAGE_TYPES = new Set<ServerMessageType>([
  'session.ready',
  'auth.result',
  'output.text',
  'output.prompt',
  'room.info',
  'command.result',
  'connection.pong',
  'protocol.error',
]);
const REQUEST_MESSAGE_TYPES = new Set<RequestMessageType>(['session.hello', 'auth.login', 'command.execute', 'connection.ping']);
const STREAM_MESSAGE_TYPES = new Set<StreamMessageType>(['session.ready', 'output.text', 'output.prompt', 'room.info']);
const RESPONSE_MESSAGE_TYPES = new Set<ResponseMessageType>(['auth.result', 'command.result', 'connection.pong', 'protocol.error']);

function fail(code: string, message: string): never {
  throw new ProtocolError(code, message);
}

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function isExactNumber(value: unknown): value is number {
  return typeof value === 'number' && Number.isInteger(value) && Number.isFinite(value);
}

function requireString(value: unknown, field: string, options?: { allowEmpty?: boolean; maxBytes?: number }): string {
  if (typeof value !== 'string') {
    fail('invalid_payload', `Payload field '${field}' must be a string.`);
  }
  if (!options?.allowEmpty && value === '') {
    fail('invalid_payload', `Payload field '${field}' must be a non-empty string.`);
  }
  if (options?.maxBytes !== undefined && byteLength(value) > options.maxBytes) {
    fail('message_too_large', `Payload field '${field}' exceeds the limit.`);
  }
  return value;
}

function requireAllowedKeys(payload: Record<string, unknown>, allowed: readonly string[]): void {
  const unexpected = Object.keys(payload).filter((key) => !allowed.includes(key));
  if (unexpected.length > 0) {
    fail('invalid_payload', 'Protocol payload contains unknown fields.');
  }
}

function validateSessionHello(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['client', 'client_version', 'capabilities', 'transport']);
  if ('client' in payload) requireString(payload.client, 'client', { maxBytes: MAX_COMMAND_BYTES });
  if ('client_version' in payload) requireString(payload.client_version, 'client_version', { maxBytes: MAX_COMMAND_BYTES });
  if ('transport' in payload) requireString(payload.transport, 'transport', { maxBytes: MAX_COMMAND_BYTES });
  if ('capabilities' in payload) {
    if (!Array.isArray(payload.capabilities)) {
      fail('invalid_payload', "Payload field 'capabilities' must be an array.");
    }
    for (const capability of payload.capabilities) {
      if (typeof capability !== 'string' || capability === '') {
        fail('invalid_payload', "Payload field 'capabilities' must contain strings.");
      }
    }
  }
}

function validateAuthLogin(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['username', 'password']);
  requireString(payload.username, 'username', { maxBytes: MAX_COMMAND_BYTES });
  requireString(payload.password, 'password', { maxBytes: MAX_COMMAND_BYTES });
}

function validateCommandExecute(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['command']);
  requireString(payload.command, 'command', { maxBytes: MAX_COMMAND_BYTES });
}

function validateConnectionPing(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['nonce']);
  if ('nonce' in payload) {
    requireString(payload.nonce, 'nonce', { allowEmpty: true, maxBytes: MAX_COMMAND_BYTES });
  }
}

function validateSessionReady(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['transport', 'username']);
  requireString(payload.transport, 'transport', { maxBytes: MAX_COMMAND_BYTES });
  if ('username' in payload) requireString(payload.username, 'username', { maxBytes: MAX_COMMAND_BYTES });
}

function validateAuthResult(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['success', 'username', 'reason']);
  if (typeof payload.success !== 'boolean') {
    fail('invalid_payload', "Payload field 'success' must be a boolean.");
  }
  requireString(payload.username, 'username', { maxBytes: MAX_COMMAND_BYTES });
  if ('reason' in payload) requireString(payload.reason, 'reason', { allowEmpty: true, maxBytes: MAX_COMMAND_BYTES });
}

function validateTextPayload(payload: Record<string, unknown>, field: 'text' | 'prompt'): void {
  requireAllowedKeys(payload, [field]);
  requireString(payload[field], field, { allowEmpty: true });
}

function validateRoomInfo(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['num', 'name', 'area', 'coords', 'exits', 'area_label', 'terrain', 'special_exits']);
  if (!isExactNumber(payload.num) || payload.num < 0) fail('invalid_payload', "Payload field 'num' must be a non-negative integer.");
  requireString(payload.name, 'name', { maxBytes: MAX_COMMAND_BYTES });
  requireString(payload.area, 'area', { maxBytes: MAX_COMMAND_BYTES });
  if (!isPlainObject(payload.coords)) fail('invalid_payload', "Payload field 'coords' must be an object.");
  for (const axis of ['x', 'y', 'z'] as const) {
    if (!isExactNumber(payload.coords[axis])) {
      fail('invalid_payload', `Payload field 'coords.${axis}' must be an integer.`);
    }
  }
  if (!isPlainObject(payload.exits)) fail('invalid_payload', "Payload field 'exits' must be an object.");
  for (const [direction, target] of Object.entries(payload.exits)) {
    if (direction === '') fail('invalid_payload', "Payload field 'exits' must use string keys.");
    if (!isExactNumber(target) || target < 0) {
      fail('invalid_payload', `Payload field 'exits.${direction}' must be a non-negative integer.`);
    }
  }
  if ('area_label' in payload) requireString(payload.area_label, 'area_label', { maxBytes: MAX_COMMAND_BYTES });
  if ('terrain' in payload) requireString(payload.terrain, 'terrain', { maxBytes: MAX_COMMAND_BYTES });
  if ('special_exits' in payload && !Array.isArray(payload.special_exits)) {
    fail('invalid_payload', "Payload field 'special_exits' must be an array.");
  }
}

function validateCommandResult(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['command', 'success']);
  requireString(payload.command, 'command', { maxBytes: MAX_COMMAND_BYTES });
  if (typeof payload.success !== 'boolean') fail('invalid_payload', "Payload field 'success' must be a boolean.");
}

function validateConnectionPong(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['nonce']);
  if ('nonce' in payload) requireString(payload.nonce, 'nonce', { allowEmpty: true, maxBytes: MAX_COMMAND_BYTES });
}

function validateProtocolError(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['code', 'message']);
  requireString(payload.code, 'code', { maxBytes: MAX_COMMAND_BYTES });
  requireString(payload.message, 'message', { allowEmpty: true, maxBytes: MAX_COMMAND_BYTES });
}

function validatePayload(type: string, payload: Record<string, unknown>): void {
  if (type === 'session.hello') return validateSessionHello(payload);
  if (type === 'auth.login') return validateAuthLogin(payload);
  if (type === 'command.execute') return validateCommandExecute(payload);
  if (type === 'connection.ping') return validateConnectionPing(payload);
  if (type === 'session.ready') return validateSessionReady(payload);
  if (type === 'auth.result') return validateAuthResult(payload);
  if (type === 'output.text') return validateTextPayload(payload, 'text');
  if (type === 'output.prompt') return validateTextPayload(payload, 'prompt');
  if (type === 'room.info') return validateRoomInfo(payload);
  if (type === 'command.result') return validateCommandResult(payload);
  if (type === 'connection.pong') return validateConnectionPong(payload);
  if (type === 'protocol.error') return validateProtocolError(payload);
}

function validateRequestMetadata(type: string, requestId: unknown, sequence: unknown): void {
  if (REQUEST_MESSAGE_TYPES.has(type as RequestMessageType)) {
    if (typeof requestId !== 'string' || requestId === '') fail('invalid_request_id', 'Request messages require a non-empty string request_id.');
    if (sequence !== undefined) fail('invalid_envelope', 'Request messages must not include sequence.');
    return;
  }
  if (STREAM_MESSAGE_TYPES.has(type as StreamMessageType)) {
    if (!isExactNumber(sequence) || sequence < 1) fail('invalid_sequence', 'Stream messages require a positive integer sequence.');
    if (requestId !== undefined) fail('invalid_envelope', 'Stream messages must not include request_id.');
    return;
  }
  if (RESPONSE_MESSAGE_TYPES.has(type as ResponseMessageType)) {
    if (typeof requestId !== 'string' || requestId === '') fail('invalid_request_id', 'Response messages require a non-empty string request_id.');
    if (sequence !== undefined && (!isExactNumber(sequence) || sequence < 1)) fail('invalid_sequence', 'sequence must be a positive integer.');
  }
}

function decodeJson(raw: string | ArrayBuffer | Uint8Array): unknown {
  const bytes = typeof raw === 'string' ? new TextEncoder().encode(raw) : raw instanceof Uint8Array ? raw : new Uint8Array(raw);
  if (bytes.byteLength > MAX_PROTOCOL_MESSAGE_BYTES) {
    fail('message_too_large', 'Protocol message exceeds size limit.');
  }
  const text = new TextDecoder('utf-8', { fatal: true }).decode(bytes);
  return JSON.parse(text, (_key, value) => {
    if (typeof value === 'number' && !Number.isFinite(value)) {
      fail('invalid_json', 'Protocol message contains non-finite numbers.');
    }
    return value;
  });
}

function byteLength(value: string): number {
  return new TextEncoder().encode(value).byteLength;
}

export function serializeWebEnvelope(envelope: ProtocolEnvelope): string {
  const data: Record<string, unknown> = {
    version: envelope.version,
    type: envelope.type,
    payload: envelope.payload,
  };
  if (envelope.request_id !== undefined) data.request_id = envelope.request_id;
  if (envelope.sequence !== undefined) data.sequence = envelope.sequence;
  return JSON.stringify(data);
}

export function buildClientEnvelope<TType extends ClientMessageType>(
  type: TType,
  payload: Extract<ClientEnvelope, { type: TType }>['payload'],
  requestId: string,
): Extract<ClientEnvelope, { type: TType }> {
  if (typeof requestId !== 'string' || requestId === '') fail('invalid_request_id', 'request_id must be a non-empty string.');
  return { version: WEB_PROTOCOL_VERSION, type, payload, request_id: requestId } as Extract<ClientEnvelope, { type: TType }>;
}

export function parseProtocolEnvelope(raw: string | ArrayBuffer | Uint8Array): ProtocolEnvelope {
  const decoded = decodeJson(raw);
  if (!isPlainObject(decoded)) fail('invalid_envelope', 'Protocol envelope must be an object.');
  const keys = Object.keys(decoded);
  const allowed = ['version', 'type', 'payload', 'request_id', 'sequence'];
  if (keys.some((key) => !allowed.includes(key))) fail('invalid_envelope', 'Protocol envelope contains unknown fields.');
  if (typeof decoded.version !== 'number' || !Number.isInteger(decoded.version) || decoded.version !== WEB_PROTOCOL_VERSION) {
    fail('unsupported_version', 'Unsupported protocol version.');
  }
  if (typeof decoded.type !== 'string') fail('invalid_type', 'Protocol message type must be a string.');
  if (!CLIENT_MESSAGE_TYPES.has(decoded.type as ClientMessageType) && !SERVER_MESSAGE_TYPES.has(decoded.type as ServerMessageType)) {
    fail('unknown_type', 'Unknown protocol message type.');
  }
  if (!isPlainObject(decoded.payload)) fail('invalid_payload', 'Protocol payload must be an object.');
  validateRequestMetadata(decoded.type, decoded.request_id, decoded.sequence);
  validatePayload(decoded.type, decoded.payload);
  return {
    version: decoded.version,
    type: decoded.type,
    payload: decoded.payload,
    ...(decoded.request_id !== undefined ? { request_id: decoded.request_id } : {}),
    ...(decoded.sequence !== undefined ? { sequence: decoded.sequence } : {}),
  } as ProtocolEnvelope;
}
