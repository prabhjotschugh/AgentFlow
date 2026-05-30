from fastapi import APIRouter, Depends
from typing import List
from database import get_db
from models import Message
import aiosqlite

router = APIRouter(prefix="/messages", tags=["messages"])

@router.get("/{run_id}", response_model=List[Message])
async def get_messages(run_id: str, db: aiosqlite.Connection = Depends(get_db)):
    async with db.execute("SELECT * FROM messages WHERE run_id = ? ORDER BY created_at ASC", (run_id,)) as cursor:
        rows = await cursor.fetchall()
        messages = []
        for row in rows:
            messages.append(Message(
                id=row["id"],
                run_id=row["run_id"],
                role=row["role"],
                content=row["content"],
                sender_name=row["sender_name"],
                created_at=row["created_at"]
            ))
        return messages
