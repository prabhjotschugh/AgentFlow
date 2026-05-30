import uuid
import json
import aiosqlite
from .graph_builder import build_workflow_graph
from database import DB_PATH
from routers.websocket import manager

async def execute_workflow(workflow_id: str, initial_message: str, trigger_source: str = "manual"):
    run_id = str(uuid.uuid4())
    
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            
            # 1. Load Workflow
            async with db.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,)) as cursor:
                wf_row = await cursor.fetchone()
                if not wf_row:
                    await manager.broadcast(json.dumps({"type": "error", "message": "Workflow not found"}))
                    return {"error": "Workflow not found"}
                wf_config = json.loads(wf_row["config"])

            # 2. Load all agents involved
            agent_data = {}
            async with db.execute("SELECT * FROM agents") as cursor:
                rows = await cursor.fetchall()
                for row in rows:
                    agent_data[row["id"]] = {
                        "name": row["name"],
                        "role": row["role"],
                        "system_prompt": row["system_prompt"],
                        "tools": json.loads(row["tools"] or "[]"),
                        "model_settings": json.loads(row["model_settings"] or "{}")
                    }

            # 3. Create Run record
            await db.execute(
                "INSERT INTO runs (id, workflow_id, status, trigger_source) VALUES (?, ?, ?, ?)",
                (run_id, workflow_id, "running", trigger_source)
            )
            
            # 4. Save initial user message
            await db.execute(
                "INSERT INTO messages (run_id, role, content) VALUES (?, ?, ?)",
                (run_id, "user", initial_message)
            )
            await db.commit()

            await manager.broadcast(json.dumps({
                "type": "log", 
                "run_id": run_id, 
                "message": f"Starting workflow {wf_row['name']}..."
            }))

            # 5. Build and Run Graph
            graph = build_workflow_graph(wf_config, agent_data)
            
            # Initial state
            state = {
                "messages": [{"role": "user", "content": initial_message}],
                "run_id": run_id,
                "workflow_config": wf_config,
                "total_tokens": 0 # NEW
            }

            # Invoke graph
            result = await graph.ainvoke(state)
            
            # 6. Persist final results (already broadcasted by nodes, just saving to DB)
            final_messages = result["messages"]
            for msg in final_messages:
                if msg["role"] == "assistant":
                    # Check if message already exists to avoid duplicates
                    async with db.execute(
                        "SELECT id FROM messages WHERE run_id = ? AND content = ? AND sender_name = ?",
                        (run_id, msg["content"], msg.get("sender_name"))
                    ) as cursor:
                        if not await cursor.fetchone():
                            await db.execute(
                                "INSERT INTO messages (run_id, role, content, sender_name) VALUES (?, ?, ?, ?)",
                                (run_id, msg["role"], msg["content"], msg.get("sender_name"))
                            )
            
            # 7. Update Run Status with the final result content and token usage
            final_content = final_messages[-1]["content"] if final_messages else "No result generated."
            total_tokens = result.get("total_tokens", 0)
            await db.execute("UPDATE runs SET status = 'completed', result = ?, usage_tokens = ? WHERE id = ?", 
                             (final_content, total_tokens, run_id))
            await db.commit()

            await manager.broadcast(json.dumps({
                "type": "log",
                "run_id": run_id,
                "message": "Workflow completed successfully."
            }))

            return {"run_id": run_id, "status": "completed", "result": final_content}

    except Exception as e:
        import traceback
        traceback.print_exc()
        error_msg = f"Execution failed: {str(e)}"
        print(f"Error executing workflow: {error_msg}")
        await manager.broadcast(json.dumps({
            "type": "error",
            "run_id": run_id,
            "message": error_msg
        }))
        try:
            async with aiosqlite.connect(DB_PATH) as db:
                await db.execute("UPDATE runs SET status = 'failed' WHERE id = ?", (run_id,))
                await db.commit()
        except:
            pass
        return {"error": str(e)}
