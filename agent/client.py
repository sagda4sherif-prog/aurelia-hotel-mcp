import asyncio

from mcp import ClientSession
from mcp.client.stdio import stdio_client

from agent.transport import create_server_parameters
from agent.handshake import perform_handshake, validate_server


async def main():
    server_params = create_server_parameters()

    async with stdio_client(server_params) as (read_stream, write_stream):

        async with ClientSession(read_stream, write_stream) as session:

            result = await perform_handshake(session)
            validate_server(result)

            print(result.serverInfo)
            print(result.capabilities)


if __name__ == "__main__":
    asyncio.run(main())