# MCP Weather Demo

This project demonstrates basic usages of the Model Context Protocol (MCP) with a Python server and client.

## Structure
- `mcp_server/`: MCP server exposing a weather tool
- `mcp_client/`: MCP client with a CLI to ask weather questions

## Setup
1. Ensure you have Python 3.13+ and [uv](https://github.com/astral-sh/uv) installed.
2. Install dependencies:
   ```sh
   uv venv
   source .venv/bin/activate
   uv pip install git+https://github.com/modelcontextprotocol/python-sdk.git
   ```

## Running the Server
Refer to [Server README](mcp_server/README.md)

## Running the Client
In a separate terminal (with the virtual environment activated):

Refer to [Client README](mcp_client/README.md)

