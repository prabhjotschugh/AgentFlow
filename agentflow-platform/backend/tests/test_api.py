import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path so we can import main
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "AgentFlow Platform API" in response.json()["message"]

def test_list_agents():
    response = client.get("/api/agents/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_agent():
    agent_data = {
        "name": "Test Agent",
        "role": "Tester",
        "system_prompt": "You are a test agent.",
        "tools": [],
        "model_settings": {"model": "gemini-1.5-flash", "temperature": 0.7},
        "telegram_enabled": False,
        "schedule": "Always On",
        "rate_limit": 100
    }
    response = client.post("/api/agents/", json=agent_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Agent"
    assert "id" in data

def test_list_workflows():
    response = client.get("/api/workflows/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
