"""MCP client wrapper using fastmcp."""

import asyncio
from typing import Any

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


async def _list_tools(url: str, token: str) -> list[dict[str, Any]]:
    transport = StreamableHttpTransport(url, auth=token)
    async with Client(transport) as client:
        tools = await client.list_tools()
        return [t.model_dump() for t in tools]


def list_tools(url: str, token: str) -> list[dict[str, Any]]:
    return asyncio.run(_list_tools(url, token))
