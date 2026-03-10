"""MCP tool registrations for plan read/write operations.

Registers 2 tools: write_plan, read_plan.
write_plan validates .vibe.md structure and schema (advisory -- still writes on failure).
read_plan reads, parses .vibe.md, validates schema, returns content + parsed + valid.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from ..parsing.vibe_md import parse_vibe_md
from ..session.manager import SessionManager
from ..validation.schema import validate_document

logger = logging.getLogger(__name__)

# Error codes
INVALID_VIBE_MD = "INVALID_VIBE_MD"
FILE_NOT_FOUND = "FILE_NOT_FOUND"
FILESYSTEM_ERROR = "FILESYSTEM_ERROR"

_manager = SessionManager()


def _safe_write_file(path: Path, content: str) -> None:
    """Write content to a file atomically via a .tmp intermediate."""
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp_path.write_text(content, encoding="utf-8")
        tmp_path.replace(path)
    except OSError as exc:
        tmp_path.unlink(missing_ok=True)
        raise RuntimeError(f"{FILESYSTEM_ERROR}: {exc}") from exc


def register_plan_tools(mcp: FastMCP) -> None:
    """Register plan read/write tools with the MCP server."""

    @mcp.tool()
    async def write_plan(
        session_id: str,
        filename: str,
        content: str,
    ) -> str:
        """Write a .vibe.md plan file to a session directory.

        Validates .vibe.md structure and schema compliance (advisory). The file
        is written regardless of validation outcome, but validation results are
        returned so the caller can address issues.

        Args:
            session_id: The session ID to write the plan into.
            filename: Name of the .vibe.md file (e.g. 'architecture.vibe.md').
            content: The full .vibe.md content (YAML frontmatter + markdown body).

        Returns:
            JSON object with write status, parse_valid, schema_valid, and any errors.
        """
        result: dict = {
            "session_id": session_id,
            "filename": filename,
            "written": False,
            "parse_valid": False,
            "schema_valid": False,
            "parse_errors": [],
            "schema_errors": [],
        }

        # Parse .vibe.md
        parsed = None
        try:
            parsed = parse_vibe_md(content)
            if isinstance(parsed, dict) and "vibe" in parsed:
                result["parse_valid"] = True
            else:
                result["parse_errors"].append(
                    f"{INVALID_VIBE_MD}: Parsed content is missing required 'vibe' field"
                )
        except Exception as exc:
            result["parse_errors"].append(f"{INVALID_VIBE_MD}: {exc}")

        # Validate schema if parsed successfully
        if isinstance(parsed, dict) and "vibe" in parsed:
            is_valid, schema_errors = validate_document(parsed)
            result["schema_valid"] = is_valid
            result["schema_errors"] = schema_errors

        # Write the file regardless of validation outcome (advisory validation)
        try:
            session_dir = _manager.get_session_dir(session_id)
            file_path = session_dir / filename
            _safe_write_file(file_path, content)
            result["written"] = True

            # Update session metadata
            _manager.update_session_plans(session_id, filename)
        except RuntimeError as exc:
            result["write_error"] = str(exc)

        return json.dumps(result, indent=2)

    @mcp.tool()
    async def read_plan(
        session_id: str,
        filename: str,
    ) -> str:
        """Read a .vibe.md plan file from a session directory.

        Reads the raw content, parses the .vibe.md format, validates against
        the VIBE v1 schema, and returns all three results.

        Args:
            session_id: The session ID containing the plan.
            filename: Name of the .vibe.md file to read.

        Returns:
            JSON object with content (raw text), parsed (dict as JSON), and
            validation results (parse_valid, schema_valid, errors).
        """
        result: dict = {
            "session_id": session_id,
            "filename": filename,
            "content": None,
            "parsed": None,
            "parse_valid": False,
            "schema_valid": False,
            "parse_errors": [],
            "schema_errors": [],
        }

        # Locate and read the file
        try:
            session_dir = _manager.get_session_dir(session_id)
        except RuntimeError as exc:
            result["error"] = str(exc)
            return json.dumps(result, indent=2)

        file_path = session_dir / filename
        if not file_path.exists():
            result["error"] = f"{FILE_NOT_FOUND}: {filename} in session {session_id}"
            return json.dumps(result, indent=2)

        try:
            raw_content = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            result["error"] = f"{FILESYSTEM_ERROR}: {exc}"
            return json.dumps(result, indent=2)

        result["content"] = raw_content

        # Parse .vibe.md
        parsed = None
        try:
            parsed = parse_vibe_md(raw_content)
            if isinstance(parsed, dict) and "vibe" in parsed:
                result["parse_valid"] = True
                result["parsed"] = parsed
            else:
                result["parse_errors"].append(
                    f"{INVALID_VIBE_MD}: Parsed content is missing required 'vibe' field"
                )
        except Exception as exc:
            result["parse_errors"].append(f"{INVALID_VIBE_MD}: {exc}")

        # Validate schema
        if isinstance(parsed, dict) and "vibe" in parsed:
            is_valid, schema_errors = validate_document(parsed)
            result["schema_valid"] = is_valid
            result["schema_errors"] = schema_errors

        return json.dumps(result, indent=2)
