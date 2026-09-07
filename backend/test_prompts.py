"""
4 Agent Test Prompts — verifies each agent's flow works or fails correctly.

Usage:
    python test_prompts.py              # Run all 4 tests sequentially
    python test_prompts.py developer    # Run only App Developer test
    python test_prompts.py deployer     # Run only App Deployer test
    python test_prompts.py maintainer   # Run only App Maintainer test
    python test_prompts.py llm          # Run only LLM Deployer test (should fail)
"""

import asyncio
import sys
import json
from datetime import datetime

from orchestrator import run_agent_task, build_agent_map


# ─────────────────────────────────────────────────────────────
# TEST PROMPTS
# ─────────────────────────────────────────────────────────────

TEST_PROMPTS = {
    "developer": {
        "agent": "developer",
        "prompt": (
            "Create a simple Flask hello-world app in a Daytona workspace named 'test-hello-flask'. "
            "Write a single file app.py with a route '/' that returns 'Hello World'. "
            "Install flask, run it, and give me the preview URL. "
            "After it works, upload app.py to S3 under daytona-sandbox/test-hello-flask/app.py."
        ),
        "expected_tools": [
            "mcp__hitl__request_human_approval",
            "mcp__daytona__daytona_create_workspace",
            "mcp__daytona__daytona_create_file",
            "mcp__daytona__daytona_execute_command",
            "mcp__daytona__daytona_get_preview_url",
            "mcp__s3__b2_upload_file",
        ],
        "should_succeed": True,
        "description": "App Developer: creates workspace, writes code, runs it, uploads to S3",
    },
    "deployer": {
        "agent": "deployer",
        "prompt": (
            "Deploy the GitHub repo https://github.com/maciekt07/TodoApp to Render. "
            "Use a Node.js web service, region Oregon, instance free tier. "
            "Build command: npm install && npm run build. "
            "Start command: npm start. "
            "Give me the live Render URL when done."
        ),
        "expected_tools": [
            "mcp__hitl__request_human_approval",
            "mcp__render__*",
            "mcp__github__*",
        ],
        "should_succeed": True,
        "description": "App Deployer: creates Render service, triggers deploy, shares URL",
    },
    "maintainer": {
        "agent": "maintainer",
        "prompt": (
            "Clone https://github.com/maciekt07/TodoApp into a Daytona workspace, "
            "install dependencies, run it, and add a new route '/health' that returns JSON "
            "{\"status\": \"ok\"}. Verify it works, then create a PR with the changes."
        ),
        "expected_tools": [
            "mcp__hitl__request_human_approval",
            "mcp__daytona__daytona_create_workspace",
            "mcp__daytona__daytona_execute_command",
            "mcp__daytona__daytona_create_file",
            "mcp__github__create_pull_request",
        ],
        "should_succeed": True,
        "description": "App Maintainer: clones repo, adds feature, tests, opens PR",
    },
    "llm_deployer": {
        "agent": "llm_deployer",
        "prompt": (
            "Deploy Llama 3.1 8B on RunPod using vLLM with an A10G GPU. "
            "I need a serverless endpoint. Give me the endpoint URL when ready."
        ),
        "expected_tools": [
            "mcp__hitl__request_human_approval",
            "mcp__runpod__*",
        ],
        "should_succeed": False,  # RunPod has no credits / Azure creds empty
        "expected_error": "insufficient credits",
        "description": "LLM Deployer: should fail due to insufficient RunPod credits",
    },
}


# ─────────────────────────────────────────────────────────────
# TEST RUNNER
# ─────────────────────────────────────────────────────────────

async def run_test(test_name: str) -> dict:
    """Run a single test and collect results."""
    test = TEST_PROMPTS[test_name]
    agent_map = build_agent_map()
    agent_options = agent_map.get(test["agent"])

    if not agent_options:
        return {
            "test": test_name,
            "status": "FAIL",
            "reason": f"Agent '{test['agent']}' not found in agent_map",
        }

    print(f"\n{'='*60}")
    print(f"  TEST: {test_name.upper()}")
    print(f"  {test['description']}")
    print(f"{'='*60}")
    print(f"  Prompt: {test['prompt'][:100]}...")
    print(f"  Expected to {'SUCCEED' if test['should_succeed'] else 'FAIL'}")
    print(f"{'='*60}\n")

    # Print agent config for debugging
    print(f"  [CONFIG] Model: {agent_options.model}")
    print(f"  [CONFIG] MCP servers: {list(agent_options.mcp_servers.keys())}")
    print(f"  [CONFIG] Allowed tools: {agent_options.allowed_tools}")
    print()

    collected_tools = []
    collected_text = []
    mcp_errors = []
    error_message = None
    status = "UNKNOWN"

    try:
        async for event in run_agent_task(agent_options, test["prompt"]):
            event_type = event.get("type")

            if event_type == "text":
                text = event.get("content", "")
                collected_text.append(text)
                print(f"  [TEXT] {text[:200]}{'...' if len(text) > 200 else ''}")

            elif event_type == "tool_use":
                tool_name = event.get("tool", "")
                collected_tools.append(tool_name)
                print(f"  [TOOL] {tool_name}")

            elif event_type == "tool_result":
                content = event.get("content", "")
                if isinstance(content, str) and "error" in content.lower():
                    error_message = content
                    print(f"  [TOOL ERROR] {content[:200]}")

            elif event_type == "mcp_error":
                server = event.get("server", "unknown")
                mcp_status = event.get("status", "unknown")
                mcp_errors.append({"server": server, "status": mcp_status})
                print(f"  [MCP ERROR] Server '{server}': {mcp_status}")
                if mcp_status in ("failed", "needs-auth"):
                    error_message = f"MCP server '{server}' status: {mcp_status}"

            elif event_type == "result":
                subtype = event.get("subtype", "unknown")
                result = event.get("result", "")
                print(f"  [RESULT] subtype={subtype}")
                if subtype == "error" :
                    error_message = str(result)
                    print(f"  [RESULT ERROR] {str(result)[:200]}")

    except Exception as e:
        error_message = str(e)
        print(f"  [EXCEPTION] {error_message}")

    # Determine pass/fail
    if test["should_succeed"]:
        if error_message:
            status = "FAIL"
            reason = f"Expected success but got error: {error_message[:200]}"
        elif not collected_tools:
            status = "FAIL"
            reason = "No tools were called"
        else:
            # Check if expected tools were called
            missing = [t for t in test["expected_tools"] if not any(
                t.replace("*", "") in ct for ct in collected_tools
            )]
            if missing:
                status = "WARN"
                reason = f"Missing expected tools: {missing}"
            else:
                status = "PASS"
                reason = "All expected tools called successfully"
    else:
        # Expected to fail
        if error_message:
            if any(kw in error_message.lower() for kw in ["insufficient", "credit", "auth", "forbidden", "unauthorized", "quota"]):
                status = "PASS"
                reason = f"Correctly failed: {error_message[:200]}"
            else:
                status = "WARN"
                reason = f"Failed but not with expected error: {error_message[:200]}"
        elif collected_tools:
            status = "WARN"
            reason = "Agent called tools but didn't produce expected failure"
        else:
            status = "PASS"
            reason = "Agent did not proceed (likely hit credentials check early)"

    result = {
        "test": test_name,
        "status": status,
        "reason": reason,
        "tools_called": collected_tools,
        "text_responses": len(collected_text),
        "error": error_message,
    }

    print(f"\n  >> RESULT: {status} — {reason}\n")
    return result


async def run_all_tests():
    """Run all 4 agent tests sequentially."""
    results = {}
    for test_name in TEST_PROMPTS:
        results[test_name] = await run_test(test_name)

    # Summary
    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    for name, r in results.items():
        status_icon = {"PASS": "✓", "FAIL": "✗", "WARN": "!"}.get(r["status"], "?")
        print(f"  {status_icon} {name:15s} — {r['status']:4s} — {r['reason'][:80]}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    import traceback
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"

    print(f"[DEBUG] Python path: {sys.executable}")
    print(f"[DEBUG] CWD: {__import__('os').getcwd()}")

    try:
        from config import DEFAULT_MODEL, ANTHROPIC_BASE_URL
        print(f"[DEBUG] Model: {DEFAULT_MODEL}")
        print(f"[DEBUG] Base URL: {ANTHROPIC_BASE_URL}")
    except Exception as e:
        print(f"[DEBUG] Config import error: {e}")

    try:
        if arg == "all":
            asyncio.run(run_all_tests())
        elif arg in TEST_PROMPTS:
            asyncio.run(run_test(arg))
        else:
            print(f"Unknown test: {arg}. Options: all, developer, deployer, maintainer, llm")
            sys.exit(1)
    except Exception as e:
        print(f"[FATAL] {e}")
        traceback.print_exc()
