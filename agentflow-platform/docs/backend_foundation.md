# Phase 1: Backend Foundation & Setup

This phase establishes the complete foundation for our FastAPI backend. We will create the necessary project structure, define our database schema, set up our API models, and create the initial API endpoints for managing agents and workflows.

## Key Steps:

1.  **Project Structure**: Create the main directories (`backend/`, `frontend/`, `docs/`) to keep the project organized from the start.

2.  **Database (`database.py`)**:
    *   Define the complete `SQLite` database schema in SQL. This includes tables for `agents`, `workflows`, `runs`, `messages`, and `agent_memory`.
    *   Implement an asynchronous connection manager (`get_db`) for interacting with the SQLite database.
    *   Create an `init_db` function that sets up the database and creates all tables on application startup.

3.  **API Models (`models.py`)**:
    *   Define all `Pydantic` models that will be used for API request and response validation. This ensures our API is type-safe and self-documenting.

4.  **API Routers (`routers/`)**:
    *   Create placeholder files for all our API endpoints (`agents.py`, `workflows.py`, `runs.py`, `messages.py`, `websocket.py`).
    *   Implement the full CRUD (Create, Read, Update, Delete) functionality for the `/api/agents` endpoint.

5.  **Main Application (`main.py`)**:
    *   Set up the main `FastAPI` application instance.
    *   Configure CORS middleware to allow the frontend application (running on a different port) to communicate with the backend.
    *   Implement a `lifespan` event handler to initialize the database when the server starts.
    *   Include all the API routers into the main application.

6.  **Dependencies**:
    *   Create a `requirements.txt` file listing all necessary Python packages.
    *   Create a `.env.example` file to document the required environment variables.

By the end of this phase, we will have a fully functional, albeit simple, backend server that can create and manage agents, backed by a persistent SQLite database.
