"""Session management for VIBE MCP server.

Handles creation, listing, retrieval, and archival of planning sessions.
Each session is a directory under data/sessions/{id}/ containing a session.json
metadata file and zero or more .vibe.md plan files.
"""

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .id_gen import generate_session_id

# Error codes
SESSION_NOT_FOUND = "SESSION_NOT_FOUND"
FILESYSTEM_ERROR = "FILESYSTEM_ERROR"


def _base_dir() -> Path:
    """Return the base data directory, resolved relative to the project root."""
    return Path(os.environ.get("VIBE_DATA_DIR", "data"))


def _sessions_dir() -> Path:
    return _base_dir() / "sessions"


def _archive_dir() -> Path:
    return _base_dir() / "archive"


def _safe_write(path: Path, data: str) -> None:
    """Write data to a file atomically via a .tmp intermediate."""
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp_path.write_text(data, encoding="utf-8")
        tmp_path.replace(path)
    except OSError as exc:
        # Clean up the temp file on failure
        tmp_path.unlink(missing_ok=True)
        raise RuntimeError(f"{FILESYSTEM_ERROR}: {exc}") from exc


class SessionManager:
    """Manages VIBE planning sessions on disk."""

    def create_session(
        self,
        name: str,
        description: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new session directory and metadata file.

        Returns the session metadata dict including the generated session_id.
        """
        session_id = generate_session_id()
        session_dir = _sessions_dir() / session_id

        try:
            session_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            # Extremely unlikely collision; re-generate once
            session_id = generate_session_id()
            session_dir = _sessions_dir() / session_id
            session_dir.mkdir(parents=True, exist_ok=False)
        except OSError as exc:
            raise RuntimeError(f"{FILESYSTEM_ERROR}: {exc}") from exc

        now = datetime.now(timezone.utc).isoformat()
        metadata: dict[str, Any] = {
            "session_id": session_id,
            "name": name,
            "description": description or "",
            "tags": tags or [],
            "status": "active",
            "created_at": now,
            "updated_at": now,
            "plans": [],
        }

        _safe_write(
            session_dir / "session.json",
            json.dumps(metadata, indent=2),
        )
        return metadata

    def list_sessions(
        self,
        tag: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """List all sessions, optionally filtered by tag and/or status."""
        sessions_dir = _sessions_dir()
        if not sessions_dir.exists():
            return []

        results: list[dict[str, Any]] = []
        for entry in sorted(sessions_dir.iterdir()):
            if not entry.is_dir():
                continue
            meta_path = entry / "session.json"
            if not meta_path.exists():
                continue
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue

            if tag and tag not in meta.get("tags", []):
                continue
            if status and meta.get("status") != status:
                continue

            results.append(meta)
        return results

    def get_session(self, session_id: str) -> dict[str, Any]:
        """Retrieve session metadata and list of .vibe.md plan files.

        Raises RuntimeError with SESSION_NOT_FOUND if the session does not exist.
        """
        session_dir = _sessions_dir() / session_id
        meta_path = session_dir / "session.json"

        if not meta_path.exists():
            raise RuntimeError(f"{SESSION_NOT_FOUND}: {session_id}")

        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise RuntimeError(f"{FILESYSTEM_ERROR}: {exc}") from exc

        # Discover .vibe.md files in the session directory
        vibe_files = sorted(
            str(p.name) for p in session_dir.glob("*.vibe.md")
        )
        meta["vibe_files"] = vibe_files
        return meta

    def archive_session(self, session_id: str) -> dict[str, Any]:
        """Move a session to the archive directory.

        Returns the updated session metadata with status set to 'archived'.
        Raises RuntimeError with SESSION_NOT_FOUND if the session does not exist.
        """
        session_dir = _sessions_dir() / session_id
        if not session_dir.exists():
            raise RuntimeError(f"{SESSION_NOT_FOUND}: {session_id}")

        # Update status in metadata before moving
        meta_path = session_dir / "session.json"
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise RuntimeError(f"{FILESYSTEM_ERROR}: {exc}") from exc

        meta["status"] = "archived"
        meta["updated_at"] = datetime.now(timezone.utc).isoformat()
        _safe_write(meta_path, json.dumps(meta, indent=2))

        # Move to archive
        archive_dir = _archive_dir()
        archive_dir.mkdir(parents=True, exist_ok=True)
        dest = archive_dir / session_id

        try:
            shutil.move(str(session_dir), str(dest))
        except OSError as exc:
            raise RuntimeError(f"{FILESYSTEM_ERROR}: {exc}") from exc

        return meta

    def update_session_plans(
        self, session_id: str, plan_filename: str
    ) -> None:
        """Add a plan filename to the session's plan list if not already present."""
        session_dir = _sessions_dir() / session_id
        meta_path = session_dir / "session.json"

        if not meta_path.exists():
            raise RuntimeError(f"{SESSION_NOT_FOUND}: {session_id}")

        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            raise RuntimeError(f"{FILESYSTEM_ERROR}: {exc}") from exc

        plans = meta.get("plans", [])
        if plan_filename not in plans:
            plans.append(plan_filename)
        meta["plans"] = plans
        meta["updated_at"] = datetime.now(timezone.utc).isoformat()

        _safe_write(meta_path, json.dumps(meta, indent=2))

    def get_session_dir(self, session_id: str) -> Path:
        """Return the Path to a session directory.

        Raises RuntimeError with SESSION_NOT_FOUND if it does not exist.
        """
        session_dir = _sessions_dir() / session_id
        if not session_dir.exists():
            raise RuntimeError(f"{SESSION_NOT_FOUND}: {session_id}")
        return session_dir
