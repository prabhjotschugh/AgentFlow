import sqlite3
import json

try:
    conn = sqlite3.connect('agentflow_platform.db')
    conn.row_factory = sqlite3.Row
    r = conn.execute("SELECT id, result FROM runs WHERE status = 'completed' ORDER BY created_at DESC LIMIT 1").fetchone()
    if r:
        print(f"Run ID: {r['id']}")
        if r['result']:
            print(f"Result length: {len(r['result'])}")
            print(f"Result starts with: {r['result'][:200]}")
            if "![Generated Image]" in r['result']:
                print("SUCCESS: Found image tag in result.")
            else:
                print("FAILURE: Image tag NOT found in result.")
        else:
            print("FAILURE: Result is empty.")
    else:
        print("No completed runs found.")
    conn.close()
except Exception as e:
    print(f"Error: {e}")
