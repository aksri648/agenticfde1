import asyncio
import json
import re
import socketio
from aiohttp import web
from orchestrator import run_agent_task, build_agent_map
from db import init_db, create_session, list_sessions, update_session_title, save_message, append_to_last_message, get_all_messages, save_state, get_state

init_db()

sio = socketio.AsyncServer(async_mode="aiohttp", cors_allowed_origins="*")
app = web.Application()
sio.attach(app)

agent_map = build_agent_map()

_active_daytona: dict[str, str] = {}
_current_session: dict[str, str] = {}

def send_log(socket, agent: str, message: str):
    log_data = {
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
        "agent": agent,
        "message": message,
    }
    asyncio.create_task(sio.emit("log", log_data, room=socket))

def _extract_preview_url(text: str) -> str | None:
    urls = re.findall(r'https?://[^\s"\'<>]+', text)
    for url in urls:
        if "daytona" in url or "preview" in url or "sandbox" in url:
            return url
    return None

async def _emit_session_state(sid, session_id):
    msgs = get_all_messages(session_id)
    await sio.emit("sync_history", {"messages": msgs, "sessionId": session_id}, room=sid)
    
    preview_url = get_state(session_id, "daytona_url")
    if preview_url:
        _active_daytona[sid] = preview_url
        await sio.emit("daytona_preview", preview_url, room=sid)
    else:
        _active_daytona.pop(sid, None)
        await sio.emit("daytona_preview", None, room=sid)
        
    hitl_plan = get_state(session_id, "hitl_plan")
    if hitl_plan:
        await sio.emit("hitl_request", {"plan": hitl_plan}, room=sid)
    else:
        await sio.emit("hitl_resumed", {}, room=sid)

@sio.event
async def connect(sid, environ):
    print(f"Frontend connected: {sid}")
    sessions = list_sessions()
    if not sessions:
        session_id = create_session("New Chat")
        sessions = list_sessions()
    else:
        session_id = sessions[0]["id"]
    
    _current_session[sid] = session_id
    await sio.emit("sessions_list", {"sessions": sessions}, room=sid)
    await _emit_session_state(sid, session_id)

@sio.event
async def disconnect(sid):
    print(f"Frontend disconnected: {sid}")
    _active_daytona.pop(sid, None)
    _current_session.pop(sid, None)

@sio.on("load_sessions")
async def handle_load_sessions(sid, data=None):
    sessions = list_sessions()
    await sio.emit("sessions_list", {"sessions": sessions}, room=sid)

@sio.on("create_session")
async def handle_create_session(sid, data=None):
    session_id = create_session("New Chat")
    _current_session[sid] = session_id
    
    sessions = list_sessions()
    await sio.emit("sessions_list", {"sessions": sessions}, room=sid)
    await _emit_session_state(sid, session_id)

@sio.on("switch_session")
async def handle_switch_session(sid, data):
    session_id = data.get("sessionId")
    if session_id:
        _current_session[sid] = session_id
        await _emit_session_state(sid, session_id)

@sio.on("start_task")
async def handle_start_task(sid, data):
    prompt = data.get("prompt", "")
    agent_name = data.get("agent", "pm")
    session_id = _current_session.get(sid)
    
    if not session_id:
        return
        
    # Auto-title new chats
    sessions = list_sessions()
    curr = next((s for s in sessions if s["id"] == session_id), None)
    if curr and curr["title"] == "New Chat":
        new_title = " ".join(prompt.split()[:5]) + ("..." if len(prompt.split()) > 5 else "")
        update_session_title(session_id, new_title)
        await sio.emit("sessions_list", {"sessions": list_sessions()}, room=sid)

    save_message(session_id, "user", prompt)
    send_log(sid, "System", f"Task received for {agent_name} agent: {prompt}")

    opts = agent_map.get(agent_name)
    if not opts:
        send_log(sid, "System", f"Unknown agent: {agent_name}")
        return

    try:
        current_agent_msg_started = False
        
        async for event in run_agent_task(opts, prompt):
            if event["type"] == "text":
                if not current_agent_msg_started:
                    save_message(session_id, "agent", event["content"], agent=agent_name)
                    current_agent_msg_started = True
                else:
                    append_to_last_message(session_id, agent_name, event["content"])
                    
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
                
                save_message(session_id, "tool", "", agent=agent_name, tool_name=tool_name, tool_input=tool_input)
                send_log(sid, agent_name, f"Calling tool: {tool_name}")

                await sio.emit("tool_use", {
                    "tool": tool_name,
                    "input": tool_input,
                    "agent": agent_name
                }, room=sid)

                if "request_human_approval" in tool_name:
                    plan = tool_input.get("plan", "No plan provided")
                    save_state(session_id, "hitl_plan", plan)
                    send_log(sid, "System", "Execution paused. Awaiting human approval.")
                    await sio.emit("hitl_request", {
                        "plan": plan,
                    }, room=sid)

                if "daytona_create_workspace" in tool_name:
                    ws_name = tool_input.get("name", "workspace")
                    send_log(sid, agent_name, f"Spinning up Daytona workspace: {ws_name}")

            elif event["type"] == "tool_result":
                current_agent_msg_started = False
                content = event.get("content", "")
                send_log(sid, agent_name, "Tool execution completed.")

                if isinstance(content, str):
                    preview_url = _extract_preview_url(content)
                    if preview_url and sid not in _active_daytona:
                        _active_daytona[sid] = preview_url
                        save_state(session_id, "daytona_url", preview_url)
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
    session_id = _current_session.get(sid)
    if not session_id:
        return
        
    feedback = data.get("feedback", "")
    send_log(sid, "User", f"HITL Decision: {feedback}")
    
    save_message(session_id, "user", feedback)
    save_state(session_id, "hitl_plan", "")
    
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
