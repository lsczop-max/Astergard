type MockWebSocketEvent = {
  type: string;
  target: MockWebSocket;
  currentTarget: MockWebSocket;
  data?: string | ArrayBuffer | Uint8Array;
  code?: number;
  reason?: string;
};

type Listener = (event: MockWebSocketEvent) => void;

export class MockWebSocket {
  static OPEN = 1;
  static CONNECTING = 0;
  static CLOSED = 3;
  static instances: MockWebSocket[] = [];

  readyState = MockWebSocket.CONNECTING;
  sent: string[] = [];
  listeners = new Map<string, Set<Listener>>();
  closeCalls: Array<{ code?: number; reason?: string }> = [];

  constructor(
    public readonly url: string,
    public readonly protocol: string,
  ) {
    MockWebSocket.instances.push(this);
  }

  addEventListener(type: string, listener: Listener) {
    const set = this.listeners.get(type) ?? new Set<Listener>();
    set.add(listener);
    this.listeners.set(type, set);
  }

  removeEventListener(type: string, listener: Listener) {
    this.listeners.get(type)?.delete(listener);
  }

  send(message: string) {
    this.sent.push(message);
  }

  close(code?: number, reason?: string) {
    this.closeCalls.push({ code, reason });
    this.readyState = MockWebSocket.CLOSED;
    this.dispatch('close', { code: code ?? 1000, reason: reason ?? '' });
  }

  open() {
    this.readyState = MockWebSocket.OPEN;
    this.dispatch('open', {});
  }

  message(data: string | ArrayBuffer | Uint8Array) {
    this.dispatch('message', { data });
  }

  error() {
    this.dispatch('error', {});
  }

  dispatch(type: string, event: Omit<MockWebSocketEvent, 'type' | 'target' | 'currentTarget'> = {}) {
    for (const listener of this.listeners.get(type) ?? []) {
      listener({ type, target: this, currentTarget: this, ...event });
    }
  }
}
