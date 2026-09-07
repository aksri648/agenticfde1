import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "https://your.custom.endpoint.com/v1")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "ag/gemini-3.8-flash")

# Hosted MCP URLs (HTTP/SSE transport)
HOSTED_MCP = {
    "github": "https://api.githubcopilot.com/mcp/",
    "tavily": f"https://mcp.tavily.com/mcp/?tavilyApiKey={os.getenv('TAVILY_API_KEY', '')}",
    "runpod": "https://mcp.getrunpod.io/",
    "render": "https://mcp.render.com/mcp",
    "stitch": "https://stitch.googleapis.com/mcp",
}
