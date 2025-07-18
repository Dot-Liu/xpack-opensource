from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

# Your original API app
api_app = FastAPI()
# Define your endpoints here...

# A separate app for the MCP server
mcp_app = FastAPI()

# Create MCP server from the API app
mcp = FastApiMCP(
    api_app,
    # base_url="http://api-host:8001"  # URL where the API app will be running
)

# Mount the MCP server to the separate app
mcp.mount(mcp_app)
