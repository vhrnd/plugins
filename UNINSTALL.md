# Uninstalling LMS Review for Codex

## Goal

Remove the `LMS Review` plugin and remove the global Codex MCP server:

```toml
[mcp_servers.vh-lms-mcp]
```

If this plugin is still being published from a marketplace repository, also remove its entry from that repository's:

```text
.agents/plugins/marketplace.json
```

## Instructions

1. Remove the installed plugin cache if it exists:

```bash
rm -rf ~/.codex/plugins/cache/lms-mcp
```

2. Remove the plugin entry from:

```text
~/.codex/config.toml
```

Delete this block if present:

```toml
[plugins."lms-review@lms-mcp"]
enabled = true
```

3. Remove the global MCP entry from:

```text
~/.codex/config.toml
```

Delete these blocks if present:

```toml
[mcp_servers.vh-lms-mcp]
url = "https://dev-mcp.vuihoc.vn/lms"
enabled = true

[mcp_servers.vh-lms-mcp.http_headers]
token = "<USER_VUIHOC_TOKEN>"
```

4. Restart Codex.

5. If the plugin still appears in the Codex marketplace UI, remove its marketplace entry from the publishing repository and push that change.

Example marketplace cleanup:

```json
{
  "plugins": []
}
```

## Verify

Confirm all of the following are true:

- `~/.codex/plugins/cache/lms-mcp` does not exist
- `~/.codex/config.toml` does not contain `lms-review@lms-mcp`
- `~/.codex/config.toml` does not contain `vh-lms-mcp`
- the publishing repository no longer contains an `lms-review` entry in `.agents/plugins/marketplace.json`

## Required behavior for the AI following this file

- Prefer removing the installed artifacts directly instead of only explaining them.
- Remove only `lms-review@lms-mcp` and `vh-lms-mcp`.
- Do not modify unrelated plugins or MCP servers.
- If the task includes removing the plugin from marketplace listings, also delete the `lms-review` entry from the publishing repository's `.agents/plugins/marketplace.json`.
