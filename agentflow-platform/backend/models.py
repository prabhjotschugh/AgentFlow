from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Agent Models ---
class AgentBase(BaseModel):
    name: str
    role: str
    system_prompt: str
    tools: List[str] = []
    model_settings: Dict[str, Any] = {"model": "gemini-1.5-flash", "temperature": 0.7}
    telegram_enabled: bool = False
    schedule: str = "Always On"
    rate_limit: int = 100

class AgentCreate(AgentBase):
    pass

class Agent(AgentBase):
    id: str
    created_at: datetime

# --- Workflow Models ---
class WorkflowBase(BaseModel):
    name: str
    config: Dict[str, Any] # Nodes and Edges for ReactFlow

class WorkflowCreate(WorkflowBase):
    pass

class Workflow(WorkflowBase):
    id: str
    created_at: datetime

# --- Run Models ---
class RunBase(BaseModel):
    workflow_id: str
    trigger_source: str # manual, telegram

class RunCreate(RunBase):
    pass

class Run(RunBase):
    id: str
    status: str
    result: Optional[str] = None
    usage_tokens: int = 0
    created_at: datetime

# --- Message Models ---
class MessageBase(BaseModel):
    run_id: str
    role: str
    content: str
    sender_name: Optional[str] = None

class Message(MessageBase):
    id: int
    created_at: datetime

# --- Utility Models ---
class WorkflowRunRequest(BaseModel):
    message: str
