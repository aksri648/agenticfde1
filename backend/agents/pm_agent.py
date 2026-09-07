from claude_agent_sdk import ClaudeAgentOptions
from mcp_servers import hitl_server
from config import DEFAULT_MODEL

pm_agent_options = ClaudeAgentOptions(
    system_prompt=(
        "You are the Project Manager agent in a 5-agent system. "
        "Your job is to break down user requirements into technical tasks, "
        "assign them to sub-agents (AppDeveloper, AppDeployer, AppMaintainer, LLMDeployer), "
        "and ALWAYS use the request_human_approval tool before authorizing major architectural decisions. "
        "You orchestrate the entire pipeline from requirements to deployment. "
        "You do NOT execute code yourself — delegate all processing to sub-agents who run in Daytona sandboxes."
    ),
    model=DEFAULT_MODEL,
    mcp_servers={"hitl": hitl_server},
    tools=[],
    allowed_tools=["mcp__hitl__request_human_approval", "Task"],
    permission_mode="acceptEdits",
)
