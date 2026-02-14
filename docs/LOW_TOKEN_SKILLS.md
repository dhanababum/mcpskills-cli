# Auto-Generated Skills for Low Token Consumption

For questions like "show me top 10 products", token cost comes from:

1. **Skill doc reads** – agent loads multiple SKILL.md files
2. **Exploratory tool calls** – list_tables → get_table_schema → execute_query (3 round-trips)

## Recommendations

### 1. Generate a single skill (do not use `--multi-skills`)

- **One** SKILL.md that documents all MCP tools (list_tables, get_table_schema, execute_query, test_connection).
- Agent loads 1 skill instead of N → fewer tokens.
- Run: `mcpskills-cli --url <URL> --token <TOKEN> --name dellstore` (omit `--multi-skills`).

### 2. Add usage guidance in the single skill

Include a short "When to use" so the agent skips discovery when not needed:

- **Known table / clear intent** (e.g. "top 10 products") → use **execute_query** only with a `SELECT ... LIMIT` query.
- **Unknown database** → use list_tables, then get_table_schema, then execute_query.

This reduces 3 tool calls to 1 for the common case.

### 3. Optional: embed schema at generation time

If the generator can call the MCP at build time (list_tables + get_table_schema) and embed a "Known tables" section into SKILL.md, the agent gets table names and columns in one read and can go straight to execute_query. Requires a new option (e.g. `--include-schema`) and one-off MCP calls during `mcpskills-cli` run.

### 4. MCP server: high-level tools (lowest tokens)

Expose tools such as:

- `get_products(limit=10, offset=0, category=...)`  
  or  
- `query_table(table_name, limit, columns, order_by)`

Then the agent: 1 skill + 1 call. mcpskills-cli just generates the skill for that tool; no generator change.

## Summary

| Approach              | Skill reads | Tool calls (e.g. top 10 products) | Token impact   |
|-----------------------|------------|------------------------------------|----------------|
| Multi-skills (current)| 3          | 3 (list + schema + query)         | Highest        |
| Single skill          | 1          | 3                                 | Lower (docs)   |
| Single skill + guidance | 1        | 1 (execute_query only)            | Lower (docs + calls) |
| Single skill + embedded schema | 1  | 1                                 | Same as above  |
| MCP high-level tool   | 1          | 1                                 | Lowest         |

**Practical minimum for mcpskills-cli:** generate **one skill** (no `--multi-skills`) and add **usage guidance** so the agent uses execute_query directly when the intent is clear.
