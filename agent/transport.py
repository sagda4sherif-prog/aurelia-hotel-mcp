from mcp import StdioServerParameters
from agent.config import SERVER_COMMAND, SERVER_ARGS


def create_server_parameters() -> StdioServerParameters:
    return StdioServerParameters(
        command=SERVER_COMMAND,
        args=SERVER_ARGS,
    )