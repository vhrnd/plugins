# AI Install Instructions: LMS Review Personal Plugin

Follow the personal plugin flow from OpenAI Codex plugin docs:
[Build plugins](https://developers.openai.com/codex/plugins/build?install-scope=global)

## Goal

Install this plugin as a personal Codex plugin for the current user.

This install must cover all three parts:

- personal marketplace registration
- bundled skill installation
- MCP availability with a real VUIHOC token

Target plugin:

- plugin name: `lms-review`
- MCP server name: `vh-lms-mcp`
- MCP URL: `https://dev-mcp.vuihoc.vn/lms`
- source plugin folder: `<REPO_ROOT>/plugins/lms-review`
- personal plugin folder: `~/.codex/plugins/lms-review`
- personal marketplace file: `~/.agents/plugins/marketplace.json`
- global Codex config: `~/.codex/config.toml`

## Required input

You need a real VUIHOC token.

- If the token is already available from the user or environment, use it.
- If the token is missing, ask the user once.
- Never invent a token.
- Never leave `<YOUR_VUIHOC_TOKEN>` in a completed install.

## Required behavior

Perform the install directly. Do not just explain it.

- Preserve unrelated plugins, marketplace entries, and MCP servers.
- Only modify `lms-review` and `vh-lms-mcp`.
- Do not edit Codex plugin cache by hand as the primary install path.
- Use the personal marketplace path from the OpenAI docs, not the repo marketplace path.

## Install steps

### 1. Resolve and validate the source plugin

Resolve `<REPO_ROOT>` from the location of this file, then validate that:

- `<REPO_ROOT>/plugins/lms-review/.codex-plugin/plugin.json` exists
- `<REPO_ROOT>/plugins/lms-review/skills/lms-review/SKILL.md` exists
- `<REPO_ROOT>/plugins/lms-review/.mcp.json` exists

Stop if those files are missing.

### 2. Copy the plugin into the personal plugin directory

Make the installed source match the repo version:

- create `~/.codex/plugins` if missing
- replace only `~/.codex/plugins/lms-review`
- copy `<REPO_ROOT>/plugins/lms-review` to `~/.codex/plugins/lms-review`

After copying, verify these files exist:

- `~/.codex/plugins/lms-review/.codex-plugin/plugin.json`
- `~/.codex/plugins/lms-review/skills/lms-review/SKILL.md`
- `~/.codex/plugins/lms-review/.mcp.json`

This copied plugin folder is what the personal marketplace should point to. The bundled skill lives inside this folder and must remain there.

### 3. Add or update the personal marketplace entry

Create or update `~/.agents/plugins/marketplace.json`.

If the file does not exist, create it.

Ensure it contains a plugin entry for `lms-review` with this exact structure:

```json
{
  "name": "lms-review",
  "source": {
    "source": "local",
    "path": "./.codex/plugins/lms-review"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Productivity"
}
```

Rules for editing the marketplace file:

- preserve unrelated plugin entries
- do not duplicate `lms-review`
- keep `source.path` relative to the marketplace root
- use `./.codex/plugins/lms-review`
- if top-level `name` is missing, set it to `personal-plugins`
- if top-level `interface.displayName` is missing, set it to `Personal Plugins`

### 4. Configure MCP for immediate use

The plugin bundles `.mcp.json`, but this plugin also requires a real token to work immediately in Codex.

Do both of the following:

1. Update `~/.codex/plugins/lms-review/.mcp.json`
2. Upsert the global MCP block in `~/.codex/config.toml`

Set the token in `~/.codex/plugins/lms-review/.mcp.json` so the bundled MCP config is no longer using the placeholder.

Expected `.mcp.json` content shape:

```json
{
  "mcpServers": {
    "vh-lms-mcp": {
      "disabled": false,
      "type": "http",
      "headers": {
        "token": "<REAL_VUIHOC_TOKEN>"
      },
      "url": "https://dev-mcp.vuihoc.vn/lms"
    }
  }
}
```

Also ensure `~/.codex/config.toml` contains this block:

```toml
[mcp_servers.vh-lms-mcp]
url = "https://dev-mcp.vuihoc.vn/lms"
enabled = true

[mcp_servers.vh-lms-mcp.http_headers]
token = "<REAL_VUIHOC_TOKEN>"
```

When editing `~/.codex/config.toml`:

- replace the existing `vh-lms-mcp` block if present
- do not modify unrelated MCP servers
- keep valid TOML formatting

If you prefer automation, you may run:

```bash
python3 ~/.codex/plugins/lms-review/scripts/install_codex_mcp.py --token "<REAL_VUIHOC_TOKEN>"
```

That script only updates the `vh-lms-mcp` block in `~/.codex/config.toml`.

### 5. Restart Codex

Restart Codex after the marketplace and MCP changes.

If you cannot restart the app directly, tell the user a restart is required to finish loading the personal marketplace and plugin changes.

## Verify

The install is complete only if all checks below pass:

- `~/.codex/plugins/lms-review/.codex-plugin/plugin.json` exists
- `~/.codex/plugins/lms-review/skills/lms-review/SKILL.md` exists
- `~/.codex/plugins/lms-review/.mcp.json` exists and does not contain `<YOUR_VUIHOC_TOKEN>`
- `~/.agents/plugins/marketplace.json` contains exactly one `lms-review` entry pointing to `./.codex/plugins/lms-review`
- `~/.codex/config.toml` contains `mcp_servers.vh-lms-mcp`
- after restart, Codex can see the plugin in the personal marketplace

## Notes for the AI executing this file

- The skill is bundled inside the plugin. Do not install it separately somewhere else.
- The MCP config is bundled inside the plugin, but the global config upsert is still required for a reliable setup on this plugin.
- Do not remove or rewrite unrelated personal plugins.
- Do not claim success until the verification checks pass.
