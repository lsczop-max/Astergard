export const WEB_PROTOCOL_VERSION = 1 as const;
export const MAX_PROTOCOL_MESSAGE_BYTES = 8192;
export const MAX_COMMAND_BYTES = 512;

export type ClientMessageType =
  | 'session.hello'
  | 'auth.login'
  | 'creator.start'
  | 'creator.submit'
  | 'creator.back'
  | 'creator.cancel'
  | 'command.execute'
  | 'connection.ping';
export type ServerMessageType =
  | 'session.ready'
  | 'auth.result'
  | 'character.vitals'
  | 'creator.started'
  | 'creator.step'
  | 'creator.validation_error'
  | 'creator.cancelled'
  | 'creator.finished'
  | 'output.text'
  | 'output.prompt'
  | 'room.info'
  | 'command.result'
  | 'connection.pong'
  | 'protocol.error';

export type RequestMessageType = ClientMessageType;
export type StreamMessageType = 'session.ready' | 'character.vitals' | 'output.text' | 'output.prompt' | 'room.info';
export type ResponseMessageType =
  | 'auth.result'
  | 'creator.started'
  | 'creator.step'
  | 'creator.validation_error'
  | 'creator.cancelled'
  | 'creator.finished'
  | 'command.result'
  | 'connection.pong'
  | 'protocol.error';

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

export interface CreatorStartPayload {
  username: string;
  password: string;
}

export interface CreatorSubmitPayload {
  step_id: string;
  value: string;
}

export interface CreatorBackPayload {
  step_id: string;
}

export interface CreatorCancelPayload {
  step_id: string;
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

export interface CharacterVitalsPayload {
  condition_current: number;
  condition_max: number;
  condition_label?: string;
  stamina_current: number;
  stamina_max: number;
  stamina_label?: string;
}

export interface CreatorChoicePayload {
  value: string;
  label: string;
  description?: string;
}

export interface CreatorStepPayload {
  step_id: string;
  title: string;
  prompt: string;
  input_type: 'text' | 'number' | 'choice' | 'secret';
  choices?: CreatorChoicePayload[];
  back_available: boolean;
  cancel_available: boolean;
}

export interface CreatorStartedPayload {
  username: string;
  step: CreatorStepPayload;
}

export interface CreatorValidationErrorPayload {
  step_id: string;
  field: string;
  message: string;
}

export interface CreatorCancelledPayload {
  username: string;
  reason?: string;
}

export interface CreatorFinishedPayload {
  username: string;
  character_name?: string;
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
  | Envelope<'creator.start', CreatorStartPayload>
  | Envelope<'creator.submit', CreatorSubmitPayload>
  | Envelope<'creator.back', CreatorBackPayload>
  | Envelope<'creator.cancel', CreatorCancelPayload>
  | Envelope<'command.execute', CommandExecutePayload>
  | Envelope<'connection.ping', ConnectionPingPayload>;

export type ServerEnvelope =
  | Envelope<'session.ready', SessionReadyPayload>
  | Envelope<'auth.result', AuthResultPayload>
  | Envelope<'character.vitals', CharacterVitalsPayload>
  | Envelope<'creator.started', CreatorStartedPayload>
  | Envelope<'creator.step', CreatorStepPayload>
  | Envelope<'creator.validation_error', CreatorValidationErrorPayload>
  | Envelope<'creator.cancelled', CreatorCancelledPayload>
  | Envelope<'creator.finished', CreatorFinishedPayload>
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

const CLIENT_MESSAGE_TYPES = new Set<ClientMessageType>([
  'session.hello',
  'auth.login',
  'creator.start',
  'creator.submit',
  'creator.back',
  'creator.cancel',
  'command.execute',
  'connection.ping',
]);
const SERVER_MESSAGE_TYPES = new Set<ServerMessageType>([
  'session.ready',
  'auth.result',
  'character.vitals',
  'creator.started',
  'creator.step',
  'creator.validation_error',
  'creator.cancelled',
  'creator.finished',
  'output.text',
  'output.prompt',
  'room.info',
  'command.result',
  'connection.pong',
  'protocol.error',
]);
const REQUEST_MESSAGE_TYPES = new Set<RequestMessageType>([
  'session.hello',
  'auth.login',
  'creator.start',
  'creator.submit',
  'creator.back',
  'creator.cancel',
  'command.execute',
  'connection.ping',
]);
const STREAM_MESSAGE_TYPES = new Set<StreamMessageType>(['session.ready', 'character.vitals', 'output.text', 'output.prompt', 'room.info']);
const RESPONSE_MESSAGE_TYPES = new Set<ResponseMessageType>([
  'auth.result',
  'creator.started',
  'creator.step',
  'creator.validation_error',
  'creator.cancelled',
  'creator.finished',
  'command.result',
  'connection.pong',
  'protocol.error',
]);

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

function requireInteger(value: unknown, field: string, options?: { min?: number }): number {
  if (!isExactNumber(value)) {
    fail('invalid_payload', `Payload field '${field}' must be an integer.`);
  }
  if (options?.min !== undefined && value < options.min) {
    fail('invalid_payload', `Payload field '${field}' must be at least ${options.min}.`);
  }
  return value;
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

function validateCharacterVitals(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['condition_current', 'condition_max', 'condition_label', 'stamina_current', 'stamina_max', 'stamina_label']);
  requireInteger(payload.condition_current, 'condition_current', { min: 0 });
  requireInteger(payload.condition_max, 'condition_max', { min: 0 });
  requireInteger(payload.stamina_current, 'stamina_current', { min: 0 });
  requireInteger(payload.stamina_max, 'stamina_max', { min: 0 });
  if ('condition_label' in payload) {
    requireString(payload.condition_label, 'condition_label', { allowEmpty: true, maxBytes: MAX_COMMAND_BYTES * 4 });
  }
  if ('stamina_label' in payload) {
    requireString(payload.stamina_label, 'stamina_label', { allowEmpty: true, maxBytes: MAX_COMMAND_BYTES * 4 });
  }
}

function validateCreatorStart(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['username', 'password']);
  requireString(payload.username, 'username', { maxBytes: MAX_COMMAND_BYTES });
  requireString(payload.password, 'password', { maxBytes: MAX_COMMAND_BYTES });
}

function validateCreatorSubmit(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['step_id', 'value']);
  requireString(payload.step_id, 'step_id', { maxBytes: MAX_COMMAND_BYTES });
  requireString(payload.value, 'value', { allowEmpty: true, maxBytes: MAX_COMMAND_BYTES });
}

function validateCreatorStepReference(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['step_id']);
  requireString(payload.step_id, 'step_id', { maxBytes: MAX_COMMAND_BYTES });
}

function validateCreatorChoice(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['value', 'label', 'description']);
  requireString(payload.value, 'value', { maxBytes: MAX_COMMAND_BYTES });
  requireString(payload.label, 'label', { maxBytes: MAX_COMMAND_BYTES });
  if ('description' in payload) {
    requireString(payload.description, 'description', { allowEmpty: true, maxBytes: MAX_COMMAND_BYTES });
  }
}

function validateCreatorStep(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['step_id', 'title', 'prompt', 'input_type', 'choices', 'back_available', 'cancel_available']);
  requireString(payload.step_id, 'step_id', { maxBytes: MAX_COMMAND_BYTES });
  requireString(payload.title, 'title', { maxBytes: MAX_COMMAND_BYTES });
  requireString(payload.prompt, 'prompt', { allowEmpty: true, maxBytes: MAX_COMMAND_BYTES * 8 });
  const inputType = requireString(payload.input_type, 'input_type', { maxBytes: MAX_COMMAND_BYTES });
  if (!['text', 'number', 'choice', 'secret'].includes(inputType)) {
    fail('invalid_payload', "Payload field 'input_type' must be one of: text, number, choice, secret.");
  }
  if ('choices' in payload) {
    if (!Array.isArray(payload.choices)) {
      fail('invalid_payload', "Payload field 'choices' must be an array.");
    }
    for (const choice of payload.choices) {
      if (!isPlainObject(choice)) {
        fail('invalid_payload', "Payload field 'choices' must contain objects.");
      }
      validateCreatorChoice(choice);
    }
  }
  if (typeof payload.back_available !== 'boolean') {
    fail('invalid_payload', "Payload field 'back_available' must be a boolean.");
  }
  if (typeof payload.cancel_available !== 'boolean') {
    fail('invalid_payload', "Payload field 'cancel_available' must be a boolean.");
  }
}

function validateCreatorStarted(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['username', 'step']);
  requireString(payload.username, 'username', { maxBytes: MAX_COMMAND_BYTES });
  if (!isPlainObject(payload.step)) {
    fail('invalid_payload', "Payload field 'step' must be an object.");
  }
  validateCreatorStep(payload.step);
}

function validateCreatorValidationError(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['step_id', 'field', 'message']);
  requireString(payload.step_id, 'step_id', { maxBytes: MAX_COMMAND_BYTES });
  requireString(payload.field, 'field', { maxBytes: MAX_COMMAND_BYTES });
  requireString(payload.message, 'message', { allowEmpty: true, maxBytes: MAX_COMMAND_BYTES * 8 });
}

function validateCreatorCancelled(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['username', 'reason']);
  requireString(payload.username, 'username', { maxBytes: MAX_COMMAND_BYTES });
  if ('reason' in payload) {
    requireString(payload.reason, 'reason', { allowEmpty: true, maxBytes: MAX_COMMAND_BYTES });
  }
}

function validateCreatorFinished(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['username', 'character_name']);
  requireString(payload.username, 'username', { maxBytes: MAX_COMMAND_BYTES });
  if ('character_name' in payload) {
    requireString(payload.character_name, 'character_name', { maxBytes: MAX_COMMAND_BYTES });
  }
}

function validateCommandExecute(payload: Record<string, unknown>): void {
  requireAllowedKeys(payload, ['command']);
  const command = requireString(payload.command, 'command', { maxBytes: MAX_COMMAND_BYTES });
  if (!command.trim()) {
    throw new ProtocolError('invalid_command', 'Command must contain non-whitespace characters.');
  }
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

function validatePayload(type: string, payload: unknown): void {
  if (!isPlainObject(payload)) {
    fail('invalid_payload', 'Protocol payload must be an object.');
  }
  if (type === 'session.hello') return validateSessionHello(payload);
  if (type === 'auth.login') return validateAuthLogin(payload);
  if (type === 'character.vitals') return validateCharacterVitals(payload);
  if (type === 'creator.start') return validateCreatorStart(payload);
  if (type === 'creator.submit') return validateCreatorSubmit(payload);
  if (type === 'creator.back') return validateCreatorStepReference(payload);
  if (type === 'creator.cancel') return validateCreatorStepReference(payload);
  if (type === 'command.execute') return validateCommandExecute(payload);
  if (type === 'connection.ping') return validateConnectionPing(payload);
  if (type === 'session.ready') return validateSessionReady(payload);
  if (type === 'auth.result') return validateAuthResult(payload);
  if (type === 'creator.started') return validateCreatorStarted(payload);
  if (type === 'creator.step') return validateCreatorStep(payload);
  if (type === 'creator.validation_error') return validateCreatorValidationError(payload);
  if (type === 'creator.cancelled') return validateCreatorCancelled(payload);
  if (type === 'creator.finished') return validateCreatorFinished(payload);
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
  validateRequestMetadata(envelope.type, envelope.request_id, envelope.sequence);
  validatePayload(envelope.type, envelope.payload);
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
  const payload = decoded.payload;
  validateRequestMetadata(decoded.type, decoded.request_id, decoded.sequence);
  validatePayload(decoded.type, payload);
  return {
    version: decoded.version,
    type: decoded.type,
    payload,
    ...(decoded.request_id !== undefined ? { request_id: decoded.request_id } : {}),
    ...(decoded.sequence !== undefined ? { sequence: decoded.sequence } : {}),
  } as ProtocolEnvelope;
}
