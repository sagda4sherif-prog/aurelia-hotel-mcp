from mcp import ClientSession
from agent.config import (
    CLIENT_NAME,
    CLIENT_VERSION,
    PROTOCOL_VERSION,
)


async def perform_handshake(session: ClientSession):
    """
    Initialize the MCP connection and negotiate capabilities.
    """

    result = await session.initialize()

    print("Handshake completed successfully.")

    return result


def validate_server(result):
    capabilities = result.capabilities

    if capabilities.tools is None:
        raise RuntimeError("Server does not support tools.")

    print("Server validation passed.")