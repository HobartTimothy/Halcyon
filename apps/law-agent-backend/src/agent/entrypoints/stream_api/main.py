"""ASGI entrypoint for SSE connections."""

from agent.entrypoints.stream_api.app_factory import create_stream_app

app = create_stream_app()
