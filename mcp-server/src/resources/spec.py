"""MCP resource registrations for VIBE specification and template resources.

Registers:
- vibe://spec/v2          -- VIBE_SPEC_v2.md (or v1 as fallback)
- vibe://spec/format      -- Condensed v2 format reference
- vibe://templates/{name} -- One resource per template archetype
- vibe://stdlib/quality   -- Standard quality criteria library
"""

import logging
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)


def _find_vibe_dir() -> Path:
    """Locate the vibe/ directory containing spec, stdlib, schema, templates."""
    env_path = os.environ.get("VIBE_DIR")
    if env_path:
        p = Path(env_path)
        if p.exists():
            return p

    # Relative to this file: src/resources/spec.py -> mcp-server/ -> repo root
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    candidates = [
        project_root / "vibe",
        Path("/app/vibe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        "Could not locate vibe/ directory. Set VIBE_DIR or ensure "
        "the directory exists at the repository root."
    )


def _read_file_safe(path: Path) -> str:
    """Read a file and return its contents, or an error message if it fails."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        msg = f"FILE_NOT_FOUND: Could not read {path}: {exc}"
        logger.warning(msg)
        return msg


_FORMAT_REFERENCE = """\
# VIBE v2 Condensed Format Reference

## File Structure
Every .vibe.md file is a markdown document with YAML frontmatter.
It has two parts: frontmatter (between `---` delimiters) and a markdown body.

## Frontmatter Fields (YAML between --- delimiters)
| Field | Required | Type |
|-------|----------|------|
| vibe | Yes | string ("2.0") |
| meta | No | object |
| imports | No | array of strings (.vibe.md paths) |

## Markdown Body Sections
| Section | Format |
|---------|--------|
| ## Context | ### subheadings as keys, content as values |
| ## Artifacts | Markdown table (Path required) |
| ## Sections | ### headings with <!-- id, type, depends_on --> comments |
| ## Decisions | ### headings with <!-- id, status --> and bold-label body |
| ## Quality | Markdown table (ID, Description required) |

## meta Fields
name, description, session_id, created_at, updated_at, author, tags, status

## context Keys (from ### headings, slugified)
problem, constraints, assumptions, scope, glossary (+ freeform keys)

## Artifacts Table Columns
Path, Kind, Description, Status (planned|in_progress|complete), Depends On, Acceptance Criteria

## Sections Metadata (in <!-- --> comments)
id (required), type (analysis|design|decision|specification|risk|checklist), depends_on

## Decisions Metadata and Body
Comment: <!-- id, status (proposed|accepted|deprecated|superseded) -->
Body: **Context:**, **Options:** (- **name**: desc), **Chosen:**, **Rationale:**, **Consequences:**

## Quality Table Columns
ID (required), Description (required), Type (review|test|metric|checklist), Criteria

## Session ID Format
{YYYY-MM-DD}-{6-char-hex} (e.g. 2026-03-10-a1b2c3)

## Document Statuses
draft -> review -> final
"""


# Template archetypes and their file paths relative to vibe/stdlib/templates/
_TEMPLATE_ARCHETYPES = {
    "overview": "overview.vibe.md",
    "architecture": "architecture.vibe.md",
    "implementation_plan": "implementation_plan.vibe.md",
    "risk_assessment": "risk_assessment.vibe.md",
    "adr_collection": "adr_collection.vibe.md",
}


def register_spec_resources(mcp: FastMCP) -> None:
    """Register all VIBE spec and template resources with the MCP server."""

    try:
        vibe_dir = _find_vibe_dir()
    except FileNotFoundError as exc:
        logger.error("Cannot register spec resources: %s", exc)
        return

    # ---- vibe://spec/v2 ----
    @mcp.resource("vibe://spec/v2")
    async def spec_v2() -> str:
        """The VIBE v2 specification document.

        Returns the full VIBE specification markdown document that defines
        the .vibe.md file format, frontmatter fields, and document model.
        """
        # Try v2 spec first, fall back to v1
        for name in ("VIBE_SPEC_v2.md", "VIBE_SPEC_v1.md"):
            path = vibe_dir / "spec" / name
            if path.exists():
                return _read_file_safe(path)
        return "FILE_NOT_FOUND: No VIBE spec document found."

    # ---- vibe://spec/format ----
    @mcp.resource("vibe://spec/format")
    async def spec_format() -> str:
        """Condensed VIBE v2 format reference.

        A quick-reference summary of the VIBE v2 .vibe.md document format
        including frontmatter fields, body sections, and allowed values.
        """
        return _FORMAT_REFERENCE

    # ---- vibe://templates/{archetype} ----
    for archetype_name, template_filename in _TEMPLATE_ARCHETYPES.items():
        _register_template_resource(mcp, vibe_dir, archetype_name, template_filename)

    # ---- vibe://stdlib/quality ----
    @mcp.resource("vibe://stdlib/quality")
    async def stdlib_quality() -> str:
        """The VIBE standard library quality criteria module.

        Contains reusable quality criteria that any .vibe.md document can import.
        Criteria IDs are prefixed with stdlib_ to avoid collisions.
        """
        path = vibe_dir / "stdlib" / "quality.vibe.md"
        return _read_file_safe(path)


def _register_template_resource(
    mcp: FastMCP,
    vibe_dir: Path,
    archetype_name: str,
    template_filename: str,
) -> None:
    """Register a single template resource.

    Uses a factory function to correctly capture the loop variables.
    """
    uri = f"vibe://templates/{archetype_name}"
    template_path = vibe_dir / "stdlib" / "templates" / template_filename

    @mcp.resource(uri)
    async def template_resource(
        _path: Path = template_path,
        _name: str = archetype_name,
    ) -> str:
        f"""VIBE v2 template for {_name} documents.

        A starter template with placeholder sections appropriate for
        creating {_name} planning documents.
        """
        return _read_file_safe(_path)
