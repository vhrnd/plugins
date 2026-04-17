# AI Uninstall Instructions: LMS Review Personal Plugin

Remove this plugin from the current user's personal Codex setup.

Target objects:

- plugin name: `lms-review`
- bundled skill: `skills/lms-review`
- MCP server name: `vh-lms-mcp`
- personal plugin folder: `~/.codex/plugins/lms-review`
- personal marketplace file: `~/.agents/plugins/marketplace.json`
- global Codex config: `~/.codex/config.toml`

## Required behavior

Perform the uninstall directly. Do not just describe it.

- Remove only `lms-review` and `vh-lms-mcp`
- Preserve unrelated marketplace entries, plugins, skills, and MCP servers
- Remove both the source plugin folder and any installed cache copies for this plugin

## Uninstall steps

### 1. Remove the personal marketplace entry

Open `~/.agents/plugins/marketplace.json` and remove the plugin entry whose `name` is `lms-review`.

Rules:

- preserve all unrelated entries
- do not rewrite the file into a new shape unless needed
- if the file becomes empty, it may still remain as a valid marketplace file

### 2. Remove the personal plugin source folder

Delete only:

```text
~/.codex/plugins/lms-review
```

This removes the bundled `lms-review` skill and the plugin-local `.mcp.json`.

### 3. Remove installed cache copies of this plugin

Codex installs marketplace plugins into cache directories under:

```text
~/.codex/plugins/cache/
```

Remove cache directories for `lms-review` only.

Search for matching paths such as:

```text
~/.codex/plugins/cache/*/lms-review/
```

Delete only the matching `lms-review` directories. Do not delete unrelated cache entries.

### 4. Remove plugin state and MCP config from `~/.codex/config.toml`

Remove the global MCP server block for `vh-lms-mcp` if present:

```toml
[mcp_servers.vh-lms-mcp]
url = "https://dev-mcp.vuihoc.vn/lms"
enabled = true

[mcp_servers.vh-lms-mcp.http_headers]
token = "<REAL_VUIHOC_TOKEN>"
```

Also remove any plugin state block for this plugin if present. Remove only entries for `lms-review`, for example:

```toml
[plugins."lms-review@some-marketplace"]
enabled = true
```

Rules:

- preserve unrelated `plugins.*` blocks
- preserve unrelated `mcp_servers.*` blocks
- keep valid TOML formatting

### 5. Restart Codex

Restart Codex so the marketplace and cache changes are reflected.

If you cannot restart the app directly, tell the user a restart is still required.

## Verify

The uninstall is complete only if all checks below pass:

- `~/.codex/plugins/lms-review` does not exist
- `~/.agents/plugins/marketplace.json` no longer contains a `lms-review` entry
- `~/.codex/plugins/cache/` no longer contains cache directories for `lms-review`
- `~/.codex/config.toml` no longer contains `vh-lms-mcp`
- `~/.codex/config.toml` no longer contains plugin state entries for `lms-review@...`

## Notes for the AI executing this file

- The bundled skill is removed by deleting the plugin folder and cache copies.
- Do not uninstall other plugins from the same marketplace.
- Do not claim success until the verification checks pass.
