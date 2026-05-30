# Phase 3: Workflow Builder & Live Monitoring

This phase is about bringing the "orchestration" part of the platform to life. We will build the visual workflow editor and the real-time monitoring dashboard.

## Key Steps:

1.  **Install React Flow**: Add the `reactflow` package to the frontend project. This library is the core of our visual builder.

2.  **Workflow Builder UI (`pages/WorkflowBuilder.jsx`)**:
    *   Create the main component for the "Workflows" page.
    *   The layout will be a two-panel design:
        *   A sidebar that lists all available agents. Users can drag these agents onto the canvas.
        *   A main canvas area powered by `ReactFlow`.
    *   Implement the logic to add agent nodes to the canvas and connect them with edges.
    *   Add input fields for the workflow name and a test message.
    *   Create a "Save & Run" button that:
        1.  Serializes the node and edge data into the required JSON format.
        2.  Calls the backend API to save the new workflow.
        3.  Triggers a new run of that workflow with the test message.

3.  **Monitoring UI (`pages/Monitor.jsx`)**:
    *   Create the component for the "Monitor" page, which will provide a live view of agent activity.
    *   This component will have a multi-panel layout:
        *   **Run History**: A sidebar listing recent runs, their status (e.g., `running`, `completed`), and their trigger source (`manual`, `telegram`).
        *   **Live Event Stream**: A panel that connects to the `/ws/logs` WebSocket and displays incoming events in real-time as they are broadcast from the executor.
        *   **Message Details**: A panel that displays the full, persisted message history for a selected run from the history list. This allows users to see the complete conversation between agents and tools.
