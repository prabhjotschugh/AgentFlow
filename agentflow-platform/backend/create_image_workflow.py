import sqlite3
import json
import uuid

conn = sqlite3.connect('agentflow_platform.db')
conn.row_factory = sqlite3.Row

# Cleanup: Delete existing "AI Image Studio" workflows and associated agents
existing_workflows = conn.execute("SELECT id, config FROM workflows WHERE name = 'AI Image Studio'").fetchall()
for wf in existing_workflows:
    config = json.loads(wf['config'])
    agent_ids = [node['data']['agentId'] for node in config.get('nodes', [])]
    for aid in agent_ids:
        conn.execute("DELETE FROM agents WHERE id = ?", (aid,))
    conn.execute("DELETE FROM workflows WHERE id = ?", (wf['id'],))

# 1. Create Prompt Architect Agent
architect_id = str(uuid.uuid4())
conn.execute("""
    INSERT INTO agents (id, name, role, system_prompt, tools, model_settings)
    VALUES (?, ?, ?, ?, ?, ?)
""", (
    architect_id,
    "Prompt Architect",
    "Visual Designer",
    "You are a professional Visual Designer and Prompt Engineer. Your task is to take a user's descriptive request and turn it into a high-quality, detailed JSON prompt for an AI image generator. The JSON should include fields like 'subject', 'style', 'lighting', 'composition', and 'mood'. Output ONLY the JSON object.",
    "[]",
    json.dumps({"model": "gemini-3.1-flash-lite", "temperature": 0.9})
))

# 2. Create Image Generator Agent
generator_id = str(uuid.uuid4())
conn.execute("""
    INSERT INTO agents (id, name, role, system_prompt, tools, model_settings)
    VALUES (?, ?, ?, ?, ?, ?)
""", (
    generator_id,
    "Image Generator",
    "AI Artist",
    "You are an AI Artist. You receive a structured JSON prompt from a designer and your job is to generate a vivid, descriptive response that represents the final image. Use your advanced visual capabilities to describe the masterpiece you have created based on the JSON.",
    "[]",
    json.dumps({"model": "gemini-3.1-flash-image-preview", "temperature": 0.7})
))

# 3. Create Workflow
workflow_id = str(uuid.uuid4())
workflow_name = "AI Image Studio"
nodes = [
    {
        "id": "node-architect",
        "type": "agentNode",
        "data": {"agentId": architect_id, "name": "Prompt Architect", "role": "Visual Designer"},
        "position": {"x": 100, "y": 100}
    },
    {
        "id": "node-generator",
        "type": "agentNode",
        "data": {"agentId": generator_id, "name": "Image Generator", "role": "AI Artist"},
        "position": {"x": 100, "y": 300}
    }
]
edges = [
    {
        "id": "edge-1",
        "source": "node-architect",
        "target": "node-generator"
    }
]
workflow_config = {"nodes": nodes, "edges": edges}

conn.execute("""
    INSERT INTO workflows (id, name, config)
    VALUES (?, ?, ?)
""", (workflow_id, workflow_name, json.dumps(workflow_config)))

conn.commit()
conn.close()
print(f"Successfully created agents and workflow '{workflow_name}'")
