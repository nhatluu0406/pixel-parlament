import json
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from app.orchestrator.state import AgentState
from app.core.skills.registry import SkillRegistry
from app.services.soul_manager import SoulManager
from app.core.llm import ModelFactory
from app.api.websocket import manager

soul_manager = SoulManager()

from app.db.database import SessionLocal
from app.db.models import Agent

async def update_agent_status(agent_id: str, status: str):
    db = SessionLocal()
    try:
        if agent_id.isdigit():
            agent = db.query(Agent).filter(Agent.id == int(agent_id)).first()
            if agent:
                agent.status = status
                db.commit()
    finally:
        db.close()

async def manager_node(state: AgentState) -> dict:
    messages = state["messages"]
    
    workers_info = ""
    worker_map = {}
    for w in state["active_workers"]:
        workers_info += f"- {w['name']} (ID: {w['id']}, Role: {w['role']})\n"
        worker_map[str(w['id'])] = w['name']

    system_prompt = f"""You are 'The Director', the manager of a pixel-art agentic office.
Your task is to talk to the user and decide if their request requires delegating a task to a worker.

ACTIVE WORKERS:
{workers_info}

INSTRUCTIONS:
1. If the user is just chatting, respond politely as The Director.
2. If the user wants to perform an action (e.g. create a file, search web), identify the best worker and the task description.
3. If the user wants to delete an agent, identify the target agent ID.

RESPONSE FORMAT (JSON ONLY):
{{
    "type": "chat" | "task" | "delete",
    "response": "Your conversational response to the user",
    "assigned_worker_id": "ID of worker if task",
    "target_delete_id": "ID of agent if delete",
    "task_description": "Detailed task for the worker"
}}
"""
    
    try:
        llm_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            llm_messages.append({"role": role, "content": msg.content})
            
        res = await ModelFactory.generate(llm_messages, response_format={"type": "json_object"})
        data = json.loads(res.choices[0].message.content)
        
        await manager.broadcast({
            "agent_id": "The Director",
            "action": "MANAGER_RESPONSE",
            "message": data["response"],
            "sprite_state": "idle"
        })
        
        target_agent_id = data.get("assigned_worker_id")
        target_delete = data.get("target_delete_id")
        
        new_messages = []
        if data["type"] == "task" and target_agent_id:
            agent_name = worker_map.get(str(target_agent_id), f"Agent {target_agent_id}")
            task_desc = data.get("task_description", "No description")
            
            await manager.broadcast({
                "agent_id": "The Director",
                "action": "ROUTING",
                "message": f"Giao việc cho {agent_name}: {task_desc}",
                "sprite_state": "idle"
            })
            new_messages.append(AIMessage(content=f"Director's Order: {task_desc}"))
            
        return {
            "current_agent": target_agent_id,
            "target_agent_to_delete": target_delete,
            "messages": new_messages
        }
        
    except Exception as e:
        print(f"Manager Error: {e}")
        return {"current_agent": None, "target_agent_to_delete": None}

async def worker_node(state: AgentState) -> dict:
    current_agent_id = str(state.get("current_agent"))
    if not current_agent_id:
        return {"messages": [AIMessage(content="No worker assigned.")]}
    
    # Persist Status: Working
    await update_agent_status(current_agent_id, "working")
        
    await manager.broadcast({
        "agent_id": current_agent_id,
        "action": "WORKING",
        "message": f"Đang thực hiện nhiệm vụ...",
        "sprite_state": "working"
    })
    
    tools = SkillRegistry.get_all_tools()
    tool_schemas = []
    for t in tools:
        tool_schemas.append({
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": {
                    "type": "object",
                    "properties": t.args,
                    "required": list(t.args.keys())
                }
            }
        })

    sys_msg_content = soul_manager.generate_system_message(current_agent_id, "Use your tools to fulfill the Director's request.")
    
    api_messages = [{"role": "system", "content": sys_msg_content}]
    for msg in state["messages"]:
        role = "user" if isinstance(msg, (HumanMessage, AIMessage)) else "assistant"
        api_messages.append({"role": role, "content": msg.content})

    try:
        response = await ModelFactory.generate(api_messages, tools=tool_schemas)
        msg = response.choices[0].message
        
        if msg.tool_calls:
            for tc in msg.tool_calls:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments)
                tool_func = next((t for t in tools if t.name == fn_name), None)
                if tool_func:
                    result = tool_func.invoke(fn_args)
                    api_messages.append(msg)
                    api_messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": fn_name,
                        "content": str(result)
                    })
            
            final_res = await ModelFactory.generate(api_messages)
            output_content = final_res.choices[0].message.content
        else:
            output_content = msg.content

        # Persist Status: Idle
        await update_agent_status(current_agent_id, "idle")

        await manager.broadcast({
            "agent_id": current_agent_id,
            "action": "DONE",
            "message": output_content,
            "sprite_state": "idle"
        })
        return {"messages": [AIMessage(content=output_content)]}

    except Exception as e:
        print(f"Worker Error: {e}")
        await update_agent_status(current_agent_id, "idle")
        return {"messages": [AIMessage(content=f"Error: {str(e)}")]}

async def consensus_node(state: AgentState) -> dict:
    return {"messages": [AIMessage(content="Voting session initiated.")]}
