from fastapi import APIRouter, Depends, HTTPException
from typing import List
import uuid
import json
from database import get_db
from models import Agent, AgentCreate
import aiosqlite

router = APIRouter(prefix="/agents", tags=["agents"])

@router.get("/", response_model=List[Agent])
async def list_agents(db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT * FROM agents") as cursor:
        rows = await cursor.fetchall()
        agents = []
        for row in rows:
            agents.append(Agent(
                id=row["id"],
                name=row["name"],
                role=row["role"],
                system_prompt=row["system_prompt"],
                tools=json.loads(row["tools"] or "[]"),
                model_settings=json.loads(row["model_settings"] or "{}"),
                telegram_enabled=bool(row["telegram_enabled"]),
                schedule=row["schedule"],
                rate_limit=row["rate_limit"],
                created_at=row["created_at"]
            ))
        return agents

@router.post("/", response_model=Agent)
async def create_agent(agent: AgentCreate, db: aiosqlite.Connection = Depends(get_db)):
    agent_id = str(uuid.uuid4())
    await db.execute(
        """
        INSERT INTO agents (id, name, role, system_prompt, tools, model_settings, telegram_enabled, schedule, rate_limit)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            agent_id,
            agent.name,
            agent.role,
            agent.system_prompt,
            json.dumps(agent.tools),
            json.dumps(agent.model_settings),
            agent.telegram_enabled,
            agent.schedule,
            agent.rate_limit
        )
    )
    await db.commit()
    
    async with db.execute("SELECT * FROM agents WHERE id = ?", (agent_id,)) as cursor:
        row = await cursor.fetchone()
        return Agent(
            id=row["id"],
            name=row["name"],
            role=row["role"],
            system_prompt=row["system_prompt"],
            tools=json.loads(row["tools"] or "[]"),
            model_settings=json.loads(row["model_settings"] or "{}"),
            telegram_enabled=bool(row["telegram_enabled"]),
        schedule=row["schedule"],
        rate_limit=row["rate_limit"],
        created_at=row["created_at"]
    )

@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str, db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT * FROM agents WHERE id = ?", (agent_id,)) as cursor:
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Agent not found")
        return Agent(
            id=row["id"],
            name=row["name"],
            role=row["role"],
            system_prompt=row["system_prompt"],
            tools=json.loads(row["tools"] or "[]"),
            model_settings=json.loads(row["model_settings"] or "{}"),
            telegram_enabled=bool(row["telegram_enabled"]),
            schedule=row["schedule"],
            rate_limit=row["rate_limit"],
        )

@router.get("/tools")
async def list_available_tools():
    from runtime.tools import AVAILABLE_TOOLS
    return list(AVAILABLE_TOOLS.keys())

@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, db: aiosqlite.Connection = Depends(get_db)):
    await db.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
    await db.commit()
    return {"status": "success"}

@router.put("/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, agent: AgentCreate, db: aiosqlite.Connection = Depends(get_db)):
    await db.execute(
        """
        UPDATE agents 
        SET name = ?, role = ?, system_prompt = ?, tools = ?, model_settings = ?, telegram_enabled = ?, schedule = ?, rate_limit = ?
        WHERE id = ?
        """,
        (
            agent.name,
            agent.role,
            agent.system_prompt,
            json.dumps(agent.tools),
            json.dumps(agent.model_settings),
            agent.telegram_enabled,
            agent.schedule,
            agent.rate_limit,
            agent_id
        )
    )
    await db.commit()
    
    async with db.execute("SELECT * FROM agents WHERE id = ?", (agent_id,)) as cursor:
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Agent not found")
        return Agent(
            id=row["id"],
            name=row["name"],
            role=row["role"],
            system_prompt=row["system_prompt"],
            tools=json.loads(row["tools"] or "[]"),
            model_settings=json.loads(row["model_settings"] or "{}"),
            telegram_enabled=bool(row["telegram_enabled"]),
            schedule=row["schedule"],
            rate_limit=row["rate_limit"],
            created_at=row["created_at"]
        )
