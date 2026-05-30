# backend/populate_workflows.py
import sqlite3
import json
import uuid

# Use the correct database name from the rename phase
DB_PATH = 'agentflow_platform.db'

def create_agent(conn, name, role, prompt, tools, model="gemini-3.1-flash-lite"):
    agent_id = str(uuid.uuid4())
    conn.execute("""
        INSERT INTO agents (id, name, role, system_prompt, tools, model_settings)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (agent_id, name, role, prompt, json.dumps(tools), json.dumps({"model": model, "temperature": 0.7})))
    return agent_id

def create_wf(conn, name, nodes_data):
    wf_id = str(uuid.uuid4())
    nodes = []
    edges = []
    for i, (a_id, a_name, a_role) in enumerate(nodes_data):
        node_id = f"node-{i}-{wf_id[:8]}"
        nodes.append({
            "id": node_id, 
            "type": "agentNode",
            "data": {"agentId": a_id, "name": a_name, "role": a_role},
            "position": {"x": 200, "y": 100 + (i * 200)}
        })
        if i > 0:
            edges.append({
                "id": f"e-{i}-{wf_id[:8]}", 
                "source": nodes[i-1]["id"], 
                "target": node_id
            })
    
    conn.execute("INSERT INTO workflows (id, name, config) VALUES (?, ?, ?)", 
                 (wf_id, name, json.dumps({"nodes": nodes, "edges": edges})))

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # --- 1. THE CONTENT STUDIO (TEMPLATE) ---
    print("Creating Content Studio agents...")
    res_id = create_agent(conn, "Researcher", "Fact Finder", 
        "You are an expert researcher. Find key facts, statistics, and credible information about the topic provided by the user. Use web search if needed.", 
        ["web_search"])
    wr_id = create_agent(conn, "Writer", "Content Creator", 
        "You are a professional writer. Craft a high-quality, engaging blog post or article based on the facts provided by the Researcher. Focus on narrative flow and clarity.", 
        [])
    img_id = create_agent(conn, "Cover Artist", "AI Artist", 
        "You are an AI Artist. Generate a vivid visual prompt for a header image that matches the theme of the written article. Output the prompt as a JSON object with 'subject', 'style', 'lighting', 'composition', and 'mood' fields.", 
        [], "gemini-3.1-flash-image-preview")

    # --- 2. MARKET INTELLIGENCE (TEMPLATE) ---
    print("Creating Market Intelligence agents...")
    scout_id = create_agent(conn, "Intel Scout", "Web Analyst", 
        "You are a competitive intelligence analyst. Scrape information from provided URLs to identify market trends, competitor pricing, and feature sets.", 
        ["url_scraper"])
    strat_id = create_agent(conn, "Strategist", "Business Consultant", 
        "You are a senior business strategist. Analyze the data from the Intel Scout and perform a SWOT analysis. Use the calculator for any financial comparisons if needed.", 
        ["calculator"])

    # --- 3. CODE SECURITY ---
    print("Creating Code Security agents...")
    sec_id = create_agent(conn, "Security Probe", "Security Engineer", 
        "Analyze the provided code snippet for security vulnerabilities, following OWASP guidelines. Focus on potential injections, leaks, and authentication flaws.", 
        [])
    qual_id = create_agent(conn, "Quality Lead", "Senior Developer", 
        "Review the code for logical errors, efficiency, and adherence to clean code principles. Provide a summary of improvements.", 
        [])

    # --- 4. YOUTUBE CONCIERGE ---
    print("Creating YouTube Concierge agents...")
    trans_id = create_agent(conn, "Transcriber", "Video Analyst", 
        "Fetch the transcript of the YouTube video from the provided URL. Provide the full text for analysis.", 
        ["youtube_transcript"])
    sum_id = create_agent(conn, "Summarizer", "Knowledge Curator", 
        "Condense the YouTube transcript into a clear summary with 5 key takeaways and a watch recommendation.", 
        [])

    # --- 5. VIRAL MACHINE ---
    print("Creating Viral Machine agents...")
    shred_id = create_agent(conn, "Shredder", "Hook Specialist", 
        "Extract the most compelling and 'viral' points from the provided article or text. Focus on controversial or highly useful insights.", 
        [])
    ghost_id = create_agent(conn, "Ghostwriter", "Copywriter", 
        "Transform the viral hooks into a 10-post Twitter thread and a professional LinkedIn post. Use emojis and formatting for high engagement.", 
        [])

    # Create the Workflows
    print("Building workflows...")
    create_wf(conn, "[TEMPLATE] Content Studio", [
        (res_id, "Researcher", "Fact Finder"), 
        (wr_id, "Writer", "Content Creator"), 
        (img_id, "Cover Artist", "AI Artist")
    ])
    create_wf(conn, "[TEMPLATE] Market Intelligence", [
        (scout_id, "Intel Scout", "Web Analyst"), 
        (strat_id, "Strategist", "Business Consultant")
    ])
    create_wf("Code Security Auditor", [
        (sec_id, "Security Probe", "Security Engineer"), 
        (qual_id, "Quality Lead", "Senior Developer")
    ])
    create_wf("YouTube Concierge", [
        (trans_id, "Transcriber", "Video Analyst"), 
        (sum_id, "Summarizer", "Knowledge Curator")
    ])
    create_wf("Viral Machine", [
        (shred_id, "Shredder", "Hook Specialist"), 
        (ghost_id, "Ghostwriter", "Copywriter")
    ])

    conn.commit()
    conn.close()
    print("SUCCESS: 5 Workflows and all agents injected into AgentFlow database!")

if __name__ == "__main__":
    main()
