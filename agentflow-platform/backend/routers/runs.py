from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
from database import get_db
from models import Run, WorkflowRunRequest
from runtime.executor import execute_workflow
import aiosqlite

router = APIRouter(prefix="/runs", tags=["runs"])

@router.get("/", response_model=List[Run])
async def list_runs(db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT * FROM runs ORDER BY created_at DESC") as cursor:
        rows = await cursor.fetchall()
        runs = []
        for row in rows:
            runs.append(Run(
                id=row["id"],
                workflow_id=row["workflow_id"],
                status=row["status"],
                trigger_source=row["trigger_source"],
                result=row["result"],
                usage_tokens=row["usage_tokens"], # NEW
                created_at=row["created_at"]
            ))
        return runs

@router.post("/{workflow_id}/execute")
async def trigger_workflow(
    workflow_id: str, 
    request: WorkflowRunRequest,
    background_tasks: BackgroundTasks
):
    # Execute workflow in background
    background_tasks.add_task(execute_workflow, workflow_id, request.message)
    return {"status": "started", "workflow_id": workflow_id}

@router.get("/{run_id}", response_model=Run)
async def get_run(run_id: str, db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT * FROM runs WHERE id = ?", (run_id,)) as cursor:
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Run not found")
        return Run(
            id=row["id"],
            workflow_id=row["workflow_id"],
            status=row["status"],
            trigger_source=row["trigger_source"],
            usage_tokens=row["usage_tokens"], # NEW
            created_at=row["created_at"]
        )
