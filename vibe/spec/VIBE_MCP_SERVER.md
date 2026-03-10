# VIBE MCP Server Specification

Local MCP server for creating and managing `.vibe` planning documents.

The VIBE MCP server provides a Model Context Protocol interface for AI agents and tools to create, read, validate, and manage `.vibe` planning sessions. It is the recommended integration path for AI systems that produce or consume VIBE v1 documents.

---

## 1. Overview

The VIBE MCP server is a local Python server that exposes six tools, one prompt, and a set of resources for working with `.vibe` planning documents.

It provides:

- session-based document management
- YAML parsing and schema validation
- access to the VIBE v1 spec, format reference, and templates
- a structured error model for all failure modes

The server does not execute plans. It creates, validates, and organizes planning documents.

---

## 2. Setup

### 2.1 Docker Image

The server runs as a Docker container built on `python:3.12-slim`.

Dockerfile summary:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/ ./server/
COPY vibe/ ./vibe/

EXPOSE 8080
CMD ["python", "-m", "server.main"]
```

### 2.2 Dependencies

```
mcp>=1.0
pyyaml>=6.0
jsonschema>=4.20
```

### 2.3 Configuration

The server reads configuration from environment variables:

| Variable | Default | Description |
|---|---|---|
| `VIBE_SESSIONS_DIR` | `./sessions` | Root directory for session storage |
| `VIBE_ARCHIVE_DIR` | `./archive` | Root directory for archived sessions |
| `VIBE_SPEC_DIR` | `./vibe/spec` | Path to VIBE spec documents |
| `VIBE_STDLIB_DIR` | `./vibe/stdlib` | Path to standard library |
| `VIBE_TEMPLATES_DIR` | `./vibe/templates` | Path to document templates |

### 2.4 Running Locally

```bash
docker build -t vibe-mcp-server .
docker run -p 8080:8080 \
  -v $(pwd)/sessions:/app/sessions \
  -v $(pwd)/vibe:/app/vibe \
  vibe-mcp-server
```

---

## 3. Tools Reference

The server exposes six tools via the MCP protocol.

### 3.1 `create_session`

Creates a new planning session with a unique ID and session directory.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Human-readable session name |
| `description` | string | No | Session purpose or scope |
| `tags` | string[] | No | Tags for filtering and organization |

**Returns:**

```json
{
  "session_id": "2026-03-10-a1b2c3",
  "path": "sessions/2026-03-10-a1b2c3/",
  "created_at": "2026-03-10T14:30:00Z"
}
```

**Behavior:**

- Creates the session directory under `VIBE_SESSIONS_DIR`
- Writes a `session.json` metadata file
- Sets session status to `active`

---

### 3.2 `write_plan`

Writes a `.vibe` planning document into a session directory and validates it.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | Target session ID |
| `filename` | string | Yes | Filename for the document (must end in `.vibe`) |
| `content` | string | Yes | YAML content of the `.vibe` document |

**Returns:**

```json
{
  "path": "sessions/2026-03-10-a1b2c3/feature_plan.vibe",
  "valid": true,
  "errors": []
}
```

If validation fails, `valid` is `false` and `errors` contains structured error objects:

```json
{
  "path": "sessions/2026-03-10-a1b2c3/feature_plan.vibe",
  "valid": false,
  "errors": [
    {
      "code": "SCHEMA_VALIDATION_FAILED",
      "message": "Field 'vibe' is required",
      "path": "$.vibe"
    }
  ]
}
```

**Behavior:**

- Parses the content as YAML
- Validates against `vibe/schema/vibe.schema.json`
- Writes the file regardless of validation result (so the author can iterate)
- Updates `session.json` with the new file entry

---

### 3.3 `read_plan`

Reads a `.vibe` document from a session and returns both raw and parsed content.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | Session ID to read from |
| `filename` | string | Yes | Filename of the document |

**Returns:**

```json
{
  "content": "vibe: 1.0\nmeta:\n  name: ...",
  "parsed": { "vibe": "1.0", "meta": { "name": "..." } },
  "valid": true
}
```

**Behavior:**

- Reads the file from the session directory
- Parses YAML into a structured object
- Validates against the schema
- Returns all three representations (raw, parsed, validity)

---

### 3.4 `list_sessions`

Lists sessions with optional filtering by tag or status.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `tag` | string | No | Filter sessions by tag |
| `status` | string | No | Filter by status: `active`, `archived`, `all` |

**Returns:**

```json
{
  "sessions": [
    {
      "session_id": "2026-03-10-a1b2c3",
      "name": "Auth Feature Plan",
      "status": "active",
      "tags": ["auth", "backend"],
      "created_at": "2026-03-10T14:30:00Z",
      "file_count": 3
    }
  ]
}
```

**Behavior:**

- Scans `VIBE_SESSIONS_DIR` for session directories
- Reads each `session.json` for metadata
- Applies tag and status filters if provided
- Returns sessions sorted by `created_at` descending

---

### 3.5 `get_session`

Returns full session metadata including file listing.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | Session ID to retrieve |

**Returns:**

```json
{
  "session_id": "2026-03-10-a1b2c3",
  "name": "Auth Feature Plan",
  "description": "Plan authentication system with JWT tokens",
  "status": "active",
  "tags": ["auth", "backend"],
  "created_at": "2026-03-10T14:30:00Z",
  "files": [
    {
      "filename": "auth_plan.vibe",
      "valid": true,
      "modified_at": "2026-03-10T14:35:00Z"
    },
    {
      "filename": "api_design.vibe",
      "valid": false,
      "modified_at": "2026-03-10T14:40:00Z"
    }
  ]
}
```

**Behavior:**

- Reads `session.json` for metadata
- Lists all `.vibe` files in the session directory
- Validates each file and reports validity

---

### 3.6 `archive_session`

Archives a session by moving it from the active sessions directory to the archive directory.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | Session ID to archive |

**Returns:**

```json
{
  "archived": true,
  "archive_path": "archive/2026-03-10-a1b2c3/"
}
```

**Behavior:**

- Moves the session directory from `VIBE_SESSIONS_DIR` to `VIBE_ARCHIVE_DIR`
- Updates `session.json` status to `archived`
- Adds `archived_at` timestamp

---

## 4. Prompts

### 4.1 `plan_in_vibe`

A prompt template that guides AI agents through creating a `.vibe` planning document.

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| `document_type` | string | No | Archetype to use (e.g., `feature`, `migration`, `investigation`) |
| `session_id` | string | No | Existing session to add the document to |

**Behavior:**

The prompt assembles context from:

1. The VIBE v1 format reference (`vibe://spec/format`)
2. The relevant archetype template if `document_type` is provided (`vibe://templates/{archetype}`)
3. Quality criteria from the standard library (`vibe://stdlib/quality`)
4. The current session state if `session_id` is provided

The assembled prompt instructs the AI agent to produce a valid `.vibe` document that includes the required `vibe: 1.0` header, `meta` block, and appropriate sections for the document type.

---

## 5. Resources

The server exposes the following MCP resources.

### 5.1 `vibe://spec/v1`

The full VIBE v1 specification (`VIBE_SPEC_v1.md`).

Use this resource when an agent needs the normative spec for authoring or validating documents.

### 5.2 `vibe://spec/format`

A concise format reference covering the top-level fields, section types, and YAML conventions. Designed as a quick-reference for agents that already understand the VIBE model.

### 5.3 `vibe://templates/{archetype}`

Archetype-specific document templates. Available archetypes:

| Archetype | Description |
|---|---|
| `feature` | New feature planning document |
| `migration` | System migration or upgrade plan |
| `investigation` | Research or spike document |
| `bugfix` | Bug analysis and fix plan |
| `refactor` | Refactoring plan with before/after |

Templates provide a skeleton `.vibe` document with suggested sections, placeholder content, and quality criteria appropriate to the archetype.

### 5.4 `vibe://stdlib/quality`

The standard quality criteria library (`vibe/stdlib/quality.vibe`). Contains reusable quality definitions that documents can reference or import.

---

## 6. Session Management

### 6.1 Session ID Format

Session IDs follow the format:

```
{YYYY-MM-DD}-{6-char-hex}
```

Examples:

```
2026-03-10-a1b2c3
2026-03-10-f4e5d6
```

The date prefix is the creation date. The hex suffix is randomly generated to ensure uniqueness.

### 6.2 Directory Layout

Each session is a directory containing a metadata file and `.vibe` documents:

```
sessions/
  2026-03-10-a1b2c3/
    session.json
    feature_plan.vibe
    api_design.vibe
    data_model.vibe
```

### 6.3 `session.json` Metadata

Each session directory contains a `session.json` file:

```json
{
  "session_id": "2026-03-10-a1b2c3",
  "name": "Auth Feature Plan",
  "description": "Plan authentication system with JWT tokens",
  "status": "active",
  "tags": ["auth", "backend"],
  "created_at": "2026-03-10T14:30:00Z",
  "files": [
    {
      "filename": "auth_plan.vibe",
      "added_at": "2026-03-10T14:35:00Z"
    }
  ]
}
```

**Status values:**

| Status | Meaning |
|---|---|
| `active` | Session is in use |
| `archived` | Session has been archived |

### 6.4 Archive Layout

Archived sessions are stored under `VIBE_ARCHIVE_DIR` with the same directory structure:

```
archive/
  2026-03-10-a1b2c3/
    session.json
    feature_plan.vibe
    api_design.vibe
```

The `session.json` in an archived session includes an `archived_at` timestamp.

---

## 7. Error Handling

All tools return structured errors. Each error includes a `code`, a human-readable `message`, and an optional `path` indicating the source of the error.

### 7.1 Error Codes

| Code | HTTP Analog | Description |
|---|---|---|
| `SESSION_NOT_FOUND` | 404 | The specified session ID does not exist |
| `FILE_NOT_FOUND` | 404 | The specified file does not exist in the session |
| `INVALID_YAML` | 400 | The content could not be parsed as valid YAML |
| `SCHEMA_VALIDATION_FAILED` | 400 | The document parsed as YAML but failed schema validation |
| `FILESYSTEM_ERROR` | 500 | An OS-level error occurred during file or directory operations |

### 7.2 Error Response Format

```json
{
  "error": {
    "code": "SESSION_NOT_FOUND",
    "message": "No session found with ID '2026-03-10-a1b2c3'",
    "path": null
  }
}
```

For schema validation errors, the `path` field contains the JSON path to the failing element:

```json
{
  "error": {
    "code": "SCHEMA_VALIDATION_FAILED",
    "message": "Field 'vibe' is required",
    "path": "$.vibe"
  }
}
```

### 7.3 Error Behavior by Tool

| Tool | Possible Errors |
|---|---|
| `create_session` | `FILESYSTEM_ERROR` |
| `write_plan` | `SESSION_NOT_FOUND`, `INVALID_YAML`, `SCHEMA_VALIDATION_FAILED`, `FILESYSTEM_ERROR` |
| `read_plan` | `SESSION_NOT_FOUND`, `FILE_NOT_FOUND`, `INVALID_YAML`, `FILESYSTEM_ERROR` |
| `list_sessions` | `FILESYSTEM_ERROR` |
| `get_session` | `SESSION_NOT_FOUND`, `FILESYSTEM_ERROR` |
| `archive_session` | `SESSION_NOT_FOUND`, `FILESYSTEM_ERROR` |

Note: `write_plan` returns `INVALID_YAML` and `SCHEMA_VALIDATION_FAILED` as non-fatal validation results (the file is still written). All other errors are fatal and prevent the operation from completing.

---

## 8. Design Philosophy

The VIBE MCP server is a document management tool, not an execution engine.

It exists to:

- give AI agents a structured way to create and organize planning documents
- validate documents against the VIBE v1 schema as they are written
- provide access to the spec, templates, and quality criteria as MCP resources
- manage planning sessions as lightweight, filesystem-based workspaces

The server intentionally does not:

- execute plans or run commands
- manage git operations
- enforce workflow ordering
- communicate with external services

This keeps the server simple, predictable, and safe to run locally.
