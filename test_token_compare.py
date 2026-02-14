import json
import urllib.request
import tiktoken

SERVERS = {
    "dellstore": {
        "url": "http://localhost:8027/mcp/a0504710-203f-4c4b-b864-5e64641d9ed3/",
        "token": "mcp_token_bb1HbX3e-wykRQYziLNaGGYod_qhxrlffUm4DxmMn7w",
        "skill": ".cursor/skills/dellstore/SKILL.md",
    },
    "neo4j-movie": {
        "url": "http://localhost:8032/mcp/8bb059d5-0115-4c08-b994-25c26695b027/",
        "token": "mcp_token_Na7kQzvA2RxhzvAjT9P3Q0rPiaxlIHUnXiPHCoeMrhE",
        "skill": ".cursor/skills/neo4j-movie/SKILL.md",
    },
}

enc = tiktoken.encoding_for_model("gpt-4o")


def count_tokens(text: str) -> int:
    return len(enc.encode(text))


def get_mcp_tools_payload(url: str, token: str) -> str:
    body = json.dumps({
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 1,
    }).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": "2025-06-18",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode()
    for line in text.strip().split("\n"):
        if line.startswith("data:"):
            line = line[5:].strip()
        if not line or line == "[DONE]":
            continue
        try:
            obj = json.loads(line)
            if "result" in obj:
                return json.dumps(obj["result"]["tools"], indent=2)
        except json.JSONDecodeError:
            pass
    return text


def main():
    print("=" * 60)
    print("MCP Tools vs Skills — Token Comparison")
    print("=" * 60)

    mcp_payloads = {}
    skill_payloads = {}

    for name, cfg in SERVERS.items():
        print(f"\n--- {name} ---")

        mcp_json = get_mcp_tools_payload(cfg["url"], cfg["token"])
        mcp_payloads[name] = mcp_json

        with open(cfg["skill"]) as f:
            skill_md = f.read()
        skill_payloads[name] = skill_md

        mcp_tokens = count_tokens(mcp_json)
        skill_tokens = count_tokens(skill_md)
        saved = mcp_tokens - skill_tokens
        pct = (saved / mcp_tokens * 100) if mcp_tokens else 0

        print(f"  MCP JSON schema tokens : {mcp_tokens:>6}")
        print(f"  Skill markdown tokens  : {skill_tokens:>6}")
        print(f"  Savings                : {saved:>6} ({pct:.1f}%)")

    print("\n" + "=" * 60)
    print("Multi-server scenario (all servers active)")
    print("=" * 60)

    all_mcp = "\n".join(mcp_payloads.values())
    all_mcp_tokens = count_tokens(all_mcp)

    print(f"\n  Traditional MCP (all tools every turn) : {all_mcp_tokens:>6} tokens")

    for name, skill_md in skill_payloads.items():
        t = count_tokens(skill_md)
        saved = all_mcp_tokens - t
        pct = (saved / all_mcp_tokens * 100) if all_mcp_tokens else 0
        print(f"  Skill '{name}' only              : {t:>6} tokens  (saves {saved}, {pct:.1f}%)")

    all_skills = "\n".join(skill_payloads.values())
    all_skills_tokens = count_tokens(all_skills)
    saved = all_mcp_tokens - all_skills_tokens
    pct = (saved / all_mcp_tokens * 100) if all_mcp_tokens else 0
    print(f"  All skills loaded (worst case)         : {all_skills_tokens:>6} tokens  (saves {saved}, {pct:.1f}%)")


if __name__ == "__main__":
    main()
