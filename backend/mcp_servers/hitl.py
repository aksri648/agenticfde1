import json
from claude_agent_sdk import tool, create_sdk_mcp_server


@tool(
    "request_human_approval",
    "Call this tool to pause execution and request human approval before proceeding with a plan or action.",
    {"plan": str},
)
async def request_human_approval(args):
    plan = args["plan"]
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(
                    {"__interrupt__": True, "plan": plan}
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
