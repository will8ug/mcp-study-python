# MCP Weather Demo

This project demonstrates basic usages of the Model Context Protocol (MCP) with a Python server and client.

## Structure
- `mcp_server/`: MCP server exposing a weather tool (mocked response)
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
```sh
python mcp_server/server.py
```

## Running the Client
In a separate terminal (with the virtual environment activated):
```sh
python mcp_client/client.py
```

## Usage
- The client will prompt: `Enter a location to get the weather (or 'quit' to exit):`
- Type a location (e.g., `London`) and press Enter.
- The client will display a mocked weather forecast.
- Type `quit` to exit. 