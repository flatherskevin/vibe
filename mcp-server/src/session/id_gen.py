"""Session ID generation for VIBE MCP server.

Generates IDs in the format {YYYY-MM-DD}-{6-char-hex} using os.urandom(3).
"""

import os
from datetime import datetime, timezone


def generate_session_id() -> str:
    """Generate a session ID in the format {YYYY-MM-DD}-{6-char-hex}.

    Uses the current UTC date and 3 random bytes (6 hex chars) for uniqueness.
    """
    date_part = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    hex_part = os.urandom(3).hex()
    return f"{date_part}-{hex_part}"
