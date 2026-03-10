# VIBE Integration Hooks (v2.0)

This document defines how external tools integrate with `.vibe` files.

In v1 this document was called Runtime Hooks and defined pre/post execution callbacks. In v2 there is no runtime to hook into. Instead, integration hooks describe how tools consume, validate, and present .vibe documents without executing them.

---

## 1. MCP Integration

The VIBE MCP server is the primary integration point for AI systems. It exposes .vibe document capabilities via the Model Context Protocol.

### 1.1 Tools

The MCP server provides tools that AI systems call during planning:

| Tool | Purpose |
|---|---|
| `create_session` | Create a new planning session with ID, name, and tags |
| `write_plan` | Write a .vibe document to a session (validates against schema) |
| `read_plan` | Read a .vibe document from a session |
| `list_sessions` | List active sessions with optional filtering |
| `get_session` | Get detailed session info including file list |
| `archive_session` | Move a session to archive storage |

Tools use structured JSON parameters and return structured JSON responses. Schema validation on `write_plan` is advisory: files are written even if validation fails, with errors returned in the response.

### 1.2 Prompts

The MCP server exposes one prompt:

**plan_in_vibe** -- Instructs the AI to produce output in .vibe v2 format.

Arguments:

- `document_type` (optional): Archetype hint (`overview`, `architecture`, `implementation_plan`, `risk_assessment`, `adr_collection`)
- `session_id` (optional): Session to write into (provides existing plans as context)

The prompt returns a system message containing:

- Condensed v2 format specification
- Section type reference
- Document archetype guidance (if document_type is provided)
- Example document skeleton
- Session context (if session_id is provided)
- Instructions to use the `write_plan` tool for output

### 1.3 Resources

The MCP server exposes read-only resources:

| Resource URI | Content |
|---|---|
| `vibe://spec/v2` | Full VIBE v2 specification (text/markdown) |
| `vibe://spec/format` | Condensed format reference (text/yaml) |
| `vibe://templates/overview` | Overview document template (text/yaml) |
| `vibe://templates/architecture` | Architecture document template (text/yaml) |
| `vibe://templates/implementation_plan` | Implementation plan template (text/yaml) |
| `vibe://templates/risk_assessment` | Risk assessment template (text/yaml) |
| `vibe://templates/adr_collection` | ADR collection template (text/yaml) |
| `vibe://stdlib/quality` | Standard quality criteria library (text/yaml) |

Resources allow AI systems to read spec documents and templates without filesystem access.

### 1.4 MCP Client Configuration

To connect the VIBE MCP server to an MCP-compatible client (Claude Desktop, Cursor, etc.), add it to the client's MCP server configuration:

```json
{
  "mcpServers": {
    "vibe": {
      "command": "docker",
      "args": ["compose", "-f", "mcp-server/docker-compose.yml", "run", "--rm", "vibe-mcp"],
      "env": {}
    }
  }
}
```

The server uses stdio transport: communication over stdin/stdout with no HTTP server or port management.

---

## 2. IDE Integration

IDEs and editors integrate with .vibe files through standard editor extension mechanisms.

### 2.1 Syntax Highlighting

VIBE provides a TextMate grammar at `syntaxes/vibe.tmLanguage.json` that supports:

- Version line highlighting (`vibe: 2.0`)
- Top-level key recognition (`meta`, `imports`, `context`, `artifacts`, `sections`, `decisions`, `quality`)
- YAML key/value highlighting
- String, number, and boolean literals
- File path recognition (`.vibe`, `.md`, `.json`, `.ts`, `.py`, etc.)
- Block scalar indicators (`|`, `>`)
- Comment highlighting (`#`)
- Embedded JSON block recognition

### 2.2 File Association

`.vibe` files should be associated with the VIBE language mode in editor settings.

VS Code example (`.vscode/settings.json`):

```json
{
  "files.associations": {
    "*.vibe": "vibe"
  }
}
```

### 2.3 Structure Preview

IDEs can provide structure preview for .vibe files by parsing the YAML and presenting:

- Document metadata (name, status, author)
- Section list with types and titles
- Decision list with statuses
- Artifact list with statuses
- Quality criteria list

This does not require a language server. YAML parsing and a simple renderer are sufficient.

### 2.4 Navigation

IDEs can support navigation features:

- Jump to section by ID (within the document)
- Jump to imported file (follow import paths)
- Jump to referenced section (follow `depends_on` links)
- Outline view showing sections, decisions, and quality criteria

### 2.5 Validation

IDEs can validate .vibe files in real time:

- YAML syntax validation (immediate feedback on parse errors)
- Schema validation against `vibe/schema/vibe.schema.json` (type checking, enum validation)
- Import resolution (verify imported files exist)

Validation should be advisory, showing warnings and errors in the editor without blocking editing.

---

## 3. CI/CD Integration

CI/CD pipelines integrate with .vibe files for quality assurance and change tracking.

### 3.1 Schema Validation in Pipelines

A CI job can validate all .vibe files in a repository against the v2 schema:

```yaml
# Example GitHub Actions step
- name: Validate VIBE documents
  run: |
    pip install pyyaml jsonschema
    python -c "
    import yaml, jsonschema, glob, sys
    schema = yaml.safe_load(open('vibe/schema/vibe.schema.json'))
    errors = 0
    for path in glob.glob('**/*.vibe', recursive=True):
        doc = yaml.safe_load(open(path))
        try:
            jsonschema.validate(doc, schema)
        except jsonschema.ValidationError as e:
            print(f'FAIL: {path}: {e.message}')
            errors += 1
    sys.exit(1 if errors else 0)
    "
```

### 3.2 Plan Diff Tracking

When .vibe files change in a pull request, CI can produce a structured diff:

- New sections added
- Decisions changed (status transitions, rationale updates)
- Artifacts added or removed
- Quality criteria modified

This is more useful than raw text diffs because it highlights semantic changes rather than formatting changes.

### 3.3 Import Validation

CI can verify that all imports resolve:

- Every path in every `imports` array points to an existing file
- No circular imports exist
- No imports reference files outside the repository

### 3.4 Status Checks

CI can enforce conventions:

- Documents merged to main must have `status: final` (or `review` at minimum)
- All decisions must have `status: accepted` (not `proposed`)
- All artifacts must have `status: complete`
- All quality criteria must have corresponding evidence

These checks are project-specific and should be configurable.

### 3.5 Version Consistency

CI can verify that all .vibe files in the repository declare the same `vibe` version. Mixed v1 and v2 files in the same project may indicate an incomplete migration.

---

## 4. Custom Import Resolvers

The standard import mechanism resolves paths relative to the filesystem. Custom import resolvers extend this for non-filesystem sources.

### 4.1 Use Cases

- Importing from a package registry (e.g., `vibe://registry/auth-patterns/v1.2`)
- Importing from a remote Git repository
- Importing from a database or document store
- Importing from a template service

### 4.2 Resolver Interface

A custom resolver takes an import path and returns the content of the resolved .vibe file. The interface is:

```
input:  import_path (string), base_directory (string)
output: file_content (string) or error
```

The resolver is responsible for:

- Determining whether it handles the given path (e.g., paths starting with `vibe://`)
- Fetching the content from the external source
- Returning valid YAML content

The consumer's import resolution algorithm calls the resolver instead of filesystem access when the path matches the resolver's pattern.

### 4.3 Resolver Chaining

Consumers MAY support multiple resolvers in a priority chain:

1. Custom resolvers are checked first (in registered order)
2. If no custom resolver handles the path, fall back to filesystem resolution

### 4.4 Security

Custom resolvers MUST respect the same security constraints as filesystem imports:

- No access to paths outside the allowed scope
- No execution of code during resolution
- Network access should be explicit and auditable
- Resolved content is still validated as YAML and (optionally) against the schema

---

## 5. Ecosystem Conventions

These conventions help maintain consistency across projects using VIBE.

### 5.1 File Naming

Recommended naming patterns for .vibe files:

| Pattern | Use |
|---|---|
| `project.vibe` | Root document for the project |
| `{NN}_{name}.vibe` | Ordered planning documents (e.g., `00_vision.vibe`, `10_architecture.vibe`) |
| `{domain}.vibe` | Domain-specific documents (e.g., `auth.vibe`, `payments.vibe`) |

The numbered prefix convention (`00_`, `10_`, `20_`) provides natural ordering when files are listed alphabetically. Gaps between numbers (10, 20 instead of 1, 2) allow inserting documents later.

### 5.2 Directory Structure

Recommended project layout:

```
project.vibe                     # Root document
vibe/
  spec/                          # VIBE specification documents
  schema/                        # JSON Schema for validation
    vibe.schema.json
  stdlib/                        # Standard library modules
    quality.vibe
    context_budget.vibe
    templates/                   # Document archetype templates
  templates/                     # Project-specific templates
plans/                           # Planning session documents
  00_vision.vibe
  10_architecture.vibe
```

### 5.3 Session Management

When using the MCP server, sessions are stored under `data/sessions/`. Each session is a directory named by its session ID (`{YYYY-MM-DD}-{6-char-hex}`).

Conventions for session workflow:

1. Create a session for each planning initiative
2. Write documents into the session using `write_plan`
3. Review documents (update status from `draft` to `review` to `final`)
4. Archive completed sessions
5. Reference prior sessions via cross-session imports when building on previous work

### 5.4 Import Conventions

- Import stdlib modules from `vibe/stdlib/` for reusable quality criteria and context
- Import sibling plan documents for cross-referencing within a session
- Use relative paths (not absolute) for all imports
- Keep import chains shallow (prefer flat imports over deep chains)

### 5.5 Standard Library

The VIBE standard library under `vibe/stdlib/` provides importable modules:

| Module | Purpose |
|---|---|
| `quality.vibe` | Standard quality criteria (YAML validity, schema validity, completeness checks) |
| `context_budget.vibe` | Context budgeting guidance for AI systems working with large plans |
| `templates/overview.vibe` | Template for overview documents |
| `templates/architecture.vibe` | Template for architecture documents |
| `templates/implementation_plan.vibe` | Template for implementation plans |
| `templates/risk_assessment.vibe` | Template for risk assessments |
| `templates/adr_collection.vibe` | Template for ADR collections |

---

## 6. Relationship to Other Documents

- `VIBE_SPEC_v2.md` -- Core format specification.
- `VIBE_CONSUMER_CONTRACT.md` -- Consumer requirements that all integrations must follow.
- `VIBE_MERGE_SEMANTICS.md` -- Merge rules relevant to import resolution.
- `VIBE_DOCUMENT_TYPES.md` -- Section types and archetypes referenced by MCP prompts and templates.
- `VIBE_MCP_SERVER.md` -- Detailed MCP server specification.
