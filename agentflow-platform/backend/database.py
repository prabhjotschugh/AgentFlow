import sqlite3
import aiosqlite
import os
from datetime import datetime

DB_PATH = "agentflow_platform.db"

# SQL Schema to initialize the database
SCHEMA = """
CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    tools TEXT, -- JSON array of tool names
    model_settings TEXT, -- JSON object
    telegram_enabled BOOLEAN DEFAULT FALSE,
    schedule TEXT DEFAULT 'Always On', -- NEW: Schedule dimension
    rate_limit INTEGER DEFAULT 100,      -- NEW: Limit dimension
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workflows (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    config TEXT NOT NULL, -- JSON structure of nodes and edges (ReactFlow format)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    workflow_id TEXT,
    status TEXT NOT NULL, -- running, completed, failed
    trigger_source TEXT, -- manual, telegram
    result TEXT, -- Final polished output
    usage_tokens INTEGER DEFAULT 0, -- NEW: Token tracking
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workflow_id) REFERENCES workflows(id)
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT,
    role TEXT NOT NULL, -- user, agent, tool
    content TEXT NOT NULL,
    sender_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES runs(id)
);

CREATE TABLE IF NOT EXISTS agent_memory (
    agent_id TEXT PRIMARY KEY,
    memory_context TEXT, -- Long-term memory for the agent
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);
"""

async def init_db():
    """Initializes the database and creates tables if they don't exist."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()

async def get_db():
    """Dependency for getting a database connection."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db
