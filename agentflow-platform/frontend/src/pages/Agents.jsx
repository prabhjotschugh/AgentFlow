import React, { useState, useEffect } from 'react';
import { agentsApi } from '../api/api';
import AgentForm from '../components/AgentForm';

const Agents = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingAgent, setEditingAgent] = useState(null);

  const fetchAgents = async () => {
    try {
      const data = await agentsApi.list();
      setAgents(data);
    } catch (error) {
      console.error("Failed to fetch agents", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  const handleDelete = async (id) => {
    if (window.confirm("Are you sure you want to delete this agent?")) {
      await agentsApi.delete(id);
      fetchAgents();
    }
  };

  const openEditModal = (agent) => {
    setEditingAgent(agent);
    setIsModalOpen(true);
  };

  return (
    <main className="flex-1 overflow-auto">
      <div className="p-8 max-w-7xl mx-auto">
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">AI Agents</h1>
            <p className="text-muted-foreground">Create and manage your autonomous agents.</p>
          </div>
          <button
            onClick={() => {
              setEditingAgent(null);
              setIsModalOpen(true);
            }}
            className="bg-gradient-to-r from-purple-500 to-blue-500 text-white px-6 py-3 rounded-lg font-semibold shadow-lg hover:shadow-xl transition-all"
          >
            + Create Agent
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {loading ? (
            Array(3).fill(0).map((_, i) => (
              <div key={i} className="h-64 rounded-2xl bg-accent animate-pulse" />
            ))
          ) : agents.length === 0 ? (
            <div className="col-span-full py-20 text-center border-2 border-dashed border-border rounded-2xl">
              <p className="text-lg text-muted-foreground mb-4">No agents yet</p>
              <p className="text-sm text-muted-foreground">Create your first agent to get started</p>
            </div>
          ) : (
            agents.map((agent) => (
              <div
                key={agent.id}
                className="rounded-2xl border border-border bg-card p-6 group hover:border-primary/50 hover:shadow-lg transition-all duration-300"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-purple-500 to-blue-500 flex items-center justify-center text-white font-bold">
                    {agent.name[0]}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => openEditModal(agent)}
                      className="px-3 py-1.5 text-sm rounded hover:bg-accent transition-colors"
                    >
                      ✎
                    </button>
                    <button
                      onClick={() => handleDelete(agent.id)}
                      className="px-3 py-1.5 text-sm text-red-500 hover:bg-red-500/10 rounded transition-colors"
                    >
                      🗑
                    </button>
                  </div>
                </div>

                <h3 className="text-xl font-bold mb-1">{agent.name}</h3>
                <p className="text-primary font-medium text-sm mb-3">{agent.role}</p>
                <p className="text-muted-foreground text-sm line-clamp-2 mb-4 leading-relaxed">
                  {agent.system_prompt}
                </p>

                <div className="flex flex-wrap gap-2 pt-4 border-t border-border">
                  {agent.tools.map((tool) => (
                    <span key={tool} className="text-xs bg-accent px-2 py-1 rounded">
                      {tool}
                    </span>
                  ))}
                  {agent.telegram_enabled && (
                    <span className="text-xs bg-blue-500/10 text-blue-500 px-2 py-1 rounded">
                      Telegram
                    </span>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {isModalOpen && (
          <AgentForm
            agent={editingAgent}
            onClose={() => setIsModalOpen(false)}
            onSuccess={() => {
              setIsModalOpen(false);
              fetchAgents();
            }}
          />
        )}
      </div>
    </main>
  );
};

export default Agents;
