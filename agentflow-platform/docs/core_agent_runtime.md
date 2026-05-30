# Phase 2: Core Agent Runtime

This phase focuses on building the "brain" of the platform. We will implement the logic that allows agents to think, use tools, and communicate, all orchestrated by LangGraph.

## Key Steps:

1.  **Directory Structure**: Create the `backend/runtime/` and `backend/telegram/` directories to house the core logic.

2.  **Gemini LLM Wrapper (`runtime/gemini_llm.py`)**:
    *   Create a class to encapsulate the `google-genai` SDK.
    *   This wrapper will handle communication with the Gemini API, including system prompts, temperature settings, and message history.

3.  **Tool Implementation (`runtime/tools.py`)**:
    *   Define a set of built-in tools that agents can use (e.g., `web_search`, `calculator`).
    *   Each tool will be decorated with LangChain's `@tool` decorator for easy integration.

4.  **Agent Memory (`runtime/memory.py`)**:
    *   Implement a class that connects to the `agent_memory` table in SQLite.
    *   This will provide agents with persistent, long-term memory across different runs. Agents will be able to read their memory context and save new information.

5.  **Graph Builder (`runtime/graph_builder.py`)**:
    *   This is the core of the LangGraph implementation.
    *   Create a function `build_workflow_graph` that dynamically constructs a `StateGraph` from a workflow configuration stored in the database.
    *   It will create a "node" for each agent in the workflow and connect them with "edges" as defined.

6.  **Workflow Executor (`runtime/executor.py`)**:
    *   Create the main `execute_workflow` function.
    *   This function will be responsible for:
        *   Loading agent and workflow configurations from the database.
        *   Calling the `graph_builder` to compile the LangGraph graph.
        *   Invoking the graph with the initial user input.
        *   Persisting every message (from users, agents, and tools) to the `messages` table.
        *   Broadcasting real-time events to the frontend via the WebSocket connection.
        *   Updating the final status of the run in the `runs` table.
