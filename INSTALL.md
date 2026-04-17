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

After installing the plugin, register the MCP globally in Codex:

```bash
python3 plugins/lms-review/scripts/install_codex_mcp.py --token "<USER_VUIHOC_TOKEN>"
```

Restart Codex. That's it — the MCP should now be available globally as `vh-lms-mcp`.

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

To update the global MCP token later, run:

```bash
python3 plugins/lms-review/scripts/install_codex_mcp.py --token "<NEW_USER_VUIHOC_TOKEN>"
```

The script is idempotent and updates only the `vh-lms-mcp` block in `~/.codex/config.toml`.

## Troubleshooting

### MCP not showing up

1. Check `~/.codex/config.toml` contains the `vh-lms-mcp` block above.
2. Make sure `enabled = true`.
3. Restart Codex after editing the config.

### Token missing

Tell the user to open:

```text
~/.codex/config.toml
```

and set:

```toml
[mcp_servers.vh-lms-mcp.http_headers]
token = "<USER_VUIHOC_TOKEN>"
```
