from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal

WEB_PROTOCOL_VERSION = 1

ClientMessageType = Literal["session.hello", "auth.login", "command.execute", "connection.ping"]
ServerMessageType = Literal[
    "session.ready",
    "auth.result",
    "output.text",
    "output.prompt",
    "room.info",
    "command.result",
    "connection.pong",
    "protocol.error",
]

CLIENT_MESSAGE_TYPES = {"session.hello", "auth.login", "command.execute", "connection.ping"}
SERVER_MESSAGE_TYPES = {
    "session.ready",
    "auth.result",
    "output.text",
    "output.prompt",
    "room.info",
    "command.result",
    "connection.pong",
    "protocol.error",
}
REQUEST_MESSAGE_TYPES = {"session.hello", "auth.login", "command.execute", "connection.ping"}
STREAM_MESSAGE_TYPES = {"session.ready", "output.text", "output.prompt", "room.info"}
RESPONSE_MESSAGE_TYPES = {"auth.result", "command.result", "connection.pong", "protocol.error"}

MESSAGE_SIZE_LIMIT = 8192
WEB_MESSAGE_MAX_BYTES = MESSAGE_SIZE_LIMIT
COMMAND_LENGTH_LIMIT = 512


class WebProtocolError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message

    def __repr__(self) -> str:
        return f"WebProtocolError(code={self.code!r}, message={self.message!r})"

    def __str__(self) -> str:
        return self.message


@dataclass(frozen=True, slots=True)
class WebProtocolEnvelope:
    version: int
    type: str
    payload: dict[str, Any]
    request_id: str | None = None
    sequence: int | None = None

    def __repr__(self) -> str:
        return (
            "WebProtocolEnvelope("
            f"version={self.version!r}, type={self.type!r}, "
            f"payload_keys={sorted(self.payload.keys())!r}, "
            f"request_id={self.request_id!r}, sequence={self.sequence!r})"
        )


def build_web_envelope(
    message_type: str,
    payload: dict[str, Any],
    *,
    request_id: str | None = None,
    sequence: int | None = None,
) -> WebProtocolEnvelope:
    if request_id is not None and (not isinstance(request_id, str) or request_id == ""):
        raise WebProtocolError("invalid_request_id", "request_id must be a non-empty string.")
    if sequence is not None and (type(sequence) is not int or sequence < 1):
        raise WebProtocolError("invalid_sequence", "sequence must be a positive integer.")
    return WebProtocolEnvelope(
        version=WEB_PROTOCOL_VERSION,
        type=message_type,
        payload=dict(payload),
        request_id=request_id,
        sequence=sequence,
    )


def serialize_web_envelope(envelope: WebProtocolEnvelope) -> str:
    data: dict[str, Any] = {
        "version": envelope.version,
        "type": envelope.type,
        "payload": envelope.payload,
    }
    if envelope.request_id is not None:
        data["request_id"] = envelope.request_id
    if envelope.sequence is not None:
        data["sequence"] = envelope.sequence
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _reject_non_finite(value: str) -> None:
    raise WebProtocolError("invalid_json", "Protocol message contains non-finite numbers.")


def _ensure_known_message_type(message_type: str) -> None:
    if message_type not in CLIENT_MESSAGE_TYPES and message_type not in SERVER_MESSAGE_TYPES:
        raise WebProtocolError("unknown_type", "Unknown protocol message type.")


def _ensure_exact_int(value: Any, field: str, *, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise WebProtocolError("invalid_payload", f"Payload field {field!r} must be an integer.")
    if minimum is not None and value < minimum:
        raise WebProtocolError("invalid_payload", f"Payload field {field!r} must be at least {minimum}.")
    return value


def _require_string_field(payload: dict[str, Any], key: str, *, max_length: int | None = None, allow_empty: bool = False) -> str:
    value = payload.get(key)
    if type(value) is not str:
        raise WebProtocolError("invalid_payload", f"Payload field {key!r} must be a string.")
    if not allow_empty and value == "":
        raise WebProtocolError("invalid_payload", f"Payload field {key!r} must be a non-empty string.")
    if max_length is not None and len(value.encode("utf-8")) > max_length:
        raise WebProtocolError("message_too_large", f"Payload field {key!r} exceeds the limit.")
    return value


def _require_allowed_keys(payload: dict[str, Any], allowed: set[str]) -> None:
    unexpected = set(payload) - allowed
    if unexpected:
        raise WebProtocolError("invalid_payload", "Protocol payload contains unknown fields.")


def _validate_session_hello(payload: dict[str, Any]) -> None:
    allowed = {"client", "client_version", "capabilities", "transport"}
    _require_allowed_keys(payload, allowed)
    if "client" in payload:
        _require_string_field(payload, "client", max_length=COMMAND_LENGTH_LIMIT)
    if "client_version" in payload:
        _require_string_field(payload, "client_version", max_length=COMMAND_LENGTH_LIMIT)
    if "transport" in payload:
        _require_string_field(payload, "transport", max_length=COMMAND_LENGTH_LIMIT)
    if "capabilities" in payload:
        capabilities = payload["capabilities"]
        if type(capabilities) is not list:
            raise WebProtocolError("invalid_payload", "Payload field 'capabilities' must be an array.")
        for capability in capabilities:
            if type(capability) is not str or capability == "":
                raise WebProtocolError("invalid_payload", "Payload field 'capabilities' must contain strings.")


def _validate_auth_login(payload: dict[str, Any]) -> None:
    _require_allowed_keys(payload, {"username", "password"})
    _require_string_field(payload, "username", max_length=COMMAND_LENGTH_LIMIT)
    _require_string_field(payload, "password", max_length=COMMAND_LENGTH_LIMIT)


def _validate_command_execute(payload: dict[str, Any]) -> None:
    _require_allowed_keys(payload, {"command"})
    _require_string_field(payload, "command", max_length=COMMAND_LENGTH_LIMIT)


def _validate_connection_ping(payload: dict[str, Any]) -> None:
    _require_allowed_keys(payload, {"nonce"})
    if "nonce" in payload:
        _require_string_field(payload, "nonce", max_length=COMMAND_LENGTH_LIMIT, allow_empty=True)


def _validate_session_ready(payload: dict[str, Any]) -> None:
    _require_allowed_keys(payload, {"transport", "username"})
    _require_string_field(payload, "transport", max_length=COMMAND_LENGTH_LIMIT)
    if "username" in payload:
        _require_string_field(payload, "username", max_length=COMMAND_LENGTH_LIMIT)


def _validate_auth_result(payload: dict[str, Any]) -> None:
    _require_allowed_keys(payload, {"success", "username", "reason"})
    if type(payload.get("success")) is not bool:
        raise WebProtocolError("invalid_payload", "Payload field 'success' must be a boolean.")
    _require_string_field(payload, "username", max_length=COMMAND_LENGTH_LIMIT)
    if "reason" in payload:
        _require_string_field(payload, "reason", max_length=COMMAND_LENGTH_LIMIT, allow_empty=True)


def _validate_output_text(payload: dict[str, Any], field: str) -> None:
    _require_allowed_keys(payload, {field})
    _require_string_field(payload, field, allow_empty=True)


def _validate_room_info(payload: dict[str, Any]) -> None:
    allowed = {"num", "name", "area", "coords", "exits", "area_label", "terrain", "special_exits"}
    _require_allowed_keys(payload, allowed)
    _ensure_exact_int(payload.get("num"), "num", minimum=0)
    _require_string_field(payload, "name", max_length=COMMAND_LENGTH_LIMIT)
    _require_string_field(payload, "area", max_length=COMMAND_LENGTH_LIMIT)
    coords = payload.get("coords")
    if type(coords) is not dict:
        raise WebProtocolError("invalid_payload", "Payload field 'coords' must be an object.")
    for axis in ("x", "y", "z"):
        _ensure_exact_int(coords.get(axis), f"coords.{axis}")
    exits = payload.get("exits")
    if type(exits) is not dict:
        raise WebProtocolError("invalid_payload", "Payload field 'exits' must be an object.")
    for direction, target in exits.items():
        if type(direction) is not str or direction == "":
            raise WebProtocolError("invalid_payload", "Payload field 'exits' must use string keys.")
        _ensure_exact_int(target, f"exits.{direction}", minimum=0)
    if "area_label" in payload:
        _require_string_field(payload, "area_label", max_length=COMMAND_LENGTH_LIMIT)
    if "terrain" in payload:
        _require_string_field(payload, "terrain", max_length=COMMAND_LENGTH_LIMIT)
    if "special_exits" in payload:
        special_exits = payload["special_exits"]
        if type(special_exits) is not list:
            raise WebProtocolError("invalid_payload", "Payload field 'special_exits' must be an array.")


def _validate_command_result(payload: dict[str, Any]) -> None:
    _require_allowed_keys(payload, {"command", "success"})
    _require_string_field(payload, "command", max_length=COMMAND_LENGTH_LIMIT)
    if type(payload.get("success")) is not bool:
        raise WebProtocolError("invalid_payload", "Payload field 'success' must be a boolean.")


def _validate_connection_pong(payload: dict[str, Any]) -> None:
    _require_allowed_keys(payload, {"nonce"})
    if "nonce" in payload:
        _require_string_field(payload, "nonce", max_length=COMMAND_LENGTH_LIMIT, allow_empty=True)


def _validate_protocol_error(payload: dict[str, Any]) -> None:
    _require_allowed_keys(payload, {"code", "message"})
    _require_string_field(payload, "code", max_length=COMMAND_LENGTH_LIMIT)
    _require_string_field(payload, "message", max_length=COMMAND_LENGTH_LIMIT, allow_empty=True)


def _validate_payload_shape(message_type: str, payload: dict[str, Any]) -> None:
    if message_type == "session.hello":
        _validate_session_hello(payload)
        return
    if message_type == "auth.login":
        _validate_auth_login(payload)
        return
    if message_type == "command.execute":
        _validate_command_execute(payload)
        return
    if message_type == "connection.ping":
        _validate_connection_ping(payload)
        return
    if message_type == "session.ready":
        _validate_session_ready(payload)
        return
    if message_type == "auth.result":
        _validate_auth_result(payload)
        return
    if message_type == "output.text":
        _validate_output_text(payload, "text")
        return
    if message_type == "output.prompt":
        _validate_output_text(payload, "prompt")
        return
    if message_type == "room.info":
        _validate_room_info(payload)
        return
    if message_type == "command.result":
        _validate_command_result(payload)
        return
    if message_type == "connection.pong":
        _validate_connection_pong(payload)
        return
    if message_type == "protocol.error":
        _validate_protocol_error(payload)
        return


def _ensure_request_metadata(message_type: str, request_id: Any, sequence: Any) -> None:
    if message_type in REQUEST_MESSAGE_TYPES:
        if type(request_id) is not str or request_id == "":
            raise WebProtocolError("invalid_request_id", "Request messages require a non-empty string request_id.")
        if sequence is not None:
            raise WebProtocolError("invalid_envelope", "Request messages must not include sequence.")
        return
    if message_type in STREAM_MESSAGE_TYPES:
        if type(sequence) is not int or sequence < 1:
            raise WebProtocolError("invalid_sequence", "Stream messages require a positive integer sequence.")
        if request_id is not None:
            raise WebProtocolError("invalid_envelope", "Stream messages must not include request_id.")
        return
    if message_type in {"auth.result", "command.result"}:
        if type(request_id) is not str or request_id == "":
            raise WebProtocolError("invalid_request_id", "Response messages require a non-empty string request_id.")
        if sequence is not None and (type(sequence) is not int or sequence < 1):
            raise WebProtocolError("invalid_sequence", "sequence must be a positive integer.")
        return
    if message_type == "connection.pong":
        if type(request_id) is not str or request_id == "":
            raise WebProtocolError("invalid_request_id", "Response messages require a non-empty string request_id.")
        if sequence is not None and (type(sequence) is not int or sequence < 1):
            raise WebProtocolError("invalid_sequence", "sequence must be a positive integer.")
        return
    if message_type == "protocol.error":
        if request_id is not None and (type(request_id) is not str or request_id == ""):
            raise WebProtocolError("invalid_request_id", "request_id must be a non-empty string.")
        if sequence is not None and (type(sequence) is not int or sequence < 1):
            raise WebProtocolError("invalid_sequence", "sequence must be a positive integer.")


def parse_web_envelope(raw: str | bytes, *, max_bytes: int = MESSAGE_SIZE_LIMIT) -> WebProtocolEnvelope:
    raw_bytes = raw.encode("utf-8") if isinstance(raw, str) else bytes(raw)
    if len(raw_bytes) > max_bytes:
        raise WebProtocolError("message_too_large", "Protocol message exceeds size limit.")
    try:
        decoded = json.loads(
            raw_bytes.decode("utf-8"),
            parse_constant=_reject_non_finite,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WebProtocolError("invalid_json", "Protocol message is not valid JSON.") from exc
    if not isinstance(decoded, dict):
        raise WebProtocolError("invalid_envelope", "Protocol envelope must be an object.")
    allowed_keys = {"version", "type", "payload", "request_id", "sequence"}
    if set(decoded) - allowed_keys:
        raise WebProtocolError("invalid_envelope", "Protocol envelope contains unknown fields.")
    version = decoded.get("version")
    if type(version) is not int or version != WEB_PROTOCOL_VERSION:
        raise WebProtocolError("unsupported_version", "Unsupported protocol version.")
    message_type = decoded.get("type")
    if type(message_type) is not str:
        raise WebProtocolError("invalid_type", "Protocol message type must be a string.")
    _ensure_known_message_type(message_type)
    payload = decoded.get("payload")
    if not isinstance(payload, dict):
        raise WebProtocolError("invalid_payload", "Protocol payload must be an object.")
    request_id = decoded.get("request_id")
    sequence = decoded.get("sequence")
    if request_id is not None and (type(request_id) is not str or request_id == ""):
        raise WebProtocolError("invalid_request_id", "request_id must be a non-empty string.")
    if sequence is not None and (type(sequence) is not int or sequence < 1):
        raise WebProtocolError("invalid_sequence", "sequence must be a positive integer.")
    _ensure_request_metadata(message_type, request_id, sequence)
    _validate_payload_shape(message_type, payload)
    return WebProtocolEnvelope(
        version=version,
        type=message_type,
        payload=payload,
        request_id=request_id,
        sequence=sequence,
    )
