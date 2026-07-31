from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp import Context
import sqlite3
import time
from jsonschema import validate
import os

from . import mcp
from . import tools
from . import resources
from . import prompts
from . import notifications

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB = os.path.join(BASE_DIR, "db", "hotel.db")


# DATABASE
          
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
    print(mcp.list_tools())
    print("Starting Aurelia Hotel MCP Server...")

    mcp.run(transport="streamable-http")