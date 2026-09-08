import json
import os
from claude_agent_sdk import tool, create_sdk_mcp_server

BYPASS_HITL = os.getenv("BYPASS_HITL", "0") == "1"


import asyncio
import uuid

pending_hitl_futures = {}

@tool(
    "request_human_approval",
    "Call this tool to pause execution and request human approval before proceeding with a plan or action.",
    {"plan": str},
)
async def request_human_approval(args):
    plan = args["plan"]
    bypass = os.getenv("BYPASS_HITL", "0") == "1"
    if bypass:
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(
                        {"__approved__": True, "plan": plan, "decision": "Approved (auto-bypass)"}
                    ),
                }
            ]
        }
        
    loop = asyncio.get_running_loop()
    fut = loop.create_future()
    # Use a dummy global key for the single-user web UI
    pending_hitl_futures["web_ui"] = fut
    
    try:
        feedback = await fut
    finally:
        pending_hitl_futures.pop("web_ui", None)

    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(
                    {"__approved__": True, "plan": plan, "decision": feedback}
                ),
            }
        ]
    }


hitl_server = create_sdk_mcp_server(name="hitl", tools=[request_human_approval])


async def process_hitl_interrupt(plan: str) -> str:
    """Blocking console prompt for HITL (used in CLI mode)."""
    print(f"\n{'='*60}")
    print(f"  HUMAN APPROVAL REQUIRED")
    print(f"{'='*60}")
    print(f"\nPlan:\n{plan}\n")
    while True:
        decision = input("Approve / Reject / Modify: ").strip().lower()
        if decision in ("approve", "reject"):
            return "Approved. Proceed." if decision == "approve" else "Rejected. Abort."
        if decision == "modify":
            feedback = input("Enter modification instructions: ")
            return f"User modified the plan: {feedback}. Please adjust and try again."
        print("Invalid choice. Type approve, reject, or modify.")
