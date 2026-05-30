import aiosqlite
from database import DB_PATH

class AgentMemory:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    async def get_memory(self) -> str:
        """Fetch the long-term memory for the agent."""
        async with aiosqlite.connect(DB_PATH) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT memory_context FROM agent_memory WHERE agent_id = ?", (self.agent_id,)) as cursor:
                row = await cursor.fetchone()
                return row["memory_context"] if row else ""

    async def save_memory(self, context: str):
        """Save/Update the long-term memory for the agent."""
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                """
                INSERT INTO agent_memory (agent_id, memory_context, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(agent_id) DO UPDATE SET
                    memory_context = excluded.memory_context,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (self.agent_id, context)
            )
            await db.commit()
