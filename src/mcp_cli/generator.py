"""Fetch MCP tools, render templates, write skill output."""

import json
import os
from dataclasses import dataclass
from typing import Any

import jinja2

SCRIPT_LANG_MAP = {
    "bash": {
        "template": "call_bash.sh.j2",
        "ext": "sh",
        "bin": "bash",
        "lang": "bash",
    },
    "python": {
        "template": "call_python.py.j2",
        "ext": "py",
        "bin": "python3",
        "lang": "python",
    },
    "node": {
        "template": "call_node.js.j2",
        "ext": "js",
        "bin": "node",
        "lang": "javascript",
    },
    "go": {
        "template": "call_go.go.j2",
        "ext": "go",
        "bin": "go run",
        "lang": "go",
    },
    "rust": {
        "template": "call_rust.rs.j2",
        "ext": "rs",
        "bin": "cargo run --",
        "lang": "rust",
    },
}


@dataclass
class ToolParam:
    name: str
    type: str
    required: str
    description: str


@dataclass
class ToolInfo:
    name: str
    description: str
    params: list[ToolParam]
    required_params: list[str]
    example_args: str


def parse_tool(raw: dict[str, Any]) -> ToolInfo:
    schema = raw.get("inputSchema") or {}
    props = schema.get("properties") or {}
    required_set = set(schema.get("required") or [])
    params = []
    for key, spec in props.items():
        if isinstance(spec, dict):
            params.append(ToolParam(
                name=key,
                type=spec.get("type", "any"),
                required="required" if key in required_set else "optional",
                description=(spec.get("description") or "").strip(),
            ))
        else:
            params.append(
                ToolParam(name=key, type="any", required="optional", description="")
            )
    req_params = [p.name for p in params if p.required == "required"]
    example = (
        json.dumps({k: f"<{k}>" for k in req_params}) if req_params else ""
    )
    return ToolInfo(
        name=raw.get("name", "unknown"),
        description=(raw.get("description") or "No description.").strip(),
        params=params,
        required_params=req_params,
        example_args=example,
    )


def _get_env() -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.PackageLoader("mcp_cli", "templates"),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def generate_skill(
    server_name: str,
    raw_tools: list[dict[str, Any]],
    output_dir: str,
    script: str = "bash",
    multi_skills: bool = False,
) -> str | list[str]:
    env = _get_env()
    tools = [parse_tool(t) for t in raw_tools]
    lang_cfg = SCRIPT_LANG_MAP[script]

    if multi_skills:
        generated_dirs = []
        for tool in tools:
            out_dir = os.path.join(output_dir, f"{server_name}-{tool.name}")
            scripts_dir = os.path.join(out_dir, "scripts")
            os.makedirs(scripts_dir, exist_ok=True)
            skill_path = os.path.abspath(out_dir)

            skill_md = env.get_template("skill_single.md.j2").render(
                server_name=server_name,
                tool=tool,
                skill_path=skill_path,
                script_lang=lang_cfg["lang"],
                script_bin=lang_cfg["bin"],
                script_ext=lang_cfg["ext"],
            )
            with open(os.path.join(out_dir, "SKILL.md"), "w") as f:
                f.write(skill_md)

            call_content = env.get_template(lang_cfg["template"]).render(
                server_name=server_name
            )
            call_filename = f"call.{lang_cfg['ext']}"
            call_path = os.path.join(scripts_dir, call_filename)
            with open(call_path, "w") as f:
                f.write(call_content)
            os.chmod(call_path, 0o755)

            generated_dirs.append(out_dir)

        return generated_dirs
    else:
        tool_names = ", ".join(t.name for t in tools)
        out_dir = os.path.join(output_dir, server_name)
        scripts_dir = os.path.join(out_dir, "scripts")
        os.makedirs(scripts_dir, exist_ok=True)
        skill_path = os.path.abspath(out_dir)

        skill_md = env.get_template("skill.md.j2").render(
            server_name=server_name,
            tools=tools,
            tool_names=tool_names,
            skill_path=skill_path,
            script_lang=lang_cfg["lang"],
            script_bin=lang_cfg["bin"],
            script_ext=lang_cfg["ext"],
        )
        with open(os.path.join(out_dir, "SKILL.md"), "w") as f:
            f.write(skill_md)

        call_content = env.get_template(lang_cfg["template"]).render(
            server_name=server_name
        )
        call_filename = f"call.{lang_cfg['ext']}"
        call_path = os.path.join(scripts_dir, call_filename)
        with open(call_path, "w") as f:
            f.write(call_content)
        os.chmod(call_path, 0o755)

        return out_dir
