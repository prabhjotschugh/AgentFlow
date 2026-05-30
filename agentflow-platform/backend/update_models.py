import sqlite3
import json

conn = sqlite3.connect('agentflow_platform.db')
conn.row_factory = sqlite3.Row

cursor = conn.execute('SELECT id, model_settings FROM agents')
agents = cursor.fetchall()

for agent in agents:
    settings = json.loads(agent['model_settings'])
    # Update any old model name to the new specific one
    settings['model'] = 'gemini-3.1-flash-lite'
    conn.execute('UPDATE agents SET model_settings = ? WHERE id = ?', (json.dumps(settings), agent['id']))

conn.commit()
conn.close()
print("Successfully updated all agents to gemini-3.1-flash-lite")
