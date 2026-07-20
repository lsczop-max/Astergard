# Astergard WebSocket Gateway

D59.3 exposes a production WebSocket gateway on top of the existing `SessionFlow` and `web_v1` protocol.
It does not introduce a second session orchestrator.

## Dependencies

Install the pinned runtime dependency:

```bash
python -m pip install -r requirements.txt
```

The gateway uses `websockets==12.0`. It is pinned in the repository so builds are reproducible.
`websockets` is a mature async WebSocket library that works with Python 3.12 and does not require adding an HTTP framework.

## Running

TCP remains on its existing port. The WebSocket gateway binds separately:

- host: `127.0.0.1`
- port: `4001`
- required subprotocol: `astergard.v1`

Example development run:

```bash
python3 main.py
```

## Origin policy

The gateway rejects connections without a matching `Origin`.

- in the required-origin mode the handshake must carry exactly one `Origin` header
- production should configure an explicit allowlist
- development may opt into localhost origins
- `*` is not used as a default

## WebSocket framing

Every application message is a JSON envelope in `web_v1`.
The gateway rejects binary frames, oversize frames, invalid JSON, and unsupported protocol versions before any game logic runs.

## Message order

The current D59.3 flow is:

1. `session.hello`
2. `auth.login`
3. `auth.result`
4. initial `output.text`
5. `room.info`
6. `output.prompt`
7. `session.ready`
8. `command.execute`
9. zero or more `output.text` / `room.info`
10. `command.result`
11. `output.prompt`

`connection.ping` is answered with `connection.pong` using the same `request_id`.

## Limits and safety

- message size limit: `WEB_MESSAGE_MAX_BYTES` / `MESSAGE_SIZE_LIMIT`
- command length limit: `COMMAND_LENGTH_LIMIT`
- hello timeout
- login timeout
- WebSocket ping timeout
- WebSocket close timeout
- per-connection rate limiting
- limited protocol error budget before close
- controlled close codes
- no traceback leakage to clients

## Reverse proxy

Production WSS is expected to terminate at a reverse proxy.
The application does not manage certificates.

Example nginx snippet:

```nginx
location /ws/ {
    proxy_pass http://127.0.0.1:4001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "Upgrade";
    proxy_set_header Host $host;
    proxy_set_header Origin $http_origin;
}
```

## Reconnect

Reconnect tokens are not part of D59.3.
WebSocket disconnects use the same cleanup path as TCP and remove the character from `GameServer.clients`.
