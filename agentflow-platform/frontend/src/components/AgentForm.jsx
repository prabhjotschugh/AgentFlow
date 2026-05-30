import React, { useState, useEffect } from 'react';
import { agentsApi } from '../api/api';

const AgentForm = ({ agent, onClose, onSuccess }) => {
  const [formData, setFormData] = useState(agent || {
    name: '',
    role: '',
    system_prompt: '',
    tools: [],
    model_settings: { model: 'gemini-1.5-flash', temperature: 0.7 },
    telegram_enabled: false,
    schedule: 'Always On',
    rate_limit: 100
  });
  const [loading, setLoading] = useState(false);
  const [availableTools, setAvailableTools] = useState([]);

  useEffect(() => {
    const fetchTools = async () => {
      try {
        const tools = await agentsApi.listTools();
        setAvailableTools(tools);
      } catch (err) {
        console.error("Failed to fetch tools", err);
        // Fallback
        setAvailableTools(["calculator", "web_search", "url_scraper", "current_time_fetcher", "youtube_transcript"]);
      }
    };
    fetchTools();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (agent) {
        await agentsApi.update(agent.id, formData);
      } else {
        await agentsApi.create(formData);
      }
      onSuccess();
    } catch (error) {
      console.error("Failed to save agent", error);
    } finally {
      setLoading(false);
    }
  };

  const toggleTool = (tool) => {
    setFormData(prev => ({
      ...prev,
      tools: prev.tools.includes(tool) 
        ? prev.tools.filter(t => t !== tool) 
        : [...prev.tools, tool]
    }));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-card w-full max-w-2xl rounded-2xl border border-border shadow-2xl overflow-hidden max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-border bg-accent/50">
          <div>
            <h2 className="text-2xl font-bold">{agent ? '✏️ Edit Agent' : '➕ Create Agent'}</h2>
            <p className="text-sm text-muted-foreground mt-1">Configure your agent's personality and capabilities</p>
          </div>
          <button onClick={onClose} className="text-2xl hover:opacity-70 transition">×</button>
        </div>

        <form onSubmit={handleSubmit} className="p-8 space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2">Agent Name</label>
              <input
                required
                className="w-full bg-accent border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition"
                placeholder="e.g. Research Assistant"
                value={formData.name}
                onChange={e => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Role</label>
              <input
                required
                className="w-full bg-accent border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none transition"
                placeholder="e.g. Data Analyst"
                value={formData.role}
                onChange={e => setFormData({ ...formData, role: e.target.value })}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold mb-2">System Prompt</label>
            <textarea
              required
              rows={4}
              className="w-full bg-accent border border-border rounded-lg px-4 py-3 focus:ring-2 focus:ring-purple-500 focus:border-transparent outline-none resize-none transition"
              placeholder="Describe how this agent should behave..."
              value={formData.system_prompt}
              onChange={e => setFormData({ ...formData, system_prompt: e.target.value })}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2">Model</label>
              <select
                className="w-full bg-accent border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-purple-500 outline-none transition"
                value={formData.model_settings.model}
                onChange={e => setFormData({ 
                  ...formData, 
                  model_settings: { ...formData.model_settings, model: e.target.value } 
                })}
              >
                <option value="gemini-3.1-pro-preview">Gemini 3.1 Pro Preview</option>
                <option value="gemini-3.5-flash">Gemini 3.5 Flash</option>
                <option value="gemini-3.1-flash-lite">Gemini 3.1 Flash Lite</option>
                <option value="gemini-3.1-flash-image-preview">Gemini 3.1 Flash Image Preview</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Temperature ({formData.model_settings.temperature})</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                className="w-full h-10 accent-purple-500"
                value={formData.model_settings.temperature}
                onChange={e => setFormData({ 
                  ...formData, 
                  model_settings: { ...formData.model_settings, temperature: parseFloat(e.target.value) } 
                })}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold mb-3">Tools</label>
            <div className="grid grid-cols-2 gap-3">
              {availableTools.map(tool => (
                <button
                  key={tool}
                  type="button"
                  onClick={() => toggleTool(tool)}
                  className={`p-3 rounded-lg border-2 transition font-medium text-left ${
                    formData.tools.includes(tool)
                      ? 'bg-purple-500/10 border-purple-500 text-purple-500'
                      : 'bg-accent border-border hover:border-purple-500/50'
                  }`}
                >
                  {formData.tools.includes(tool) ? '✓ ' : '○ '}
                  {tool.replace('_', ' ').toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2">Schedule</label>
              <select
                className="w-full bg-accent border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-purple-500 outline-none transition"
                value={formData.schedule}
                onChange={e => setFormData({ ...formData, schedule: e.target.value })}
              >
                <option value="Always On">Always On</option>
                <option value="Business Hours">Business Hours</option>
                <option value="Weekend Only">Weekend Only</option>
                <option value="Disabled">Disabled</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Rate Limit (Req/min)</label>
              <input
                type="number"
                className="w-full bg-accent border border-border rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-purple-500 outline-none transition"
                value={formData.rate_limit}
                onChange={e => setFormData({ ...formData, rate_limit: parseInt(e.target.value) })}
              />
            </div>
          </div>

          <div className="flex items-center justify-between p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
            <div>
              <p className="font-semibold">Enable Telegram</p>
              <p className="text-xs text-muted-foreground">Allow this agent to respond to Telegram messages</p>
            </div>
            <button
              type="button"
              onClick={() => setFormData({ ...formData, telegram_enabled: !formData.telegram_enabled })}
              className={`w-12 h-6 rounded-full relative transition ${formData.telegram_enabled ? 'bg-blue-500' : 'bg-muted'}`}
            >
              <div className={`absolute top-0.5 w-5 h-5 rounded-full bg-white transition ${formData.telegram_enabled ? 'left-6' : 'left-0.5'}`} />
            </button>
          </div>

          <div className="flex gap-3 pt-4 border-t border-border">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-3 rounded-lg border border-border font-semibold hover:bg-accent transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-4 py-3 bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded-lg font-semibold shadow-lg hover:shadow-xl transition disabled:opacity-50"
            >
              {loading ? '⏳ Saving...' : (agent ? '💾 Update' : '✨ Create')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AgentForm;

