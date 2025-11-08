"""Lightweight schema validator for emoji-runtime@1.0 and factory-order@1.0 payloads.

Used by the contract test runner and other offline tooling to detect schema drift.
The validator focuses on structural checks and key field requirements rather than
full JSON Schema compliance so it can run without extra dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


class SchemaValidationError(ValueError):
    """Raised when a payload does not conform to the expected schema."""


_ALLOWED_EMOJI_FIELDS = {
    "schema",
    "glyph_chain",
    "spoken",
    "raw",
    "actor",
    "verb",
    "target",
    "qualifiers",
    "outcomes",
    "summary",
    "intent",
    "telemetry_stub",
    "created_at",
}

_EMOJI_REQUIRED_INTENT = {"actor", "action", "target", "outcome"}
_EMOJI_REQUIRED_TELEMETRY = {
    "batch_id",
    "ritual",
    "units_processed",
    "status",
    "duration_ms",
}

_ALLOWED_FACTORY_FIELDS = {
    "schema",
    "order_id",
    "issued_by",
    "target",
    "priority",
    "timestamp_issued",
    "summary",
    "context",
    "directives",
    "requires_ack",
    "dependencies",
    "attachments",
    "success_criteria",
    "safety_notes",
    "metadata",
}

_FACTORY_REQUIRED_FIELDS = {
    "schema",
    "order_id",
    "issued_by",
    "target",
    "priority",
    "timestamp_issued",
    "summary",
    "directives",
}

_ALLOWED_PRIORITIES = {"low", "normal", "high", "critical"}
_ALLOWED_TELEMETRY_STATUS = {"success", "warning", "failure"}


def _ensure(condition: bool, message: str) -> None:
    if not condition:
        raise SchemaValidationError(message)


def _validate_iso8601(value: str, *, field: str) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:  # pragma: no cover - defensive path
        raise SchemaValidationError(f"{field} must be ISO8601: {value}") from exc


def _validate_list(payload: Mapping[str, Any], field: str, *, element_type: type, allow_empty: bool = False) -> None:
    value = payload.get(field)
    _ensure(isinstance(value, list), f"{field} must be a list")
    if not allow_empty:
        _ensure(bool(value), f"{field} must not be empty")
    for item in value:
        _ensure(isinstance(item, element_type), f"{field} must contain {element_type.__name__}")


def _validate_dict(payload: Mapping[str, Any], field: str, required_keys: Iterable[str]) -> Dict[str, Any]:
    value = payload.get(field)
    _ensure(isinstance(value, dict), f"{field} must be an object")
    missing = [key for key in required_keys if key not in value]
    _ensure(not missing, f"{field} missing keys: {missing}")
    return value


def _validate_emoji_runtime(payload: Mapping[str, Any]) -> None:
    _ensure(payload.get("schema") == "emoji-runtime@1.0", "schema must equal emoji-runtime@1.0")

    unexpected = sorted(set(payload.keys()) - _ALLOWED_EMOJI_FIELDS)
    _ensure(not unexpected, f"unexpected fields present: {unexpected}")
    missing = sorted(_ALLOWED_EMOJI_FIELDS - set(payload.keys()))
    _ensure(not missing, f"missing required fields: {missing}")

    _validate_list(payload, "glyph_chain", element_type=str)
    _validate_list(payload, "spoken", element_type=str)
    _validate_list(payload, "raw", element_type=str)

    glyphs = payload["glyph_chain"]
    _ensure(len(payload["spoken"]) == len(glyphs), "spoken length must match glyph_chain")
    _ensure(len(payload["raw"]) == len(glyphs), "raw length must match glyph_chain")

    _ensure(isinstance(payload.get("actor"), str), "actor must be a string")
    _ensure(isinstance(payload.get("verb"), str), "verb must be a string")
    _ensure(isinstance(payload.get("target"), str), "target must be a string")

    _validate_list(payload, "qualifiers", element_type=str, allow_empty=True)
    _validate_list(payload, "outcomes", element_type=str, allow_empty=False)

    intent = _validate_dict(payload, "intent", _EMOJI_REQUIRED_INTENT)
    for key in _EMOJI_REQUIRED_INTENT:
        value = intent.get(key)
        if key == "outcome":
            _ensure(isinstance(value, str), "intent.outcome must be a string")
        else:
            _ensure(isinstance(value, str), f"intent.{key} must be a string")

    telemetry = _validate_dict(payload, "telemetry_stub", _EMOJI_REQUIRED_TELEMETRY)
    _ensure(telemetry["status"] in _ALLOWED_TELEMETRY_STATUS, "telemetry_stub.status invalid")
    _ensure(isinstance(telemetry["units_processed"], int), "telemetry_stub.units_processed must be int")
    _ensure(telemetry["units_processed"] >= 0, "telemetry_stub.units_processed must be >= 0")
    _ensure(isinstance(telemetry["duration_ms"], int), "telemetry_stub.duration_ms must be int")

    created_at = payload.get("created_at")
    _ensure(isinstance(created_at, str), "created_at must be a string")
    _validate_iso8601(created_at, field="created_at")


def _validate_factory_order(payload: Mapping[str, Any]) -> None:
    _ensure(payload.get("schema") == "factory-order@1.0", "schema must equal factory-order@1.0")

    unexpected = sorted(set(payload.keys()) - _ALLOWED_FACTORY_FIELDS)
    _ensure(not unexpected, f"unexpected fields present: {unexpected}")

    missing = sorted(_FACTORY_REQUIRED_FIELDS - set(payload.keys()))
    _ensure(not missing, f"missing required fields: {missing}")

    _ensure(isinstance(payload["order_id"], str) and payload["order_id"], "order_id must be string")
    _ensure(isinstance(payload["issued_by"], str), "issued_by must be string")
    _ensure(isinstance(payload["target"], str), "target must be string")
    _ensure(payload["priority"] in _ALLOWED_PRIORITIES, "priority invalid")
    _ensure(isinstance(payload.get("summary"), str) and payload["summary"], "summary must be string")

    timestamp = payload["timestamp_issued"]
    _ensure(isinstance(timestamp, str), "timestamp_issued must be string")
    _validate_iso8601(timestamp, field="timestamp_issued")

    directives = payload.get("directives")
    _ensure(isinstance(directives, list) and directives, "directives must be non-empty list")
    seen_steps = set()
    for directive in directives:
        _ensure(isinstance(directive, dict), "directives entries must be objects")
        _ensure({"step", "action", "details"}.issubset(directive), "directive missing required keys")
        step = directive["step"]
        _ensure(isinstance(step, int) and step > 0, "directive.step must be positive int")
        _ensure(step not in seen_steps, "directive.step values must be unique")
        seen_steps.add(step)
        _ensure(isinstance(directive["action"], str) and directive["action"], "directive.action must be string")
        _ensure(isinstance(directive["details"], str) and directive["details"], "directive.details must be string")

    if "dependencies" in payload:
        deps = payload["dependencies"]
        _ensure(isinstance(deps, list), "dependencies must be a list if provided")
        for dep in deps:
            _ensure(isinstance(dep, str), "dependencies entries must be strings")

    if "attachments" in payload:
        attachments = payload["attachments"]
        _ensure(isinstance(attachments, list), "attachments must be a list if provided")
        for item in attachments:
            _ensure(isinstance(item, dict), "attachments entries must be objects")
            _ensure({"type", "path"}.issubset(item), "attachments entries missing keys")


@dataclass
class ValidationResult:
    path: Path
    status: str
    error: str | None = None


def validate_file(path: Path | str) -> str:
    """Validate a JSON payload and return a status string.

    Returns "ok" for recognised schemas, "skip" for unrecognised ones.
    Raises SchemaValidationError for invalid payloads.
    """

    file_path = Path(path)
    data = json.loads(file_path.read_text(encoding="utf-8"))  # type: ignore[name-defined]
    schema = data.get("schema")
    if schema == "emoji-runtime@1.0":
        _validate_emoji_runtime(data)
        return "ok"
    if schema == "factory-order@1.0":
        _validate_factory_order(data)
        return "ok"
    return "skip"


# Minimal JSON import without adding a hard dependency at import time
import json  # noqa: E402  (import placed here to avoid circular imports)


__all__ = ["validate_file", "SchemaValidationError"]
