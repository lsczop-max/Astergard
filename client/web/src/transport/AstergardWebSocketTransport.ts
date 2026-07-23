import {
  MAX_COMMAND_BYTES,
  WEB_PROTOCOL_VERSION,
  parseProtocolEnvelope,
  serializeWebEnvelope,
  type AuthLoginPayload,
  type CreatorBackPayload,
  type CreatorCancelPayload,
  type CreatorStartPayload,
  type CreatorSubmitPayload,
  type ClientEnvelope,
  type CommandExecutePayload,
  type ConnectionPingPayload,
  type ProtocolEnvelope,
  ProtocolError,
  type ServerEnvelope,
  type SessionHelloPayload,
} from '../protocol/webProtocol';
import { utf8ByteLength } from '../protocol/utf8';

export type TransportState = 'disconnected' | 'connecting' | 'handshaking' | 'authenticating' | 'ready' | 'closing' | 'error';

export function connectionStateLabel(state: TransportState): string {
  switch (state) {
    case 'disconnected':
      return 'Rozłączono';
    case 'connecting':
      return 'Łączenie';
    case 'handshaking':
      return 'Uzgadnianie';
    case 'authenticating':
      return 'Logowanie';
    case 'ready':
      return 'Gotowe';
    case 'closing':
      return 'Zamykanie';
    case 'error':
      return 'Błąd';
  }
}

type PendingRequest = 'hello' | 'login' | 'creator' | 'command' | 'ping';

type ClientPayloadMap = {
  'session.hello': SessionHelloPayload;
  'auth.login': AuthLoginPayload;
  'creator.start': CreatorStartPayload;
  'creator.submit': CreatorSubmitPayload;
  'creator.back': CreatorBackPayload;
  'creator.cancel': CreatorCancelPayload;
  'command.execute': CommandExecutePayload;
  'connection.ping': ConnectionPingPayload;
};

type ClientEnvelopeByType<TType extends keyof ClientPayloadMap> = {
  version: typeof WEB_PROTOCOL_VERSION;
  type: TType;
  payload: ClientPayloadMap[TType];
  request_id: string;
};

type Listener = (event: TransportEvent) => void;

export type TransportEvent =
  | { kind: 'state'; state: TransportState }
  | { kind: 'message'; message: ServerEnvelope }
  | { kind: 'error'; message: string; code?: string }
  | { kind: 'closed'; code: number; reason: string }
  | { kind: 'connected' }
  | { kind: 'request'; requestId: string; active: boolean }
  | { kind: 'debug'; message: string };

type WebSocketFactory = (url: string, protocol: string) => WebSocket;

const SUBPROTOCOL = 'astergard.v1';
const CLOSE_NORMAL = 1000;
const CLOSE_PROTOCOL_ERROR = 1008;

const SAFE_CLOSE_MESSAGES: Record<number, string> = {
  1000: 'Połączenie zamknięte.',
  1001: 'Serwer zakończył połączenie.',
  1003: 'Serwer odrzucił dane binarne.',
  1008: 'Serwer zamknął połączenie z powodu naruszenia protokołu.',
  1011: 'Serwer napotkał błąd wewnętrzny.',
};

export function createClientEnvelope<TType extends keyof ClientPayloadMap>(
  type: TType,
  payload: ClientPayloadMap[TType],
  requestId: string,
): ClientEnvelopeByType<TType> {
  if (typeof requestId !== 'string' || requestId === '') {
    throw new Error('request_id must be a non-empty string.');
  }
  const envelope: ClientEnvelopeByType<TType> = {
    version: WEB_PROTOCOL_VERSION,
    type,
    payload,
    request_id: requestId,
  };
  return envelope;
}

function makeRequestIdGenerator(): () => string {
  let counter = 0;
  return () => {
    counter += 1;
    const random = typeof crypto !== 'undefined' && 'getRandomValues' in crypto
      ? Array.from(crypto.getRandomValues(new Uint8Array(6)), (value) => value.toString(16).padStart(2, '0')).join('')
      : Math.random().toString(16).slice(2, 14);
    return `req-${Date.now().toString(36)}-${counter.toString(36)}-${random}`;
  };
}

export class AstergardWebSocketTransport {
  private readonly url: string;
  private readonly factory: WebSocketFactory;
  private readonly listeners = new Set<Listener>();
  private readonly requestId = makeRequestIdGenerator();
  private socket: WebSocket | null = null;
  private state: TransportState = 'disconnected';
  private lastSequence = 0;
  private pending = new Map<string, PendingRequest>();
  private closingByClient = false;
  private disposed = false;

  constructor(url: string, factory: WebSocketFactory = (socketUrl, protocol) => new WebSocket(socketUrl, protocol)) {
    this.url = url;
    this.factory = factory;
  }

  subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    listener({ kind: 'state', state: this.state });
    return () => {
      this.listeners.delete(listener);
    };
  }

  getState(): TransportState {
    return this.state;
  }

  connect(): void {
    if (this.disposed) {
      return;
    }
    this.closingByClient = false;
    this.lastSequence = 0;
    this.detachSocket();
    this.setState('connecting');
    const socket = this.factory(this.url, SUBPROTOCOL);
    this.socket = socket;
    socket.addEventListener('open', this.onOpen);
    socket.addEventListener('message', this.onMessage);
    socket.addEventListener('close', this.onClose);
    socket.addEventListener('error', this.onError);
  }

  dispose(): void {
    this.disposed = true;
    this.closingByClient = true;
    this.detachSocket();
    this.setState('disconnected');
  }

  async submitLogin(username: string, password: string): Promise<void> {
    if (this.state !== 'handshaking' && this.state !== 'authenticating') {
      throw new Error('Najpierw nawiąż połączenie.');
    }
    if (this.pendingHas('login')) {
      throw new Error('Logowanie jest już w toku.');
    }
    const payload = { username, password };
    const envelope = this.buildEnvelope('auth.login', payload, 'login');
    this.send(envelope);
    this.setState('authenticating');
  }

  async startCreator(username: string, password: string): Promise<void> {
    if (this.state !== 'handshaking' && this.state !== 'authenticating') {
      throw new Error('Najpierw nawiąż połączenie.');
    }
    if (this.pendingHas('creator')) {
      throw new Error('Kreator jest już w toku.');
    }
    const payload: CreatorStartPayload = { username, password };
    const envelope = this.buildEnvelope('creator.start', payload, 'creator');
    this.send(envelope);
    this.setState('authenticating');
  }

  async submitCreator(stepId: string, value: string): Promise<void> {
    if (this.state !== 'authenticating' && this.state !== 'handshaking') {
      throw new Error('Kreator jest dostępny dopiero po handshake.');
    }
    if (this.pendingHas('creator')) {
      throw new Error('Kreator jest już w toku.');
    }
    const payload: CreatorSubmitPayload = { step_id: stepId, value };
    const envelope = this.buildEnvelope('creator.submit', payload, 'creator');
    this.send(envelope);
  }

  async goBackInCreator(stepId: string): Promise<void> {
    if (this.state !== 'authenticating' && this.state !== 'handshaking') {
      throw new Error('Kreator jest dostępny dopiero po handshake.');
    }
    if (this.pendingHas('creator')) {
      throw new Error('Kreator jest już w toku.');
    }
    const payload: CreatorBackPayload = { step_id: stepId };
    const envelope = this.buildEnvelope('creator.back', payload, 'creator');
    this.send(envelope);
  }

  async cancelCreator(stepId: string): Promise<void> {
    if (this.state !== 'authenticating' && this.state !== 'handshaking') {
      throw new Error('Kreator jest dostępny dopiero po handshake.');
    }
    if (this.pendingHas('creator')) {
      throw new Error('Kreator jest już w toku.');
    }
    const payload: CreatorCancelPayload = { step_id: stepId };
    const envelope = this.buildEnvelope('creator.cancel', payload, 'creator');
    this.send(envelope);
  }

  async executeCommand(command: string): Promise<void> {
    if (this.state !== 'ready') {
      throw new Error('Komenda może zostać wysłana dopiero po zalogowaniu.');
    }
    if (utf8ByteLength(command) > MAX_COMMAND_BYTES) {
      throw new Error('Komenda przekracza limit 512 znaków.');
    }
    if (this.pendingHas('command')) {
      throw new Error('Poprzednia komenda nadal oczekuje na wynik.');
    }
    const envelope = this.buildEnvelope('command.execute', { command }, 'command');
    this.send(envelope);
  }

  canExecuteCommand(): boolean {
    return this.state === 'ready' && !this.pendingHas('command');
  }

  async ping(nonce?: string): Promise<void> {
    if (this.state === 'disconnected' || this.state === 'connecting') {
      throw new Error('Ping jest dostępny po handshake.');
    }
    if (this.pendingHas('ping')) {
      throw new Error('Ping jest już w toku.');
    }
    const payload = nonce === undefined ? {} : { nonce };
    const envelope = this.buildEnvelope('connection.ping', payload, 'ping');
    this.send(envelope);
  }

  close(): void {
    if (this.socket === null) {
      this.setState('disconnected');
      return;
    }
    this.closingByClient = true;
    this.setState('closing');
    this.socket.close(CLOSE_NORMAL, 'client closing');
  }

  private send(envelope: ClientEnvelope): void {
    if (!this.socket || this.socket.readyState !== 1) {
      throw new Error('Połączenie WebSocket nie jest otwarte.');
    }
    try {
      this.socket.send(serializeWebEnvelope(envelope));
    } catch (error) {
      if (envelope.request_id) {
        this.pending.delete(envelope.request_id);
        this.emit({ kind: 'request', requestId: envelope.request_id, active: false });
      }
      throw error;
    }
  }

  private buildEnvelope<T extends keyof ClientPayloadMap>(type: T, payload: ClientPayloadMap[T], requestKind: PendingRequest): ClientEnvelopeByType<T> {
    const requestId = this.requestId();
    const envelope = createClientEnvelope(type, payload, requestId);
    this.pending.set(requestId, requestKind);
    this.emit({ kind: 'request', requestId, active: true });
    return envelope;
  }

  private pendingHas(kind: PendingRequest): boolean {
    for (const value of this.pending.values()) {
      if (value === kind) {
        return true;
      }
    }
    return false;
  }

  private emit(event: TransportEvent): void {
    for (const listener of this.listeners) {
      listener(event);
    }
  }

  private setState(state: TransportState): void {
    this.state = state;
    this.emit({ kind: 'state', state });
  }

  private detachSocket(): void {
    if (!this.socket) {
      return;
    }
    this.socket.removeEventListener('open', this.onOpen);
    this.socket.removeEventListener('message', this.onMessage);
    this.socket.removeEventListener('close', this.onClose);
    this.socket.removeEventListener('error', this.onError);
    try {
      if (this.socket.readyState === 1 || this.socket.readyState === 0) {
        this.socket.close(CLOSE_NORMAL, 'reconnect');
      }
    } catch {
      // ignore
    }
    this.socket = null;
    this.pending.clear();
  }

  private onOpen = (): void => {
    this.emit({ kind: 'connected' });
    this.setState('handshaking');
    const hello = this.buildEnvelope('session.hello', {
      client: 'Astergard Web',
      client_version: 'D59.4',
      transport: 'websocket',
    }, 'hello');
    this.send(hello);
  };

  private onMessage = async (event: MessageEvent): Promise<void> => {
    if (typeof event.data !== 'string' && !(event.data instanceof ArrayBuffer) && !(event.data instanceof Uint8Array)) {
      this.failProtocol('invalid_binary', 'Binary websocket messages are not supported.');
      return;
    }
    try {
      const envelope = parseProtocolEnvelope(event.data);
      if (envelope.sequence !== undefined) {
        this.ensureSequence(envelope.sequence);
      }
      this.handleEnvelope(envelope);
    } catch (error) {
      if (error instanceof ProtocolError) {
        const code = error.code;
        const message = error.message || 'Błąd protokołu.';
        this.failProtocol(code, message);
      } else if (error instanceof Error) {
        this.failProtocol('protocol_error', error.message || 'Błąd protokołu.');
      } else {
        this.failProtocol('protocol_error', 'Błąd protokołu.');
      }
    }
  };

  private onClose = (event: CloseEvent): void => {
    this.detachListenersOnly();
    this.socket = null;
    this.pending.clear();
    if (this.closingByClient || event.code === CLOSE_NORMAL) {
      this.setState('disconnected');
      this.emit({ kind: 'closed', code: event.code, reason: event.reason });
      this.closingByClient = false;
      return;
    }
    this.setState('error');
    this.emit({
      kind: 'error',
      code: String(event.code),
      message: SAFE_CLOSE_MESSAGES[event.code] ?? 'Połączenie zostało przerwane.',
    });
    this.emit({ kind: 'closed', code: event.code, reason: event.reason });
  };

  private onError = (): void => {
    this.setState('error');
    this.emit({ kind: 'error', message: 'Wystąpił błąd połączenia WebSocket.' });
  };

  private detachListenersOnly(): void {
    if (!this.socket) {
      return;
    }
    this.socket.removeEventListener('open', this.onOpen);
    this.socket.removeEventListener('message', this.onMessage);
    this.socket.removeEventListener('close', this.onClose);
    this.socket.removeEventListener('error', this.onError);
  }

  private ensureSequence(sequence: number): void {
    if (sequence <= this.lastSequence) {
      this.failProtocol('sequence_regression', 'Odebrano zdublowaną lub cofniętą sekwencję wiadomości.');
      return;
    }
    if (sequence !== this.lastSequence + 1) {
      this.failProtocol('sequence_gap', 'Odebrano lukę w sekwencji wiadomości.');
      return;
    }
    this.lastSequence = sequence;
  }

  private handleEnvelope(envelope: ProtocolEnvelope): void {
    if (envelope.request_id && !this.pending.has(envelope.request_id) && envelope.type !== 'protocol.error') {
      this.failProtocol('unexpected_request_id', 'Odebrano odpowiedź dla nieznanego żądania.');
      return;
    }
    if (envelope.request_id) {
      this.pending.delete(envelope.request_id);
      this.emit({ kind: 'request', requestId: envelope.request_id, active: false });
    }
    if (envelope.type === 'protocol.error') {
      this.setState('error');
      this.emit({ kind: 'error', code: envelope.payload.code, message: `Błąd protokołu: ${envelope.payload.message}` });
      this.emit({ kind: 'message', message: envelope });
      return;
    }
    if (envelope.type === 'auth.result') {
      if (!envelope.payload.success) {
        this.setState('handshaking');
        this.emit({
          kind: 'error',
          code: envelope.payload.reason ?? 'auth_failed',
          message: `Logowanie nie powiodło się: ${envelope.payload.reason ?? 'odmowa serwera'}.`,
        });
      }
    }
    if (envelope.type === 'creator.started') {
      this.setState('authenticating');
    }
    if (envelope.type === 'creator.step') {
      this.setState('authenticating');
    }
    if (envelope.type === 'creator.validation_error') {
      this.setState('authenticating');
      this.emit({
        kind: 'error',
        code: envelope.payload.field,
        message: `Błąd kreatora: ${envelope.payload.message}`,
      });
    }
    if (envelope.type === 'creator.cancelled') {
      this.setState('handshaking');
    }
    if (envelope.type === 'creator.finished') {
      this.setState('authenticating');
    }
    if (envelope.type === 'session.ready') {
      this.setState('ready');
    }
    if (
      envelope.type === 'output.text' ||
      envelope.type === 'output.prompt' ||
      envelope.type === 'room.info' ||
      envelope.type === 'character.vitals' ||
      envelope.type === 'command.result' ||
      envelope.type === 'connection.pong' ||
      envelope.type === 'session.ready' ||
      envelope.type === 'auth.result' ||
      envelope.type === 'creator.started' ||
      envelope.type === 'creator.step' ||
      envelope.type === 'creator.validation_error' ||
      envelope.type === 'creator.cancelled' ||
      envelope.type === 'creator.finished'
    ) {
      this.emit({ kind: 'message', message: envelope });
    }
  }

  private failProtocol(code: string, message: string): void {
    this.setState('error');
    this.emit({ kind: 'error', code, message });
    if (this.socket && this.socket.readyState === 1) {
      try {
        this.socket.close(CLOSE_PROTOCOL_ERROR, 'protocol violation');
      } catch {
        // ignore
      }
    }
  }
}
