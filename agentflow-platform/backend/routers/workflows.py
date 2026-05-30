from fastapi import APIRouter, Depends, HTTPException
from typing import List
import uuid
import json
from database import get_db
from models import Workflow, WorkflowCreate
import aiosqlite

router = APIRouter(prefix="/workflows", tags=["workflows"])

@router.get("/", response_model=List[Workflow])
async def list_workflows(db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT * FROM workflows ORDER BY created_at DESC") as cursor:
        rows = await cursor.fetchall()
        workflows = []
        for row in rows:
            workflows.append(Workflow(
                id=row["id"],
                name=row["name"],
                config=json.loads(row["config"]),
                created_at=row["created_at"]
            ))
        return workflows

@router.post("/", response_model=Workflow)
async def create_workflow(workflow: WorkflowCreate, db: aiosqlite.Connection = Depends(get_db)):
    workflow_id = str(uuid.uuid4())
    await db.execute(
        "INSERT INTO workflows (id, name, config) VALUES (?, ?, ?)",
        (workflow_id, workflow.name, json.dumps(workflow.config))
    )
    await db.commit()
    
    async with db.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,)) as cursor:
        row = await cursor.fetchone()
        return Workflow(
            id=row["id"],
            name=row["name"],
            config=json.loads(row["config"]),
            created_at=row["created_at"]
        )

@router.get("/{workflow_id}", response_model=Workflow)
async def get_workflow(workflow_id: str, db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT * FROM workflows WHERE id = ?", (workflow_id,)) as cursor:
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Workflow not found")
        return Workflow(
            id=row["id"],
            name=row["name"],
            config=json.loads(row["config"]),
            created_at=row["created_at"]
        )

@router.delete("/{workflow_id}")
async def delete_workflow(workflow_id: str, db: aiosqlite.Connection = Depends(get_db)):
    await db.execute("DELETE FROM workflows WHERE id = ?", (workflow_id,))
    await db.commit()
    return {"status": "success"}
