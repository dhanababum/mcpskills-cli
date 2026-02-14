---
name: dellstore
description: MCP tools for dellstore. Available tools: list_tables, get_table_schema, execute_query, test_connection. Use when the user needs to call these MCP tools.
---

# dellstore MCP Tools



## Tables

**categories** — category (int PK), categoryname (varchar 50)

**cust_hist** — customerid (int, FK→customers.customerid), orderid (int), prod_id (int)

**customers** — customerid (int PK), firstname, lastname, address1, address2 (nullable), city, state (nullable), zip (int, nullable), country, region (smallint), email (nullable), phone (nullable), creditcardtype (int), creditcard, creditcardexpiration, username (unique), password, age (smallint, nullable), income (int, nullable), gender (varchar 1, nullable) — all strings varchar 50 unless noted

**inventory** — prod_id (int PK), quan_in_stock (int), sales (int)

**orderlines** — orderlineid (int), orderid (int, FK→orders.orderid), prod_id (int), quantity (smallint), orderdate (date)

**orders** — orderid (int PK), orderdate (date), customerid (int, nullable, FK→customers.customerid), netamount (numeric), tax (numeric), totalamount (numeric)

**products** — prod_id (int PK), category (int), title (varchar 50), actor (varchar 50), price (numeric), special (smallint, nullable), common_prod_id (int)

**reorder** — prod_id (int), date_low (date), quan_low (int), date_reordered (date, nullable), quan_reordered (int, nullable), date_expected (date, nullable)

## Available Tools

### list_tables

List all tables in the database.

Args:
    db_name: Identifier for the database instance (default: "default")

**Execute:**
```python
python3 /Users/dhanababu/workspace/forge-mcp-to-skills/.cursor/skills/dellstore/scripts/call.py list_tables
```

### get_table_schema

Get schema information for a specific table.

Args:
    table_name: Name of the table to inspect
    db_name: Identifier for the database instance (default: "default")

Returns:
    JSON string with table schema information

**Parameters:**
- `table_name` (string, required): -

**Execute:**
```python
python3 /Users/dhanababu/workspace/forge-mcp-to-skills/.cursor/skills/dellstore/scripts/call.py get_table_schema '{"table_name": "<table_name>"}'
```

### execute_query

Execute a SQL query with optional parameters.

This tool allows you to execute any SQL query
(SELECT, INSERT, UPDATE, DELETE, etc.)
with support for parameterized queries to prevent SQL injection.

Args:
    query: SQL query to execute
    params: Optional dictionary of parameters for parameterized queries
    db_name: Identifier for the database instance (default: "default")

Returns:
    For SELECT queries: List of dictionaries representing rows
    For INSERT/UPDATE/DELETE: List with affected_rows count

**Parameters:**
- `query` (string, required): -
- `params` (any, optional): -

**Execute:**
```python
python3 /Users/dhanababu/workspace/forge-mcp-to-skills/.cursor/skills/dellstore/scripts/call.py execute_query '{"query": "<query>"}'
```

### test_connection

Test the database connection and return connection status information.

This tool verifies that the database connection is active and returns
connection details including database type, version, and pool
configuration.

Args:

Returns:
    Dictionary with connection status, database information, and pool
    settings

**Execute:**
```python
python3 /Users/dhanababu/workspace/forge-mcp-to-skills/.cursor/skills/dellstore/scripts/call.py test_connection
```
