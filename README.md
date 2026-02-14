# mcpskills-cli

Generate Agent Skills from MCP server tools. Connects via Streamable HTTP, discovers tools, and outputs a skill with schema docs and a call script in the language of your choice.

## Why bake MCP into skills?

Skills are easy to understand, static, edit, and most coding and non-coding agents are adopting them. Traditional MCPs load all tools into context and pollute the agent; token penalty is also costly because of loading every tool. This is why we transform MCP into skills: skills reduce token consumption because the agent does not load all skills into context—it only loads them when necessary.

## But why do we even need MCP?

MCP is a standardized protocol for AI agents to communicate. Because of this, any system can easily adopt it and create the necessary tools specific to their needs.

## Install

```bash
pip install mcpskills-cli
# or for development:
pip install -e .
```

## Usage

```bash
mcpskills-cli --url <MCP_SERVER_URL> --token <TOKEN> [--name <NAME>] [--output <DIR>] [--script <LANG>] [--multi-skills]
```

| Flag | Default | Description |
|---|---|---|
| `--url` | (required) | MCP server endpoint |
| `--token` | (required) | Bearer token |
| `--name` | from URL | Server name (skill dir + credentials key) |
| `--output` | `~/.cursor/skills` | Skills output directory |
| `--script` | `bash` | Call script language: `bash`, `python`, `node`, `go`, `rust` |
| `--multi-skills` | `false` | Generate a separate skill for each tool |

### Examples

```bash
# Generate single skill with all tools (default)
mcpskills-cli --url http://localhost:8027/mcp/abc123 --token mytoken --name my-db

# Generate separate skill for each tool
mcpskills-cli --url http://localhost:8027/mcp/abc123 --token mytoken --name my-db --multi-skills

# Generate with Python call script
mcpskills-cli --url http://localhost:8027/mcp/abc123 --token mytoken --name my-db --script python

# Generate with Node.js call script
mcpskills-cli --url http://localhost:8027/mcp/abc123 --token mytoken --name my-db --script node
```

## Credentials

Stored in `~/.mcps/credentials` (INI format, `chmod 600`). One section per server, updated automatically.

```ini
[my-db]
url = http://localhost:8027/mcp/abc123/
token = mytoken
```

Rotate tokens by editing the file directly; no need to regenerate skills.

## Generated Output

### Default Mode (Single Skill)

```
~/.cursor/skills/<server-name>/
  SKILL.md              # Documents all tools with parameters
  scripts/
    call.<ext>          # Calls any tool: ./call.<ext> <tool_name> '{"key":"val"}'
```

### Multi-Skills Mode (--multi-skills)

```
~/.cursor/skills/<server-name>-<tool-name-1>/
  SKILL.md              # Documents single tool
  scripts/
    call.<ext>          # Calls tool: ./call.<ext> <tool_name> '{"key":"val"}'

~/.cursor/skills/<server-name>-<tool-name-2>/
  SKILL.md
  scripts/
    call.<ext>
```

## Requirements

- Python >= 3.10
- `fastmcp` >= 2.3
- `jinja2` >= 3.1
