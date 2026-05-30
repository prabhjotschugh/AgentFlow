import React, { useState, useCallback, useEffect, useRef, useMemo } from 'react';
import ReactFlow, { 
  addEdge, 
  Background, 
  Controls, 
  MiniMap,
  useNodesState,
  useEdgesState,
  Panel,
  Handle,
  Position
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Plus, Save, Play, Trash2, Box, Cpu } from 'lucide-react';
import { agentsApi, workflowsApi } from '../api/api';

const initialNodes = [];
const initialEdges = [];

const AgentNode = ({ data }) => {
  return (
    <div className="bg-card border-2 border-primary rounded-xl text-foreground shadow-lg flex flex-col items-center p-3 min-w-[120px]">
      <Handle type="target" position={Position.Top} className="!bg-primary !w-2 !h-2" />
      <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center mb-1">
        <Cpu className="w-4 h-4 text-primary-foreground" />
      </div>
      <div className="font-bold text-xs">{data.name || 'Agent'}</div>
      <div className="text-[10px] opacity-70">{data.role || 'No Role'}</div>
      <Handle type="source" position={Position.Bottom} className="!bg-primary !w-2 !h-2" />
    </div>
  );
};

const Workflows = () => {
  const nodeTypes = useMemo(() => ({
    agentNode: AgentNode,
  }), []);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [agents, setAgents] = useState([]);
  const [workflowName, setWorkflowName] = useState('Untitled Workflow');
  const [isSaving, setIsSaving] = useState(false);
  const [activeWorkflow, setActiveWorkflow] = useState(null);
  const [showList, setShowList] = useState(true);
  const [savedWorkflows, setSavedWorkflows] = useState([]);
  const [showRunModal, setShowRunModal] = useState(false);
  const [runMessage, setRunMessage] = useState('');

  useEffect(() => {
    fetchAgents();
    fetchWorkflows();
  }, []);

  const handleRun = async () => {
    if (!runMessage) return alert('Please enter a message');
    try {
      await workflowsApi.execute(activeWorkflow.id, runMessage);
      setShowRunModal(false);
      setRunMessage('');
      alert('Workflow execution started! Check the Monitor page.');
    } catch (err) {
      console.error('Failed to execute workflow', err);
    }
  };

  const fetchAgents = async () => {
    try {
      const data = await agentsApi.list();
      setAgents(data);
    } catch (err) {
      console.error('Failed to fetch agents', err);
    }
  };

  const fetchWorkflows = async () => {
    try {
      const data = await workflowsApi.list();
      setSavedWorkflows(data);
    } catch (err) {
      console.error('Failed to fetch workflows', err);
    }
  };

  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  const onAddAgent = (agent) => {
    const newNode = {
      id: `agent-${Date.now()}`,
      type: 'agentNode',
      data: { 
        name: agent.name,
        role: agent.role,
        agentId: agent.id 
      },
      position: { x: Math.random() * 400, y: Math.random() * 400 },
    };
    setNodes((nds) => nds.concat(newNode));
  };

  const saveWorkflow = async () => {
    if (!workflowName) return alert('Please enter a workflow name');
    setIsSaving(true);
    try {
      const config = { nodes, edges };
      await workflowsApi.create({ name: workflowName, config });
      fetchWorkflows();
      setShowList(true);
    } catch (err) {
      console.error('Failed to save workflow', err);
    } finally {
      setIsSaving(false);
    }
  };

  const deleteWorkflow = async (id) => {
    if (!window.confirm('Are you sure you want to delete this workflow?')) return;
    try {
      await workflowsApi.delete(id);
      fetchWorkflows();
    } catch (err) {
      console.error('Failed to delete workflow', err);
    }
  };

  const loadWorkflow = (wf) => {
    setWorkflowName(wf.name);
    // Sanitize nodes to ensure they use the new custom node type and don't contain serialized JSX
    const sanitizedNodes = (wf.config.nodes || []).map(node => {
      let name = node.data?.name;
      let role = node.data?.role;
      
      // Attempt to recover from old broken label structure if it exists
      if (!name && node.data?.label?.props?.children) {
        const children = node.data.label.props.children;
        if (Array.isArray(children)) {
          name = children[1]?.props?.children;
          role = children[2]?.props?.children;
        }
      }

      return {
        ...node,
        type: 'agentNode',
        data: {
          ...node.data,
          name: typeof name === 'string' ? name : 'Agent',
          role: typeof role === 'string' ? role : 'Agent Role',
          label: undefined // Remove the broken label object
        }
      };
    });
    setNodes(sanitizedNodes);
    setEdges(wf.config.edges || []);
    setActiveWorkflow(wf);
    setShowList(false);
  };

  const createNew = () => {
    setWorkflowName('New Workflow');
    setNodes([]);
    setEdges([]);
    setActiveWorkflow(null);
    setShowList(false);
  };

  if (showList) {
    return (
      <main className="flex-1 overflow-auto bg-background p-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-blue-500 bg-clip-text text-transparent">
                Workflows
              </h1>
              <p className="text-muted-foreground mt-2">Manage and orchestrate multi-agent pipelines</p>
            </div>
            <button 
              onClick={createNew}
              className="px-6 py-3 bg-primary text-primary-foreground rounded-xl font-medium hover:opacity-90 transition-all flex items-center gap-2 shadow-lg shadow-primary/20"
            >
              <Plus className="w-5 h-5" />
              Create New
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {savedWorkflows.map((wf) => (
              <div 
                key={wf.id}
                className="group p-6 rounded-2xl bg-card border border-border hover:border-primary/50 transition-all cursor-pointer"
                onClick={() => loadWorkflow(wf)}
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center text-primary">
                    <Box className="w-6 h-6" />
                  </div>
                  <button 
                    onClick={(e) => { e.stopPropagation(); deleteWorkflow(wf.id); }}
                    className="p-2 text-muted-foreground hover:text-destructive transition-colors opacity-0 group-hover:opacity-100"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <h3 className="text-xl font-bold mb-1">{wf.name}</h3>
                <p className="text-sm text-muted-foreground">
                  {wf.config?.nodes?.length || 0} Agents • {wf.config?.edges?.length || 0} Connections
                </p>
                <div className="mt-4 flex items-center gap-2 text-xs text-primary font-medium">
                  Open Builder →
                </div>
              </div>
            ))}
            {savedWorkflows.length === 0 && (
              <div className="col-span-full py-20 text-center border-2 border-dashed border-border rounded-2xl">
                <p className="text-muted-foreground">No workflows yet. Create your first orchestration!</p>
              </div>
            )}
          </div>
        </div>
      </main>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-background overflow-hidden">
      {/* Top Bar */}
      <div className="h-16 border-b border-border bg-card/50 backdrop-blur-sm px-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => setShowList(true)}
            className="text-muted-foreground hover:text-foreground p-2"
          >
            ←
          </button>
          <input 
            type="text" 
            value={workflowName}
            onChange={(e) => setWorkflowName(e.target.value)}
            className="bg-transparent text-xl font-bold focus:outline-none border-b border-transparent focus:border-primary transition-colors"
          />
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={saveWorkflow}
            disabled={isSaving}
            className="px-4 py-2 rounded-lg bg-secondary text-secondary-foreground hover:opacity-90 flex items-center gap-2 disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {isSaving ? 'Saving...' : 'Save'}
          </button>
          {activeWorkflow && (
            <button 
              onClick={() => setShowRunModal(true)}
              className="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:opacity-90 flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              Run
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar - Agents */}
        <div className="w-72 border-r border-border bg-card/30 overflow-y-auto p-4">
          <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4">Available Agents</h3>
          <div className="space-y-3">
            {agents.map((agent) => (
              <div 
                key={agent.id}
                onClick={() => onAddAgent(agent)}
                className="p-3 rounded-xl border border-border bg-card hover:border-primary/50 cursor-pointer transition-all flex items-center gap-3 group"
              >
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white font-bold">
                  {agent.name[0]}
                </div>
                <div className="flex-1 overflow-hidden">
                  <div className="font-medium truncate group-hover:text-primary transition-colors">{agent.name}</div>
                  <div className="text-xs text-muted-foreground truncate">{agent.role}</div>
                </div>
                <Plus className="w-4 h-4 text-muted-foreground group-hover:text-primary" />
              </div>
            ))}
          </div>
        </div>

        {/* Canvas */}
        <div className="flex-1 relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            fitView
          >
            <Background color="#333" gap={20} />
            <Controls />
            <MiniMap 
              style={{ backgroundColor: 'hsl(var(--card))' }} 
              nodeColor={() => 'hsl(var(--primary))'}
              maskColor="rgba(0,0,0,0.3)"
            />
            <Panel position="top-right" className="bg-card border border-border p-2 rounded-lg text-xs text-muted-foreground shadow-xl">
              Connect agent nodes to define execution order
            </Panel>
          </ReactFlow>
        </div>
      </div>

      {/* Run Modal */}
      {showRunModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-in fade-in duration-300">
          <div className="w-full max-w-md bg-card border border-border rounded-2xl shadow-2xl p-6">
            <h2 className="text-2xl font-bold mb-4">Run Workflow</h2>
            <p className="text-muted-foreground text-sm mb-6">Enter an initial message to start the multi-agent execution.</p>
            <textarea
              className="w-full p-4 rounded-xl bg-muted border border-border focus:ring-2 focus:ring-primary focus:outline-none text-sm mb-6"
              rows={4}
              placeholder="e.g. Research the latest trends in AI agents and write a summary."
              value={runMessage}
              onChange={(e) => setRunMessage(e.target.value)}
            />
            <div className="flex justify-end gap-3">
              <button 
                onClick={() => setShowRunModal(false)}
                className="px-4 py-2 text-sm font-medium hover:text-primary"
              >
                Cancel
              </button>
              <button 
                onClick={handleRun}
                className="px-6 py-2 bg-primary text-primary-foreground rounded-xl font-medium hover:opacity-90 flex items-center gap-2"
              >
                <Play className="w-4 h-4" />
                Launch Workflow
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Workflows;
