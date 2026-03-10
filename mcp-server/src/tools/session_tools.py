"""MCP tool registrations for session management.

Registers 4 tools: create_session, list_sessions, get_session, archive_session.
"""

import json
import logging

from mcp.server.fastmcp import FastMCP

from ..session.manager import SessionManager

logger = logging.getLogger(__name__)

_manager = SessionManager()


def register_session_tools(mcp: FastMCP) -> None:
    """Register all session management tools with the MCP server."""

    @mcp.tool()
    async def create_session(
        name: str,
        description: str = "",
        tags: list[str] | None = None,
    ) -> str:
        """Create a new VIBE planning session.

        Creates a session directory with a unique ID and metadata file.

        Args:
            name: Human-readable session name.
            description: Optional description of the session's purpose.
            tags: Optional list of freeform tags for categorization.

        Returns:
            JSON object with session metadata including session_id.
        """
        try:
            result = _manager.create_session(
                name=name, description=description, tags=tags
            )
            return json.dumps(result, indent=2)
        except RuntimeError as exc:
            return json.dumps({"error": str(exc)})

    @mcp.tool()
    async def list_sessions(
        tag: str | None = None,
        status: str | None = None,
    ) -> str:
        """List all VIBE planning sessions, with optional filtering.

        Args:
            tag: Filter sessions to only those containing this tag.
            status: Filter sessions by status (e.g. 'active', 'archived').

        Returns:
            JSON array of session metadata objects.
        """
        try:
            results = _manager.list_sessions(tag=tag, status=status)
            return json.dumps(results, indent=2)
        except RuntimeError as exc:
            return json.dumps({"error": str(exc)})

    @mcp.tool()
    async def get_session(session_id: str) -> str:
        """Retrieve a VIBE planning session's metadata and plan files.

        Args:
            session_id: The session ID in format YYYY-MM-DD-xxxxxx.

        Returns:
            JSON object with session metadata and list of .vibe files.
        """
        try:
            result = _manager.get_session(session_id)
            return json.dumps(result, indent=2)
        except RuntimeError as exc:
            return json.dumps({"error": str(exc)})

    @mcp.tool()
    async def archive_session(session_id: str) -> str:
        """Archive a VIBE planning session.

        Moves the session directory to the archive and sets status to 'archived'.

        Args:
            session_id: The session ID in format YYYY-MM-DD-xxxxxx.

        Returns:
            JSON object with updated session metadata.
        """
        try:
            result = _manager.archive_session(session_id)
            return json.dumps(result, indent=2)
        except RuntimeError as exc:
            return json.dumps({"error": str(exc)})
