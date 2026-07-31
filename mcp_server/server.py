from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context

import sqlite3
import time
from jsonschema import validate

# MCP SERVER

mcp = FastMCP(
    "Aurelia Hotel Recovery Server",
    json_response=True
)

# DATABASE

DB = "db"          


def get_db():
    return sqlite3.connect(DB)


# CAPABILITY NEGOTIATION

SERVER_CAPABILITIES = {
    "tools": True,
    "resources": True,
    "prompts": True,
    "notifications": True,
    "progress": True
}


@mcp.tool()
def initialize():

    """
    Capability Negotiation
    """

    return {
        "server": "Aurelia Hotel Recovery Server",
        "version": "1.0",
        "capabilities": SERVER_CAPABILITIES
    }
if __name__ == "__main__":

    print("Starting Aurelia Hotel MCP Server...")

    mcp.run()