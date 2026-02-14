"""CLI entry point for mcpskills-cli."""

import argparse
import os
import re
import sys

from mcp_cli import credentials, client, generator

DEFAULT_OUTPUT = os.path.expanduser("~/.cursor/skills")
SCRIPT_CHOICES = list(generator.SCRIPT_LANG_MAP.keys())


def sanitize_name(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "mcp-server"


def derive_server_name(url: str) -> str:
    u = url.rstrip("/")
    if "/" in u:
        return sanitize_name(u.split("/")[-1])
    return sanitize_name(u.replace(":", "-"))


def main():
    ap = argparse.ArgumentParser(
        prog="mcpskills-cli",
        description="Generate Cursor Agent Skill from MCP server tools",
    )
    ap.add_argument("--url", required=True, help="MCP server URL (Streamable HTTP)")
    ap.add_argument("--token", required=True, help="Bearer token for auth")
    ap.add_argument("--output", default=DEFAULT_OUTPUT, help=f"Skills output dir (default: {DEFAULT_OUTPUT})")
    ap.add_argument("--name", help="Server name (default: derived from URL)")
    ap.add_argument(
        "--script",
        choices=SCRIPT_CHOICES,
        default="bash",
        help="Language for the generated call script (default: bash)",
    )
    ap.add_argument(
        "--multi-skills",
        action="store_true",
        help="Generate a separate skill for each tool",
    )
    args = ap.parse_args()

    server_name = sanitize_name((args.name or derive_server_name(args.url)).strip())
    url = args.url.rstrip("/") + "/"

    try:
        tools = client.list_tools(url, args.token)
    except Exception as e:
        print(f"Error fetching tools: {e}", file=sys.stderr)
        sys.exit(1)

    if not tools:
        print("No tools returned by server.", file=sys.stderr)
        sys.exit(1)

    credentials.save(server_name, url, args.token)
    print(f"Credentials saved to {credentials.CREDS_FILE} (chmod 600)")

    result = generator.generate_skill(
        server_name=server_name,
        raw_tools=tools,
        output_dir=os.path.expanduser(args.output),
        script=args.script,
        multi_skills=args.multi_skills,
    )
    lang_cfg = generator.SCRIPT_LANG_MAP[args.script]
    
    if args.multi_skills:
        print(f"\nSkills generated:")
        for out_dir in result:
            print(f"  {out_dir}")
    else:
        out_dir = result
        call_file = os.path.join(out_dir, "scripts", f"call.{lang_cfg['ext']}")
        print(f"Skill generated at {out_dir}")
        print(f"  SKILL.md ({len(tools)} tools)")
        print(f"  scripts/call.{lang_cfg['ext']}")
        print(f"Usage: {lang_cfg['bin']} {call_file} <tool_name> '{{}}' ")


if __name__ == "__main__":
    main()
