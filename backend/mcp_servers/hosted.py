import os
from config import HOSTED_MCP


def get_hosted_mcp_config(server_name: str) -> dict:
    """Return MCP config dict for a hosted HTTP/SSE server with auth headers."""
    url = HOSTED_MCP.get(server_name)
    if not url:
        raise ValueError(f"Unknown hosted MCP server: {server_name}")

    config: dict = {"type": "http", "url": url}

    # GitHub MCP requires a PAT bearer token
    if server_name == "github":
        token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")
        if token:
            config["headers"] = {"Authorization": f"Bearer {token}"}

    # Stitch MCP requires API key as X-Goog-Api-Key header
    if server_name == "stitch":
        api_key = os.getenv("STITCH_API_KEY", "")
        if api_key:
            config["headers"] = {"X-Goog-Api-Key": api_key}

    return config
