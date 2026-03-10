"""VIBE schema validation.

Loads the VIBE v2 JSON Schema at startup and validates dicts against it
using jsonschema.
"""

import json
import logging
from pathlib import Path
from typing import Any

import jsonschema

logger = logging.getLogger(__name__)

# Error codes
SCHEMA_VALIDATION_FAILED = "SCHEMA_VALIDATION_FAILED"

# The schema is loaded once at module import time.
_schema: dict[str, Any] | None = None
_schema_load_error: str | None = None


def _find_schema() -> Path:
    """Locate the vibe.schema.json file.

    Searches in order:
    1. VIBE_SCHEMA_PATH environment variable
    2. vibe/schema/vibe.schema.json relative to project root
    3. /app/vibe/schema/vibe.schema.json (Docker mount)
    """
    import os

    env_path = os.environ.get("VIBE_SCHEMA_PATH")
    if env_path:
        p = Path(env_path)
        if p.exists():
            return p

    # Relative to this file: src/validation/schema.py -> mcp-server/ -> vibe/
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    candidates = [
        project_root / "vibe" / "schema" / "vibe.schema.json",
        Path("/app/vibe/schema/vibe.schema.json"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        "Could not locate vibe.schema.json. Set VIBE_SCHEMA_PATH or ensure "
        "the file exists at vibe/schema/vibe.schema.json"
    )


def _load_schema() -> None:
    """Load the JSON schema into the module-level cache."""
    global _schema, _schema_load_error
    try:
        schema_path = _find_schema()
        raw = schema_path.read_text(encoding="utf-8")
        _schema = json.loads(raw)
        logger.info("Loaded VIBE schema from %s", schema_path)
    except Exception as exc:
        _schema_load_error = str(exc)
        logger.warning("Failed to load VIBE schema: %s", exc)


# Load on import
_load_schema()


def get_schema() -> dict[str, Any] | None:
    """Return the loaded schema dict, or None if loading failed."""
    return _schema


def get_schema_load_error() -> str | None:
    """Return the schema load error message, or None if loading succeeded."""
    return _schema_load_error


def validate_document(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a parsed VIBE document against the v2 schema.

    Returns:
        A tuple of (is_valid, errors) where errors is a list of
        human-readable error strings. If the schema was not loaded,
        returns (False, [error_message]).
    """
    if _schema is None:
        return False, [
            f"{SCHEMA_VALIDATION_FAILED}: Schema not loaded"
            + (f" ({_schema_load_error})" if _schema_load_error else "")
        ]

    validator = jsonschema.Draft202012Validator(_schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))

    if not errors:
        return True, []

    messages = []
    for error in errors:
        path = ".".join(str(p) for p in error.absolute_path) or "(root)"
        messages.append(f"{SCHEMA_VALIDATION_FAILED}: {path}: {error.message}")

    return False, messages
