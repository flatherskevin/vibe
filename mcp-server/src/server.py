"""VIBE MCP Server -- Main entry point.

Creates a FastMCP server instance, registers tools, prompts, and resources
from submodules, and runs with stdio transport.
"""

import logging
import sys

from mcp.server.fastmcp import FastMCP

# Configure logging to stderr (never stdout, which is used for MCP JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("vibe-mcp-server")

# Create the MCP server instance
mcp = FastMCP("vibe-mcp-server")


def _register_all() -> None:
    """Register all tools, prompts, and resources from submodules."""
    from .tools.session_tools import register_session_tools
    from .tools.plan_tools import register_plan_tools
    from .prompts.plan_in_vibe import register_plan_in_vibe_prompt
    from .resources.spec import register_spec_resources

    register_session_tools(mcp)
    register_plan_tools(mcp)
    register_plan_in_vibe_prompt(mcp)
    register_spec_resources(mcp)

    logger.info("All tools, prompts, and resources registered.")


def main() -> None:
    """Initialize and run the VIBE MCP server with stdio transport."""
    _register_all()
    logger.info("Starting VIBE MCP server on stdio transport...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
