import os
import json
import aiohttp
from claude_agent_sdk import tool, create_sdk_mcp_server

AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID", "")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET", "")
AZURE_API_VERSION = "2023-07-01-preview"


async def _get_azure_token():
    async with aiohttp.ClientSession() as session:
        payload = {
            "grant_type": "client_credentials",
            "client_id": AZURE_CLIENT_ID,
            "client_secret": AZURE_CLIENT_SECRET,
            "resource": "https://management.azure.com/",
        }
        async with session.post(
            f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/token",
            data=payload,
        ) as resp:
            data = await resp.json()
            return data.get("access_token", "")


@tool(
    "azure_deploy_webapp",
    "Deploy a web application to Azure App Service.",
    {"resource_group": str, "app_name": str, "runtime": str},
)
async def azure_deploy_webapp(args):
    token = await _get_azure_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "location": "eastus",
        "kind": "app",
        "properties": {"serverFarmId": f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/{args['resource_group']}/providers/Microsoft.Web/serverfarms/default", "siteConfig": {"appSettings": [{"name": "WEBSITE_NODE_DEFAULT_VERSION", "value": args.get("runtime", "~18")}]}}
    }
    async with aiohttp.ClientSession() as session:
        url = f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/{args['resource_group']}/providers/Microsoft.Web/sites/{args['app_name']}?api-version={AZURE_API_VERSION}"
        async with session.put(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            return {"content": [{"type": "text", "text": json.dumps(data)}]}


@tool(
    "azure_scale_llm_endpoint",
    "Scale an Azure ML endpoint for LLM deployment.",
    {"resource_group": str, "endpoint_name": str, "instance_count": int},
)
async def azure_scale_llm_endpoint(args):
    token = await _get_azure_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"properties": {"scaleSettings": {"scaleType": "manual", "minInstances": 0, "maxInstances": args["instance_count"]}}}
    async with aiohttp.ClientSession() as session:
        url = f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/{args['resource_group']}/providers/Microsoft.MachineLearningServices/workspaces/{args['endpoint_name']}?api-version={AZURE_API_VERSION}"
        async with session.patch(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            return {"content": [{"type": "text", "text": json.dumps(data)}]}


@tool(
    "azure_list_resources",
    "List all resources in an Azure resource group.",
    {"resource_group": str},
)
async def azure_list_resources(args):
    token = await _get_azure_token()
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        url = f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/{args['resource_group']}/resources?api-version={AZURE_API_VERSION}"
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            return {"content": [{"type": "text", "text": json.dumps(data)}]}


@tool(
    "azure_delete_resource",
    "Delete an Azure resource.",
    {"resource_group": str, "resource_type": str, "resource_name": str},
)
async def azure_delete_resource(args):
    token = await _get_azure_token()
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        url = f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/{args['resource_group']}/providers/{args['resource_type']}/{args['resource_name']}?api-version={AZURE_API_VERSION}"
        async with session.delete(url, headers=headers) as resp:
            data = await resp.json() if resp.status != 204 else {"status": "deleted"}
            return {"content": [{"type": "text", "text": json.dumps(data)}]}


azure_server = create_sdk_mcp_server(
    name="azure",
    tools=[
        azure_deploy_webapp,
        azure_scale_llm_endpoint,
        azure_list_resources,
        azure_delete_resource,
    ],
)
