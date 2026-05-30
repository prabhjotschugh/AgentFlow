import sqlite3
import json
import os
from pathlib import Path

def check_database(db_path):
    """Check if database exists and has data."""
    if not os.path.exists(db_path):
        return None, 0, 0
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Count agents
        cursor.execute("SELECT COUNT(*) as count FROM agents")
        agent_count = cursor.fetchone()[0]
        
        # Count workflows
        cursor.execute("SELECT COUNT(*) as count FROM workflows")
        workflow_count = cursor.fetchone()[0]
        
        conn.close()
        return (agent_count, workflow_count)
    except Exception as e:
        return None

def query_db(db_path):
    """Query and display all workflows and agents from a specific database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    print("\n" + "="*120)
    print(f"DATABASE: {db_path}")
    print("="*120)
    
    print("\n" + "="*120)
    print("WORKFLOWS IN DATABASE")
    print("="*120)
    
    try:
        cursor.execute("SELECT id, name, config FROM workflows ORDER BY created_at DESC")
        workflows = cursor.fetchall()
        
        if workflows:
            print(f"✅ Found {len(workflows)} workflow(s)\n")
            for i, wf in enumerate(workflows, 1):
                print(f"[{i}] Workflow Name: {wf['name']}")
                print(f"    ID: {wf['id']}")
                try:
                    config = json.loads(wf['config'])
                    if 'nodes' in config:
                        agents_in_wf = [node['data'].get('name', 'Unknown') for node in config['nodes']]
                        print(f"    Agents in this workflow: {agents_in_wf}")
                except Exception as e:
                    print(f"    (Could not parse config: {e})")
                print()
        else:
            print("❌ NO WORKFLOWS FOUND\n")
    except Exception as e:
        print(f"❌ Error querying workflows: {e}\n")
    
    print("\n" + "="*120)
    print("AGENTS IN DATABASE")
    print("="*120)
    
    try:
        cursor.execute("SELECT id, name, role, tools, system_prompt FROM agents ORDER BY created_at DESC")
        agents = cursor.fetchall()
        
        if agents:
            print(f"✅ Found {len(agents)} agent(s)\n")
            for i, agent in enumerate(agents, 1):
                tools = json.loads(agent['tools']) if agent['tools'] else []
                print(f"[{i}] Agent Name: {agent['name']}")
                print(f"    Role: {agent['role']}")
                print(f"    Tools: {tools}")
                if agent['system_prompt']:
                    prompt_preview = agent['system_prompt'][:100] + "..." if len(agent['system_prompt']) > 100 else agent['system_prompt']
                    print(f"    System Prompt: {prompt_preview}")
                print()
        else:
            print("❌ NO AGENTS FOUND\n")
    except Exception as e:
        print(f"❌ Error querying agents: {e}\n")
    
    conn.close()
    print("="*120 + "\n")

if __name__ == "__main__":
    print("🔍 Finding and checking all AgentFlow databases...\n")
    
    # Check multiple possible database locations
    db_paths = [
        r"C:\Users\prabh\OneDrive\Desktop\AgentFlow\agentflow_platform.db",
        r"C:\Users\prabh\OneDrive\Desktop\AgentFlow\agentflow-platform\backend\agentflow_platform.db",
        r"C:\Users\prabh\OneDrive\Desktop\Agent\agentflow_platform.db",
        r"C:\Users\prabh\OneDrive\Desktop\Agent\agentflow-platform\backend\agentflow_platform.db",
    ]
    
    print("Checking database files:\n")
    db_with_data = None
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            result = check_database(db_path)
            if result:
                agent_count, workflow_count = result
                status = "✅ HAS DATA" if (agent_count > 0 or workflow_count > 0) else "❌ EMPTY"
                print(f"  {db_path}")
                print(f"    Agents: {agent_count}, Workflows: {workflow_count} {status}\n")
                
                if agent_count > 0 or workflow_count > 0:
                    db_with_data = db_path
        else:
            print(f"  {db_path} - NOT FOUND\n")
    
    if db_with_data:
        print(f"\n✨ Using database with data: {db_with_data}\n")
        query_db(db_with_data)
    else:
        print("\n❌ No database with data found!")