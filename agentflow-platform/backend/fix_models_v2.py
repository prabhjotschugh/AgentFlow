import sqlite3
import json

conn = sqlite3.connect('agentflow_platform.db')
conn.row_factory = sqlite3.Row

cursor = conn.execute('SELECT id, name, model_settings FROM agents')
agents = cursor.fetchall()

for agent in agents:
    settings = json.loads(agent['model_settings'] or '{}')
    changed = False
    
    if agent['name'] == 'Image Generator':
        settings['model'] = 'gemini-3.1-flash-image-preview'
        # Update system prompt to force generation
        new_prompt = "You are a native Image Generation Model. Your sole purpose is to take the provided JSON design and GENERATE the actual image. Do not provide a text description. Do not ask questions. Output the image pixels immediately based on the specs."
        conn.execute('UPDATE agents SET system_prompt = ?, model_settings = ? WHERE id = ?', (new_prompt, json.dumps(settings), agent['id']))
        changed = True
    elif agent['name'] == 'Prompt Architect':
        # Update the system prompt directly to avoid escaping issues
        new_prompt = "You are a professional Visual Designer and Prompt Engineer. Your task is to take a users descriptive request and turn it into a high-quality, detailed JSON prompt for an AI image generator. The JSON should include fields like subject, style, lighting, composition, and mood. IMPORTANT: Use descriptive artistic terms. Avoid clinical or medical words. Instead of cybernetic use tech-integrated or futuristic glowing circuitry. Focus on the beauty and aesthetic of the scene. Output ONLY the JSON object."
        conn.execute('UPDATE agents SET system_prompt = ? WHERE id = ?', (new_prompt, agent['id']))
        changed = True
    elif settings.get('model') == 'gemini-1.5-flash' or settings.get('model') == 'gemini-2.0-flash':
        settings['model'] = 'gemini-3.1-flash-lite'
        changed = True
        
    if changed:
        conn.execute('UPDATE agents SET model_settings = ? WHERE id = ?', (json.dumps(settings), agent['id']))

conn.commit()
conn.close()
print("Updated database agents to use supported models.")
