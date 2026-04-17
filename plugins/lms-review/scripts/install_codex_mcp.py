from __future__ import annotations

import argparse
from pathlib import Path

SERVER_NAME = "vh-lms-mcp"
SERVER_URL = "https://dev-mcp.vuihoc.vn/lms"


def _toml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _server_block(token: str) -> str:
    return (
        f"[mcp_servers.{SERVER_NAME}]\n"
        f'url = "{SERVER_URL}"\n'
        "enabled = true\n\n"
        f"[mcp_servers.{SERVER_NAME}.http_headers]\n"
        f"token = {_toml_quote(token)}\n"
    )


def upsert_global_mcp_config(existing: str, token: str) -> str:
    lines = existing.splitlines()
    output: list[str] = []
    skip = False
    saw_block = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith(f"[mcp_servers.{SERVER_NAME}]"):
            if not saw_block:
                if output and output[-1] != "":
                    output.append("")
                output.extend(_server_block(token).splitlines())
                saw_block = True
            skip = True
            continue

        if skip and stripped.startswith("[") and not stripped.startswith(
            f"[mcp_servers.{SERVER_NAME}."
        ):
            skip = False

        if skip:
            continue

        output.append(line)

    if not saw_block:
        if output and output[-1] != "":
            output.append("")
        output.extend(_server_block(token).splitlines())

    return "\n".join(output).rstrip() + "\n"


def install_global_mcp(config_path: Path, token: str) -> None:
    existing = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    updated = upsert_global_mcp_config(existing, token)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(updated, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install or update the global Codex MCP config for LMS Review."
    )
    parser.add_argument("--token", required=True, help="VUIHOC token to send as MCP header")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path.home() / ".codex" / "config.toml",
        help="Path to Codex config.toml (default: ~/.codex/config.toml)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    install_global_mcp(config_path=args.config, token=args.token)
    print(f"Updated {args.config} with global MCP server '{SERVER_NAME}'.")


if __name__ == "__main__":
    main()
