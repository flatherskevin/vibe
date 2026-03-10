"""Parser and serializer for the .vibe.md format.

The .vibe.md format uses YAML frontmatter (between --- delimiters) for
vibe, meta, and imports fields, and a Markdown body for context, artifacts,
sections, decisions, and quality.

Public API:
    parse_vibe_md(text) -> dict    Parse a .vibe.md string into the 8-field dict.
    serialize_vibe_md(data) -> str  Render the 8-field dict back to .vibe.md format.
"""

from __future__ import annotations

import re
from typing import Any

import yaml


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_vibe_md(text: str) -> dict[str, Any]:
    """Parse a .vibe.md document into the canonical 8-field dict.

    Returns a dict with keys: vibe, meta, imports, context, artifacts,
    sections, decisions, quality.  Missing optional fields are omitted
    (same behaviour as the old YAML parser).
    """
    frontmatter_raw, body = _split_frontmatter(text)

    # Parse frontmatter YAML
    fm = yaml.safe_load(frontmatter_raw) if frontmatter_raw else {}
    if not isinstance(fm, dict):
        fm = {}

    result: dict[str, Any] = {}

    # Frontmatter fields
    if "vibe" in fm:
        result["vibe"] = fm["vibe"]
    if "meta" in fm:
        result["meta"] = fm["meta"]
    if "imports" in fm:
        result["imports"] = fm["imports"]

    # Body sections (split on ## headings)
    h2_blocks = _split_h2(body)

    for heading, content in h2_blocks:
        heading_lower = heading.strip().lower()
        if heading_lower == "context":
            result["context"] = _parse_context(content)
        elif heading_lower == "artifacts":
            result["artifacts"] = _parse_table_artifacts(content)
        elif heading_lower == "sections":
            result["sections"] = _parse_sections(content)
        elif heading_lower == "decisions":
            result["decisions"] = _parse_decisions(content)
        elif heading_lower == "quality":
            result["quality"] = _parse_table_quality(content)

    return result


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Split text into (frontmatter_yaml, body_markdown).

    Frontmatter is delimited by the first two lines that are exactly '---'.
    """
    lines = text.split("\n")
    # Find the opening ---
    start = None
    for i, line in enumerate(lines):
        if line.strip() == "---":
            start = i
            break
    if start is None:
        return "", text

    # Find the closing ---
    end = None
    for i in range(start + 1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return "", text

    frontmatter = "\n".join(lines[start + 1 : end])
    body = "\n".join(lines[end + 1 :])
    return frontmatter, body


def _split_h2(body: str) -> list[tuple[str, str]]:
    """Split markdown body into (heading, content) pairs on ## headings."""
    # Match lines that start with exactly "## " (not ###)
    pattern = re.compile(r"^## (?!#)", re.MULTILINE)
    parts: list[tuple[str, str]] = []
    matches = list(pattern.finditer(body))

    for i, m in enumerate(matches):
        line_end = body.index("\n", m.start()) if "\n" in body[m.start() :] else len(body)
        heading = body[m.start() + 3 : line_end].strip()
        content_start = line_end + 1
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        content = body[content_start:content_end].strip()
        parts.append((heading, content))

    return parts


def _split_h3(content: str) -> list[tuple[str, str]]:
    """Split content into (heading, body) pairs on ### headings."""
    pattern = re.compile(r"^### (?!#)", re.MULTILINE)
    parts: list[tuple[str, str]] = []
    matches = list(pattern.finditer(content))

    for i, m in enumerate(matches):
        line_end = content.index("\n", m.start()) if "\n" in content[m.start() :] else len(content)
        heading = content[m.start() + 4 : line_end].strip()
        body_start = line_end + 1
        body_end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        body = content[body_start:body_end].strip()
        parts.append((heading, body))

    return parts


def _slugify(text: str) -> str:
    """Convert heading text to a context key: lowercase, spaces/hyphens to underscores."""
    return re.sub(r"[\s\-]+", "_", text.strip().lower())


# ---- Context ----

def _parse_context(content: str) -> dict[str, Any]:
    """Parse ## Context into a dict of slugified_key -> markdown content."""
    h3_blocks = _split_h3(content)
    if not h3_blocks:
        # No sub-headings: treat entire content as a single "problem" key
        stripped = content.strip()
        return {"problem": stripped} if stripped else {}

    ctx: dict[str, Any] = {}
    for heading, body in h3_blocks:
        key = _slugify(heading)
        ctx[key] = body.strip()
    return ctx


# ---- Artifacts table ----

def _parse_table_artifacts(content: str) -> list[dict[str, Any]]:
    """Parse a markdown table under ## Artifacts into a list of artifact dicts."""
    rows = _parse_markdown_table(content)
    artifacts: list[dict[str, Any]] = []
    for row in rows:
        artifact: dict[str, Any] = {}
        for key, value in row.items():
            norm = key.strip().lower().replace(" ", "_")
            if not value.strip():
                continue
            if norm == "path":
                artifact["path"] = value.strip()
            elif norm == "kind":
                artifact["kind"] = value.strip()
            elif norm == "description":
                artifact["description"] = value.strip()
            elif norm == "status":
                artifact["status"] = value.strip()
            elif norm == "depends_on":
                artifact["depends_on"] = _split_semicolons(value)
            elif norm == "acceptance_criteria":
                artifact["acceptance_criteria"] = _split_semicolons(value)
        if artifact:
            artifacts.append(artifact)
    return artifacts


# ---- Quality table ----

def _parse_table_quality(content: str) -> list[dict[str, Any]]:
    """Parse a markdown table under ## Quality into a list of quality dicts."""
    rows = _parse_markdown_table(content)
    quality: list[dict[str, Any]] = []
    for row in rows:
        item: dict[str, Any] = {}
        for key, value in row.items():
            norm = key.strip().lower().replace(" ", "_")
            if not value.strip():
                continue
            if norm == "id":
                item["id"] = value.strip()
            elif norm == "type":
                item["type"] = value.strip()
            elif norm == "description":
                item["description"] = value.strip()
            elif norm == "criteria":
                item["criteria"] = value.strip()
        if item:
            quality.append(item)
    return quality


def _parse_markdown_table(content: str) -> list[dict[str, str]]:
    """Parse a markdown table into a list of row dicts keyed by header names.

    Handles escaped pipes (\\|) inside cells.
    """
    lines = [l for l in content.strip().split("\n") if l.strip()]
    if len(lines) < 2:
        return []

    # Find header line (first line with |)
    header_idx = None
    for i, line in enumerate(lines):
        if "|" in line:
            header_idx = i
            break
    if header_idx is None:
        return []

    headers = _split_table_row(lines[header_idx])
    if not headers:
        return []

    rows: list[dict[str, str]] = []
    for line in lines[header_idx + 1 :]:
        # Skip separator line (e.g. |---|---|)
        if re.match(r"^\s*\|[\s\-:|]+\|\s*$", line):
            continue
        if "|" not in line:
            continue
        cells = _split_table_row(line)
        row = {}
        for j, header in enumerate(headers):
            row[header] = cells[j] if j < len(cells) else ""
        rows.append(row)

    return rows


def _split_table_row(line: str) -> list[str]:
    """Split a markdown table row on | delimiters, handling escaped pipes."""
    # Replace escaped pipes with a placeholder
    placeholder = "\x00PIPE\x00"
    line = line.replace("\\|", placeholder)
    parts = line.split("|")
    # Strip leading/trailing empty parts from outer pipes
    if parts and not parts[0].strip():
        parts = parts[1:]
    if parts and not parts[-1].strip():
        parts = parts[:-1]
    return [p.replace(placeholder, "|").strip() for p in parts]


def _split_semicolons(value: str) -> list[str]:
    """Split a semicolon-delimited string into a list, stripping whitespace."""
    return [v.strip() for v in value.split(";") if v.strip()]


# ---- Sections ----

def _parse_sections(content: str) -> list[dict[str, Any]]:
    """Parse ## Sections into a list of section dicts.

    Each ### heading is a section. An HTML comment immediately after
    the heading carries metadata: <!-- id: ..., type: ..., depends_on: ... -->
    """
    h3_blocks = _split_h3(content)
    sections: list[dict[str, Any]] = []

    for heading, body in h3_blocks:
        section: dict[str, Any] = {"title": heading}
        # Extract HTML comment metadata
        meta, remaining = _extract_html_comment_meta(body)
        if "id" in meta:
            section["id"] = meta["id"]
        if "type" in meta:
            section["type"] = meta["type"]
        if "depends_on" in meta:
            deps = [d.strip() for d in meta["depends_on"].split(",") if d.strip()]
            section["depends_on"] = deps

        body_text = remaining.strip()
        if body_text:
            section["content"] = body_text

        sections.append(section)

    return sections


# ---- Decisions ----

def _parse_decisions(content: str) -> list[dict[str, Any]]:
    """Parse ## Decisions into a list of decision dicts.

    Each ### heading is a decision title. HTML comment carries id and status.
    Body uses bold-label patterns for Context, Options, Chosen, Rationale,
    Consequences.
    """
    h3_blocks = _split_h3(content)
    decisions: list[dict[str, Any]] = []

    for heading, body in h3_blocks:
        decision: dict[str, Any] = {"title": heading}
        meta, remaining = _extract_html_comment_meta(body)
        if "id" in meta:
            decision["id"] = meta["id"]
        if "status" in meta:
            decision["status"] = meta["status"]

        # Parse bold-label patterns from remaining text
        _parse_decision_body(decision, remaining)
        decisions.append(decision)

    return decisions


def _parse_decision_body(decision: dict[str, Any], body: str) -> None:
    """Parse bold-label patterns from a decision body."""
    # Split body into sections by **Label:** patterns
    label_pattern = re.compile(r"^\*\*(\w[\w\s]*):\*\*\s*", re.MULTILINE)
    matches = list(label_pattern.finditer(body))

    for i, m in enumerate(matches):
        label = m.group(1).strip().lower()
        value_start = m.end()
        value_end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        value = body[value_start:value_end].strip()

        if label == "context":
            decision["context"] = value
        elif label == "chosen":
            decision["chosen"] = value
        elif label == "rationale":
            decision["rationale"] = value
        elif label == "options":
            decision["options"] = _parse_options_list(value)
        elif label == "consequences":
            decision["consequences"] = _parse_bullet_list(value)


def _parse_options_list(text: str) -> list[dict[str, str]]:
    """Parse options from a list of '- **name**: description' items."""
    options: list[dict[str, str]] = []
    for m in re.finditer(r"-\s+\*\*(\w[\w\s]*)\*\*:\s*(.*?)(?=\n-\s+\*\*|\Z)", text, re.DOTALL):
        options.append({
            "name": m.group(1).strip(),
            "description": m.group(2).strip(),
        })
    return options


def _parse_bullet_list(text: str) -> list[str]:
    """Parse a markdown bullet list into a list of strings."""
    items: list[str] = []
    for line in text.strip().split("\n"):
        line = line.strip()
        if line.startswith("- "):
            items.append(line[2:].strip())
    return items


# ---- HTML comment metadata ----

def _extract_html_comment_meta(body: str) -> tuple[dict[str, str], str]:
    """Extract <!-- key: value, ... --> from the start of body text.

    Returns (meta_dict, remaining_body).
    """
    m = re.match(r"\s*<!--\s*(.*?)\s*-->\s*", body, re.DOTALL)
    if not m:
        return {}, body

    meta_str = m.group(1)
    remaining = body[m.end():]

    meta: dict[str, str] = {}
    for pair in meta_str.split(","):
        if ":" in pair:
            k, v = pair.split(":", 1)
            meta[k.strip()] = v.strip()

    return meta, remaining


# ---------------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------------

def serialize_vibe_md(data: dict[str, Any]) -> str:
    """Render the canonical 8-field dict back to .vibe.md format."""
    parts: list[str] = []

    # Frontmatter
    fm: dict[str, Any] = {}
    if "vibe" in data:
        fm["vibe"] = data["vibe"]
    if "meta" in data:
        fm["meta"] = data["meta"]
    if "imports" in data:
        fm["imports"] = data["imports"]

    fm_yaml = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True).strip()
    # Ensure vibe value is double-quoted as string to avoid numeric coercion
    # Handles: vibe: 2.0 (unquoted) and vibe: '2.0' (single-quoted from yaml.dump)
    fm_yaml = re.sub(r"^(vibe:\s*)'?(\d+\.\d+)'?\s*$", r'\1"\2"', fm_yaml, flags=re.MULTILINE)
    parts.append(f"---\n{fm_yaml}\n---")

    # Context
    if "context" in data and data["context"]:
        parts.append(_serialize_context(data["context"]))

    # Artifacts
    if "artifacts" in data and data["artifacts"]:
        parts.append(_serialize_artifacts(data["artifacts"]))

    # Sections
    if "sections" in data and data["sections"]:
        parts.append(_serialize_sections(data["sections"]))

    # Decisions
    if "decisions" in data and data["decisions"]:
        parts.append(_serialize_decisions(data["decisions"]))

    # Quality
    if "quality" in data and data["quality"]:
        parts.append(_serialize_quality(data["quality"]))

    return "\n\n".join(parts) + "\n"


def _serialize_context(context: dict[str, Any]) -> str:
    """Serialize context dict to ## Context with ### subheadings."""
    lines = ["## Context"]
    for key, value in context.items():
        # Convert key back to title case heading
        heading = key.replace("_", " ").title()
        lines.append(f"\n### {heading}\n")
        lines.append(str(value).strip())
    return "\n".join(lines)


def _serialize_artifacts(artifacts: list[dict[str, Any]]) -> str:
    """Serialize artifacts list to a ## Artifacts markdown table."""
    columns = ["Path", "Kind", "Description", "Status", "Depends On", "Acceptance Criteria"]
    rows: list[list[str]] = []
    for a in artifacts:
        rows.append([
            a.get("path", ""),
            a.get("kind", ""),
            a.get("description", ""),
            a.get("status", ""),
            "; ".join(a.get("depends_on", [])),
            "; ".join(a.get("acceptance_criteria", [])),
        ])
    return "## Artifacts\n\n" + _build_markdown_table(columns, rows)


def _serialize_quality(quality: list[dict[str, Any]]) -> str:
    """Serialize quality list to a ## Quality markdown table."""
    columns = ["ID", "Type", "Description", "Criteria"]
    rows: list[list[str]] = []
    for q in quality:
        rows.append([
            q.get("id", ""),
            q.get("type", ""),
            q.get("description", ""),
            q.get("criteria", ""),
        ])
    return "## Quality\n\n" + _build_markdown_table(columns, rows)


def _build_markdown_table(columns: list[str], rows: list[list[str]]) -> str:
    """Build a markdown table from column headers and row data."""
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, separator]
    for row in rows:
        # Escape pipes in cell values
        cells = [c.replace("|", "\\|") for c in row]
        # Pad to match column count
        while len(cells) < len(columns):
            cells.append("")
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _serialize_sections(sections: list[dict[str, Any]]) -> str:
    """Serialize sections list to ## Sections with ### headings and HTML comments."""
    lines = ["## Sections"]
    for s in sections:
        title = s.get("title", "Untitled")
        lines.append(f"\n### {title}")

        # Build HTML comment metadata
        meta_parts: list[str] = []
        if "id" in s:
            meta_parts.append(f"id: {s['id']}")
        if "type" in s:
            meta_parts.append(f"type: {s['type']}")
        if "depends_on" in s and s["depends_on"]:
            meta_parts.append(f"depends_on: {', '.join(s['depends_on'])}")
        if meta_parts:
            lines.append(f"<!-- {', '.join(meta_parts)} -->")

        if "content" in s and s["content"]:
            lines.append("")
            lines.append(s["content"].strip())
    return "\n".join(lines)


def _serialize_decisions(decisions: list[dict[str, Any]]) -> str:
    """Serialize decisions list to ## Decisions with ### headings and bold-labels."""
    lines = ["## Decisions"]
    for d in decisions:
        title = d.get("title", "Untitled")
        lines.append(f"\n### {title}")

        # HTML comment for id and status
        meta_parts: list[str] = []
        if "id" in d:
            meta_parts.append(f"id: {d['id']}")
        if "status" in d:
            meta_parts.append(f"status: {d['status']}")
        if meta_parts:
            lines.append(f"<!-- {', '.join(meta_parts)} -->")

        lines.append("")

        if "context" in d:
            lines.append(f"**Context:** {d['context'].strip()}")
            lines.append("")
        if "options" in d:
            lines.append("**Options:**")
            lines.append("")
            for opt in d["options"]:
                lines.append(f"- **{opt.get('name', '')}**: {opt.get('description', '')}")
            lines.append("")
        if "chosen" in d:
            lines.append(f"**Chosen:** {d['chosen'].strip()}")
            lines.append("")
        if "rationale" in d:
            lines.append(f"**Rationale:** {d['rationale'].strip()}")
            lines.append("")
        if "consequences" in d:
            lines.append("**Consequences:**")
            lines.append("")
            for c in d["consequences"]:
                lines.append(f"- {c}")
    return "\n".join(lines)
