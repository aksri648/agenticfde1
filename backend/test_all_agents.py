import asyncio
import os
import sys
import json
from orchestrator import run_agent_task, build_agent_map
from config import DEFAULT_MODEL

TEST_SCENARIOS = {
    "pm": {
        "agent": "pm",
        "name": "Project Manager Agent",
        "prompt": "We need to build and deploy a simple task manager web app with user authentication. Break this down into technical tasks and explain how you will coordinate with the other 4 agents.",
        "expected_keywords": ["Developer", "Deployer", "Maintainer", "approval"],
    },
    "developer": {
        "agent": "developer",
        "name": "App Developer Agent",
        "prompt": "Create a minimal REST API service using FastAPI with a single health check endpoint. Follow your workflow: formulate your full plan and request human approval first.",
        "expected_keywords": ["FastAPI", "workspace", "Daytona", "plan"],
    },
    "deployer": {
        "agent": "deployer",
        "name": "App Deployer Agent",
        "prompt": "Here is a repository to deploy: https://github.com/example/sample-node-app. Prepare your deployment plan and request approval according to your strict workflow.",
        "expected_keywords": ["Render", "plan", "approval", "deploy"],
    },
    "maintainer": {
        "agent": "maintainer",
        "name": "App Maintainer Agent",
        "prompt": "We received an issue report for https://github.com/example/sample-node-app stating the /api/status endpoint is 500 erroring. Formulate your troubleshooting and maintenance plan.",
        "expected_keywords": ["Daytona", "plan", "approval", "clone"],
    },
    "llm_deployer": {
        "agent": "llm_deployer",
        "name": "LLM Deployer Agent",
        "prompt": "I want to deploy Qwen 2.5 7B for low latency inference. Outline the deployment plan with GPU selection and vLLM configuration.",
        "expected_keywords": ["vLLM", "RunPod", "GPU", "plan"],
    },
}

async def run_single_agent(key: str, scenario: dict):
    print("=" * 60)
    print(f"TESTING AGENT: {scenario['name']} ({key})")
    print(f"Prompt: {scenario['prompt']}")
    print("=" * 60)

    agent_map = build_agent_map()
    agent_options = agent_map[scenario["agent"]]
    
    events_received = []
    text_chunks = []
    tools_called = []
    
    try:
        async for event in run_agent_task(agent_options, scenario["prompt"]):
            etype = event.get("type")
            events_received.append(etype)
            
            if etype == "text":
                text_chunks.append(event.get("content", ""))
            elif etype == "tool_use":
                tools_called.append(event.get("tool"))
                print(f"  -> [TOOL USE] {event.get('tool')}")
            elif etype == "interrupt":
                print(f"  -> [HITL INTERRUPT] Plan: {event.get('plan')[:100]}...")
            elif etype == "log":
                print(f"  -> [LOG] {event.get('content')}")
            elif etype == "result":
                print(f"  -> [RESULT] Subtype: {event.get('subtype')}")

        full_text = "".join(text_chunks)
        print(f"\nResponse preview ({len(full_text)} chars):\n{full_text[:300]}...\n")
        print(f"Tools called: {tools_called}")
        
        found_keywords = [kw for kw in scenario["expected_keywords"] if kw.lower() in full_text.lower()]
        print(f"Keywords verified: {found_keywords} / {scenario['expected_keywords']}")
        print(f"STATUS: SUCCESS\n")
        return True
    except Exception as e:
        print(f"STATUS: FAILED with error: {e}\n")
        return False

async def main():
    target = sys.argv[1] if len(sys.argv) > 1 else "all"
    print(f"Running Agent Suite on 9 Router | Model: {DEFAULT_MODEL}")
    
    if target == "all":
        for k, v in TEST_SCENARIOS.items():
            await run_single_agent(k, v)
    elif target in TEST_SCENARIOS:
        await run_single_agent(target, TEST_SCENARIOS[target])
    else:
        print(f"Unknown target {target}. Choose from: {list(TEST_SCENARIOS.keys())}")

if __name__ == "__main__":
    asyncio.run(main())
