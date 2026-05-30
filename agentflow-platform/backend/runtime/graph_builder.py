from typing import Annotated, TypedDict, List, Dict, Any
import json
from langgraph.graph import StateGraph, END
from .gemini_llm import GeminiLLM
from .tools import AVAILABLE_TOOLS
from .memory import AgentMemory
from routers.websocket import manager

class AgentState(TypedDict):
    messages: List[Dict[str, str]]
    next_node: str
    run_id: str
    workflow_config: Dict[str, Any]
    total_tokens: int # NEW

def build_workflow_graph(workflow_config: Dict[str, Any], agent_data: Dict[str, Any]):
    """
    Dynamically builds a LangGraph StateGraph from the workflow configuration.
    """
    workflow = StateGraph(AgentState)

    async def run_agent_node(state: AgentState, node_id: str, agent_id: str):
        agent = agent_data.get(agent_id)
        if not agent:
            return {"next_node": END}

        await manager.broadcast(json.dumps({
            "type": "log",
            "run_id": state["run_id"],
            "message": f"Agent {agent['name']} is thinking..."
        }))

        llm = GeminiLLM(
            model_name=agent.get("model_settings", {}).get("model", "gemini-3.1-flash-lite"),
            temperature=agent.get("model_settings", {}).get("temperature", 0.7)
        )

        # Add a small delay so the user can see the "Thinking" state in the UI
        import asyncio
        await asyncio.sleep(1.5)
        
        # Inject current date into the system prompt (Adjusted for IST: UTC+5:30)
        from datetime import datetime, timedelta, timezone
        ist_time = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
        current_date = ist_time.strftime("%B %d, %Y")
        current_time_str = ist_time.strftime("%I:%M %p")
        
        # Load agent memory if it exists
        agent_memory = ""
        try:
            import sqlite3
            from database import DB_PATH
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute("SELECT memory_context FROM agent_memory WHERE agent_id = ?", (agent_id,)).fetchone()
                if row: agent_memory = f"\n\nLONG-TERM MEMORY: {row['memory_context']}"
        except: pass

        # Enhanced instructions for tool usage
        tool_list = agent.get("tools") or []
        if isinstance(tool_list, str):
            try:
                tool_list = json.loads(tool_list)
            except:
                tool_list = []
        
        tool_instruction = ""
        if tool_list and isinstance(tool_list, list):
            tool_instruction = f"\n\nCRITICAL: You have access to the following tools: {', '.join([str(t) for t in tool_list])}. " \
                               f"If the user provides a link (YouTube, URL, etc.), you MUST use the corresponding tool " \
                               f"to retrieve the data before responding. Do not use your internal knowledge for external links."

        enhanced_system_prompt = f"Current Date: {current_date}. Current Time (IST): {current_time_str}. {agent['system_prompt']}{tool_instruction}{agent_memory}"

        # Ensure role alternation and clear handover
        messages = state["messages"]
        
        # Enhanced Logging: Print the exact input being sent to the agent
        print(f"DEBUG: Agent {agent['name']} receiving {len(messages)} messages. Last: {messages[-1]['content'][:100]}...")

        # If the last message is from an assistant, add a small user bridge to prompt the next agent
        current_history = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            # Crucial: If content is missing, use a placeholder to avoid API errors
            content = msg.get("content") or msg.get("message") or "[Empty Message]"
            current_history.append({"role": role, "content": content})
        
        # If the last message was a model response, we need a user message to trigger the next agent
        if current_history and current_history[-1]["role"] == "model":
            # For the Image Generator, we want to pass the data directly
            last_content = current_history[-1]["content"]
            current_history.append({
                "role": "user", 
                "content": last_content
            })

        # Logic to include tools and memory would go here
        response, tokens = await llm.generate_response(enhanced_system_prompt, current_history, run_id=state["run_id"])
        
        # Update agent memory with the new response (simple last-resort memory)
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute("INSERT OR REPLACE INTO agent_memory (agent_id, memory_context) VALUES (?, ?)", 
                             (agent_id, str(response)[:500]))
                conn.commit()
        except: pass

        # Ensure the response is a string and not empty
        if not response:
            response = "[The agent completed the task but provided no visible output text.]"
        
        new_messages = messages + [{"role": "assistant", "content": str(response), "sender_name": agent["name"]}]
        
        # Explicitly broadcast that this agent is SENDING its response
        await manager.broadcast(json.dumps({
            "type": "log",
            "run_id": state["run_id"],
            "message": f"✅ Agent {agent['name']} has finished and is delivering result..."
        }))
        
        await manager.broadcast(json.dumps({
            "type": "message",
            "run_id": state["run_id"],
            "role": "assistant",
            "sender": agent["name"],
            "content": str(response)
        }))
        
        # Determine next node based on edges
        edges = state["workflow_config"].get("edges", [])
        next_node = END
        for edge in edges:
            if edge["source"] == node_id:
                next_node = edge["target"]
                break
        
        return {"messages": new_messages, "next_node": next_node, "total_tokens": state.get("total_tokens", 0) + tokens}

    # Helper to create a node function for a specific agent
    def create_agent_node(node_id: str, agent_id: str):
        async def node_func(state: AgentState):
            return await run_agent_node(state, node_id, agent_id)
        return node_func

    # Add nodes for each agent in the workflow using their node.id
    nodes = workflow_config.get("nodes", [])
    for node in nodes:
        node_id = node["id"]
        agent_id = node["data"]["agentId"]
        workflow.add_node(node_id, create_agent_node(node_id, agent_id))

    # Add edges
    edges = workflow_config.get("edges", [])
    if nodes:
        # Initial entry point
        start_node_id = nodes[0]["id"]
        workflow.set_entry_point(start_node_id)
        
        for edge in edges:
            workflow.add_edge(edge["source"], edge["target"])
            
        # Ensure all leaf nodes go to END
        node_ids = [n["id"] for n in nodes]
        sources = [e["source"] for e in edges]
        for nid in node_ids:
            if nid not in sources:
                workflow.add_edge(nid, END)

    return workflow.compile()
