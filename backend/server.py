import asyncio
import json
import re
import socketio
from aiohttp import web
from orchestrator import run_agent_task, build_agent_map
from db import init_db, save_message, append_to_last_message, get_all_messages, save_state, get_state

init_db()

sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
app = web.Application()
sio.attach(app)

agent_map = build_agent_map()

# Track active Daytona workspace per sid
_active_daytona: dict[str, str] = {}


def send_log(socket, agent: str, message: str):
    log_data = {
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        "agent": agent,
        "message": message,
    }
    asyncio.create_task(sio.emit("log", log_data, room=socket))


def _extract_preview_url(text: str) -> str | None:
    """Try to extract a Daytona preview URL from tool output."""
    urls = re.findall(r'https?://[^\s"\'<>]+', text)
    for url in urls:
        if "daytona" in url or "preview" in url or "sandbox" in url:
            return url
    return None


@sio.event
async def connect(sid, environ):
    print(f"Frontend connected: {sid}")
    # Restore messages
    msgs = get_all_messages()
    await sio.emit("sync_history", {"messages": msgs}, room=sid)
    
    # Restore preview URL if exists
    preview_url = get_state("daytona_url")
    if preview_url:
        _active_daytona[sid] = preview_url
        await sio.emit("daytona_preview", preview_url, room=sid)
        
    # Restore hitl plan if exists
    hitl_plan = get_state("hitl_plan")
    if hitl_plan:
        await sio.emit("hitl_request", {"plan": hitl_plan}, room=sid)


@sio.event
async def disconnect(sid):
    print(f"Frontend disconnected: {sid}")
    _active_daytona.pop(sid, None)


@sio.on("start_task")
async def handle_start_task(sid, data):
    prompt = data.get("prompt", "")
    agent_name = data.get("agent", "pm")
    
    # Save user message to DB
    save_message("user", prompt)
    
    send_log(sid, "System", f"Task received for {agent_name} agent: {prompt}")

    opts = agent_map.get(agent_name)
    if not opts:
        send_log(sid, "System", f"Unknown agent: {agent_name}")
        return

    try:
        # Keep track if we started an agent message to append chunks
        current_agent_msg_started = False
        
        async for event in run_agent_task(opts, prompt):
            if event["type"] == "text":
                if not current_agent_msg_started:
                    save_message("agent", event["content"], agent=agent_name)
                    current_agent_msg_started = True
                else:
                    append_to_last_message(agent_name, event["content"])
                    
                await sio.emit("message_stream", {
                    "role": "agent",
                    "agent": agent_name,
                    "content": event["content"],
                }, room=sid)
                send_log(sid, agent_name, "Streaming response...")

            elif event["type"] == "tool_use":
                current_agent_msg_started = False
                tool_name = event.get("tool", "")
                tool_input = event.get("input", {})
                
                save_message("tool", "", agent=agent_name, tool_name=tool_name, tool_input=tool_input)
                
                send_log(sid, agent_name, f"Calling tool: {tool_name}")

                await sio.emit("tool_use", {
                    "tool": tool_name,
                    "input": tool_input,
                    "agent": agent_name
                }, room=sid)

                if "request_human_approval" in tool_name:
                    plan = tool_input.get("plan", "No plan provided")
                    save_state("hitl_plan", plan)
                    send_log(sid, "System", "Execution paused. Awaiting human approval.")
                    await sio.emit("hitl_request", {
                        "plan": plan,
                    }, room=sid)

                # Detect workspace creation and emit preview
                if "daytona_create_workspace" in tool_name:
                    ws_name = tool_input.get("name", "workspace")
                    send_log(sid, agent_name, f"Spinning up Daytona workspace: {ws_name}")

            elif event["type"] == "tool_result":
                current_agent_msg_started = False
                content = event.get("content", "")
                send_log(sid, agent_name, "Tool execution completed.")

                # Detect preview URL from tool output and emit to frontend
                if isinstance(content, str):
                    preview_url = _extract_preview_url(content)
                    if preview_url and sid not in _active_daytona:
                        _active_daytona[sid] = preview_url
                        save_state("daytona_url", preview_url)
                        send_log(sid, agent_name, f"Daytona sandbox ready: {preview_url}")
                        await sio.emit("daytona_preview", preview_url, room=sid)

            elif event["type"] == "log":
                send_log(sid, agent_name, event.get("content", ""))

            elif event["type"] == "mcp_error":
                send_log(sid, "System", f"MCP server '{event['server']}' status: {event['status']}")

            elif event["type"] == "result":
                current_agent_msg_started = False
                send_log(sid, agent_name, f"Task completed: {event.get('subtype', 'success')}")
                await sio.emit("task_complete", {"agent": agent_name}, room=sid)

    except Exception as e:
        send_log(sid, "System", f"Error: {str(e)}")
        await sio.emit("error", {"message": str(e)}, room=sid)


@sio.on("hitl_response")
async def handle_hitl_response(sid, data):
    feedback = data.get("feedback", "")
    send_log(sid, "User", f"HITL Decision: {feedback}")
    
    # Save the user's feedback to the DB as well
    save_message("user", feedback)
    
    # Clear hitl plan state
    save_state("hitl_plan", "")
    
    # Resolve pending hitl futures
    try:
        from mcp_servers.hitl import pending_hitl_futures
        for fut in pending_hitl_futures.values():
            if not fut.done():
                fut.set_result(feedback)
    except Exception as e:
        print(f"Error resolving HITL future: {e}")

    await sio.emit("hitl_resumed", {"feedback": feedback}, room=sid)


async def index_handler(request):
    return web.FileResponse("./static/index.html")


app.router.add_get("/", index_handler)


if __name__ == "__main__":
    print("Starting 5-Agent System Server on port 3000")
    web.run_app(app, host="0.0.0.0", port=3000)
