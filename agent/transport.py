from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any, Callable

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamable_http_client

from agent.config import AgentConfig, TransportMode

GetSessionId = Callable[[], "str | None"]


@asynccontextmanager
async def open_transport(
    config: AgentConfig,
) -> AsyncGenerator[tuple[Any, Any, GetSessionId], None]:
    """Provide transport streams (read, write, get_session_id) based on configuration."""

    if config.transport_mode is TransportMode.STDIO:
        params = StdioServerParameters(
            command=config.stdio_command,
            args=list(config.stdio_args),
        )
        print(
            f"[transport] stdio mode -> spawning: "
            f"{config.stdio_command} {' '.join(config.stdio_args)}"
        )
        async with stdio_client(params) as (read, write):
            yield read, write, (lambda: None)
        return

    if config.transport_mode is TransportMode.HTTP:
        assert config.http_url, "HTTP transport requires AgentConfig.http_url"
        print(f"[transport] Streamable HTTP mode -> {config.http_url}")
        async with streamable_http_client(
            config.http_url,
            headers=config.http_headers or None,
        ) as (read, write, get_session_id):
            yield read, write, get_session_id
        return

    raise ValueError(f"Unsupported transport mode: {config.transport_mode!r}")