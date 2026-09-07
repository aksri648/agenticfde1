import os
import json
import aiohttp
from claude_agent_sdk import tool, create_sdk_mcp_server

DAYTONA_API_KEY = os.getenv("DAYTONA_API_KEY", "")
DAYTONA_API_URL = os.getenv("DAYTONA_API_URL", "https://api.daytona.io/v1")


@tool(
    "daytona_create_workspace",
    "Create a new Daytona development workspace/sandbox.",
    {"name": str, "image": str},
)
async def daytona_create_workspace(args):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {DAYTONA_API_KEY}", "Content-Type": "application/json"}
        payload = {"name": args["name"], "image": args.get("image", "daytona/workspace:latest")}
        async with session.post(f"{DAYTONA_API_URL}/sandbox", json=payload, headers=headers) as resp:
            try:
                data = await resp.json()
            except:
                data = {"error": "API Error", "status": resp.status, "text": await resp.text()}
            return {"content": [{"type": "text", "text": json.dumps(data)}]}


@tool(
    "daytona_start_workspace",
    "Start a stopped Daytona workspace.",
    {"workspace_id": str},
)
async def daytona_start_workspace(args):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {DAYTONA_API_KEY}"}
        async with session.post(f"{DAYTONA_API_URL}/sandbox/{args['workspace_id']}/start", headers=headers) as resp:
            try:
                data = await resp.json()
            except:
                data = {"error": "API Error", "status": resp.status, "text": await resp.text()}
            return {"content": [{"type": "text", "text": json.dumps(data)}]}


@tool(
    "daytona_stop_workspace",
    "Stop a running Daytona workspace.",
    {"workspace_id": str},
)
async def daytona_stop_workspace(args):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {DAYTONA_API_KEY}"}
        async with session.post(f"{DAYTONA_API_URL}/sandbox/{args['workspace_id']}/stop", headers=headers) as resp:
            try:
                data = await resp.json()
            except:
                data = {"error": "API Error", "status": resp.status, "text": await resp.text()}
            return {"content": [{"type": "text", "text": json.dumps(data)}]}


@tool(
    "daytona_delete_workspace",
    "Delete a Daytona workspace permanently.",
    {"workspace_id": str},
)
async def daytona_delete_workspace(args):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {DAYTONA_API_KEY}"}
        async with session.delete(f"{DAYTONA_API_URL}/sandbox/{args['workspace_id']}", headers=headers) as resp:
            try:
                data = await resp.json()
            except:
                data = {"error": "API Error", "status": resp.status, "text": await resp.text()}
            return {"content": [{"type": "text", "text": json.dumps(data)}]}


@tool(
    "daytona_list_workspaces",
    "List all Daytona workspaces.",
    {},
)
async def daytona_list_workspaces(_args):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {DAYTONA_API_KEY}"}
        async with session.get(f"{DAYTONA_API_URL}/sandbox", headers=headers) as resp:
            try:
                data = await resp.json()
            except:
                data = {"error": "API Error", "status": resp.status, "text": await resp.text()}
            return {"content": [{"type": "text", "text": json.dumps(data)}]}


@tool(
    "daytona_get_workspace",
    "Get details of a specific Daytona workspace.",
    {"workspace_id": str},
)
async def daytona_get_workspace(args):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {DAYTONA_API_KEY}"}
        async with session.get(f"{DAYTONA_API_URL}/sandbox/{args['workspace_id']}", headers=headers) as resp:
            try:
                data = await resp.json()
            except:
                data = {"error": "API Error", "status": resp.status, "text": await resp.text()}
            return {"content": [{"type": "text", "text": json.dumps(data)}]}


@tool(
    "daytona_execute_command",
    "Execute a shell command inside a running Daytona workspace. Use this for all code execution, builds, tests, and processing.",
    {"workspace_id": str, "command": str},
)
async def daytona_execute_command(args):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {DAYTONA_API_KEY}", "Content-Type": "application/json"}
        payload = {"command": args["command"]}
        async with session.post(
            f"{DAYTONA_API_URL}/sandbox/{args['workspace_id']}/execute",
            json=payload,
            headers=headers,
        ) as resp:
            try:
                data = await resp.json()
            except:
                data = {"error": "API Error", "status": resp.status, "text": await resp.text()}
            return {"content": [{"type": "text", "text": json.dumps(data)}]}


@tool(
    "daytona_create_file",
    "Create or overwrite a file inside a Daytona workspace.",
    {"workspace_id": str, "path": str, "content": str},
)
async def daytona_create_file(args):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {DAYTONA_API_KEY}", "Content-Type": "application/json"}
        payload = {"path": args["path"], "content": args["content"]}
        async with session.post(
            f"{DAYTONA_API_URL}/sandbox/{args['workspace_id']}/files",
            json=payload,
            headers=headers,
        ) as resp:
            try:
                data = await resp.json()
            except:
                data = {"error": "API Error", "status": resp.status, "text": await resp.text()}
            return {"content": [{"type": "text", "text": json.dumps(data)}]}


@tool(
    "daytona_get_file",
    "Read a file from a Daytona workspace.",
    {"workspace_id": str, "path": str},
)
async def daytona_get_file(args):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {DAYTONA_API_KEY}"}
        async with session.get(
            f"{DAYTONA_API_URL}/sandbox/{args['workspace_id']}/files/{args['path']}",
            headers=headers,
        ) as resp:
            try:
                data = await resp.json()
            except:
                data = {"error": "API Error", "status": resp.status, "text": await resp.text()}
            return {"content": [{"type": "text", "text": json.dumps(data)}]}


@tool(
    "daytona_get_preview_url",
    "Get the public preview URL for a running Daytona workspace sandbox.",
    {"workspace_id": str},
)
async def daytona_get_preview_url(args):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {DAYTONA_API_KEY}"}
        async with session.get(
            f"{DAYTONA_API_URL}/sandbox/{args['workspace_id']}/preview",
            headers=headers,
        ) as resp:
            try:
                data = await resp.json()
            except:
                data = {"error": "API Error", "status": resp.status, "text": await resp.text()}
            return {"content": [{"type": "text", "text": json.dumps(data)}]}


daytona_server = create_sdk_mcp_server(
    name="daytona",
    tools=[
        daytona_create_workspace,
        daytona_start_workspace,
        daytona_stop_workspace,
        daytona_delete_workspace,
        daytona_list_workspaces,
        daytona_get_workspace,
        daytona_execute_command,
        daytona_create_file,
        daytona_get_file,
        daytona_get_preview_url,
    ],
)
