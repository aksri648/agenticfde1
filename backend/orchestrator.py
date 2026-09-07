import json
import asyncio
import os
from typing import AsyncGenerator
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    SystemMessage,
)

BYPASS_HITL = os.getenv("BYPASS_HITL", "0") == "1"


async def run_agent_task(
    agent_options: ClaudeAgentOptions,
    prompt: str,
    session_id: str | None = None,
) -> AsyncGenerator[dict, None]:
    """Run an agent task and yield structured events."""
    opts_dict = {
        "system_prompt": agent_options.system_prompt,
        "mcp_servers": agent_options.mcp_servers,
        "allowed_tools": agent_options.allowed_tools,
        "permission_mode": agent_options.permission_mode,
    }
    if agent_options.tools is not None:
        opts_dict["tools"] = agent_options.tools
    if agent_options.model:
        opts_dict["model"] = agent_options.model
    if session_id:
        opts_dict["session_id"] = session_id

    opts = ClaudeAgentOptions(**opts_dict)

    async for message in query(prompt=prompt, options=opts):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    yield {"type": "text", "content": block.text}
                elif hasattr(block, "name"):
                    yield {
                        "type": "tool_use",
                        "tool": block.name,
                        "input": block.input,
                    }
                elif hasattr(block, "content"):
                    content = block.content
                    # Check for HITL interrupt in tool result
                    if isinstance(content, str):
                        try:
                            parsed = json.loads(content)
                            if isinstance(parsed, dict) and parsed.get("__interrupt__"):
                                if BYPASS_HITL:
                                    yield {"type": "log", "content": "HITL bypassed — auto-approving."}
                                    continue
                                yield {
                                    "type": "interrupt",
                                    "plan": parsed.get("plan", "No plan provided"),
                                }
                                continue
                        except (json.JSONDecodeError, TypeError):
                            pass
                    yield {"type": "tool_result", "content": content}

        elif isinstance(message, SystemMessage):
            if hasattr(message, "session_id"):
                yield {"type": "session", "session_id": message.session_id}
            if hasattr(message, "subtype") and message.subtype == "init":
                mcp_servers = message.data.get("mcp_servers", []) if hasattr(message, "data") else []
                for server in mcp_servers:
                    if server.get("status") in ("failed", "needs-auth"):
                        yield {
                            "type": "mcp_error",
                            "server": server.get("name", "unknown"),
                            "status": server.get("status"),
                        }

        elif isinstance(message, ResultMessage):
            yield {
                "type": "result",
                "subtype": message.subtype,
                "result": getattr(message, "result", ""),
            }


def build_agent_map():
    """Build a mapping from agent name to its options."""
    from agents.pm_agent import pm_agent_options
    from agents.app_developer_agent import dev_agent_options
    from agents.app_deployer_agent import deployer_agent_options
    from agents.app_maintainer_agent import maintainer_agent_options
    from agents.llm_deployer_agent import llm_deployer_agent_options

    return {
        "pm": pm_agent_options,
        "developer": dev_agent_options,
        "deployer": deployer_agent_options,
        "maintainer": maintainer_agent_options,
        "llm_deployer": llm_deployer_agent_options,
    }
