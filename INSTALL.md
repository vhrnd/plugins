# Installing LMS Review for Codex

## Prerequisites

- Codex installed
- Access to this repository
- A VUIHOC token for the end user

## Installation

Install the plugin from this repository's local marketplace:

```text
lms-review@lms-mcp
```

The marketplace definition is:

```text
.agents/plugins/marketplace.json
```

The plugin ships with:

- the hosted MCP connection `vh-lms-mcp`
- the bundled skill `lms-review` for revise/practice audit workflows

After installing the plugin, register the MCP globally in Codex:

```bash
python3 plugins/lms-review/scripts/install_codex_mcp.py
```

The script will ask for the user's VUIHOC token directly in the terminal and then write it into the global Codex MCP config automatically.

If you already have the token in another scripted flow, this still works:

```bash
python3 plugins/lms-review/scripts/install_codex_mcp.py --token "<USER_VUIHOC_TOKEN>"
```

Restart Codex. The MCP should now be available globally as `vh-lms-mcp`.

After restart, Codex can also load the bundled `lms-review` skill from the plugin package.

Do not rely on editing the token only inside the plugin UI. Persist the token through the install script above so users do not need to open `~/.codex/config.toml` manually.

## Verify

Check `~/.codex/config.toml` contains:

```toml
[mcp_servers.vh-lms-mcp]
url = "https://dev-mcp.vuihoc.vn/lms"
enabled = true

[mcp_servers.vh-lms-mcp.http_headers]
token = "<USER_VUIHOC_TOKEN>"
```

If the AI does not know the user's token, it must tell the user to set it there and must not fabricate one.

## Usage

Use the global MCP `vh-lms-mcp` from Codex after restart.

If needed, verify by asking the AI to confirm that `vh-lms-mcp` is present in the global Codex MCP configuration.

## Updating

To update the global MCP token later, run the same command again:

```bash
python3 plugins/lms-review/scripts/install_codex_mcp.py
```

The script is idempotent and updates only the `vh-lms-mcp` block in `~/.codex/config.toml`. You can also keep using `--token` for scripted updates.

## Troubleshooting

### MCP not showing up

1. Check `~/.codex/config.toml` contains the `vh-lms-mcp` block above.
2. Make sure `enabled = true`.
3. Restart Codex after editing the config.

### Token missing

Tell the user to rerun:

```bash
python3 plugins/lms-review/scripts/install_codex_mcp.py
```

If a manual fix is absolutely needed, open:

```text
~/.codex/config.toml
```

and set:

```toml
[mcp_servers.vh-lms-mcp.http_headers]
token = "<USER_VUIHOC_TOKEN>"
```
