# Astergard Web Protocol v1

This document defines the versioned JSON contract for the future web client.
It is intentionally independent from React, browser frameworks, and any specific WebSocket library.

## Envelope

Every message is a single JSON object with these top-level fields:

- `version`: exact integer `1`
- `type`: message type string
- `payload`: JSON object
- `request_id`: non-empty string correlation id for request/response messages
- `sequence`: positive integer monotonic sequence for streamed outbound events

Unknown top-level fields are rejected. Unknown protocol versions are rejected. `bool` is not accepted as either `version` or `sequence`.

## Directions

Client to server:

- `session.hello`
- `auth.login`
- `command.execute`
- `connection.ping`

Server to client:

- `session.ready`
- `auth.result`
- `output.text`
- `output.prompt`
- `room.info`
- `command.result`
- `connection.pong`
- `protocol.error`

## Request and sequence rules

- Inbound messages require `request_id`: `session.hello`, `auth.login`, `command.execute`, `connection.ping`
- Streamed outbound events require `sequence`: `session.ready`, `output.text`, `output.prompt`, `room.info`
- Response events require `request_id`: `auth.result`, `command.result`, `connection.pong`, `protocol.error`
- `request_id` and `sequence` may coexist on response events
- `sequence` starts at `1`

## Payloads

Minimal payload shape:

- `session.hello`: optional client metadata such as `client`, `client_version`, `transport`, `capabilities`
- `auth.login`: `username`, `password`
- `command.execute`: `command`
- `connection.ping`: optional `nonce`
- `session.ready`: `transport`, optional `username`
- `auth.result`: `success`, `username`, optional `reason`
- `output.text`: `text`
- `output.prompt`: `prompt`
- `room.info`: authoritative room object compatible with GMCP `Room.Info`
- `command.result`: `command`, `success`
- `connection.pong`: optional `nonce`
- `protocol.error`: `code`, `message`

`command.result` does not repeat `output`. Clients should render `output.text` and `output.prompt` only, which avoids double-printing.

Room payload uses the same authoritative room data that Mudlet receives today through GMCP `Room.Info`.

## Examples

```json
{"version":1,"type":"session.hello","request_id":"1","payload":{"client":"Astergard Web"}}
```

```json
{"version":1,"type":"auth.login","request_id":"2","payload":{"username":"ala","password":"secret"}}
```

```json
{"version":1,"type":"command.result","request_id":"3","sequence":6,"payload":{"command":"spojrz","success":true}}
```

```json
{"version":1,"type":"output.prompt","sequence":7,"payload":{"prompt":"> "}}
```

## Validation and Errors

The transport boundary validates:

- JSON syntax
- UTF-8 decoding
- message size in bytes, not characters
- supported protocol version
- known message type
- exact envelope shape
- payload type for each known message
- command length
- non-finite values are rejected during JSON parsing

Rejected messages become safe `protocol.error` responses or a closed connection.
Errors never include traceback details, server internals, or passwords.

## Limits

- Protocol message size: 8192 bytes
- Command length: 512 UTF-8 bytes

These limits are enforced at the transport boundary before `SessionFlow` executes game logic.

## Compatibility

- TCP/Telnet and Mudlet GMCP remain byte-for-byte compatible with the existing server behavior.
- `SessionFlow` remains the only shared orchestration for login, initial view, and command execution.
- The server remains the source of truth for world state, movement, combat, and prompts.
- Web clients consume the same server-authored state; they do not compute authoritative game logic locally.

## Deployment

Production `WSS` is expected to be terminated by a reverse proxy.
The game server itself stays transport-agnostic and does not manage TLS certificates.

## D59.3 Reservation

Future work will extend this protocol with reconnect tokens, rate limiting, and richer character/inventory/combat payloads.
Those payloads are intentionally not present in runtime for D59.2.
