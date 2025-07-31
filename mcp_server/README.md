# mcp_server

## Startup commands
```sh
uv venv
source .venv/bin/activate

uv sync
```

## Running the unit tests
```sh
PYTHONPATH=. uv run pytest server_stdio_test.py -v
```

## Running the integration tests
```sh
PYTHONPATH=. uv run pytest server_stdio_integration_test.py -v
```

## Running the SSE server
```sh
uv run python server_sse.py
```
