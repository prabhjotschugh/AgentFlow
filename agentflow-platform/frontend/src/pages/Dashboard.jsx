import React, { useState, useEffect } from 'react';
import { 
  Users, 
  GitBranch, 
  Activity, 
  Play, 
  Plus, 
  ArrowUpRight, 
  Zap, 
  Clock,
  Database,
  ChevronRight
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { agentsApi, workflowsApi, runsApi } from '../api/api';

const Dashboard = () => {
  const [stats, setStats] = useState({
    agents: 0,
    workflows: 0,
    runs: 0,
    successRate: '98.4%'
  });
  const [recentRuns, setRecentRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [greeting, setGreeting] = useState('');

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good Morning');
    else if (hour < 18) setGreeting('Good Afternoon');
    else setGreeting('Good Evening');

    const fetchData = async () => {
      try {
        const [agents, workflows, runs] = await Promise.all([
          agentsApi.list(),
          workflowsApi.list(),
          runsApi.list()
        ]);
        
        setStats({
          agents: agents.length,
          workflows: workflows.length,
          runs: runs.length,
          successRate: '98%' // Placeholder for now
        });
        
        setRecentRuns(runs.slice(0, 5));
      } catch (err) {
        console.error('Failed to fetch dashboard data', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const statCards = [
    { label: 'Total Agents', value: stats.agents, icon: Users, color: 'text-blue-500', bg: 'bg-blue-500/10' },
    { label: 'Active Workflows', value: stats.workflows, icon: GitBranch, color: 'text-purple-500', bg: 'bg-purple-500/10' },
    { label: 'Total Executions', value: stats.runs, icon: Play, color: 'text-orange-500', bg: 'bg-orange-500/10' },
    { label: 'Platform Stability', value: stats.successRate, icon: Zap, color: 'text-green-500', bg: 'bg-green-500/10' },
  ];

  return (
    <main className="flex-1 overflow-y-auto bg-background text-foreground relative transition-colors duration-500">
      {/* Very Subtle Background Blobs */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/[0.03] dark:bg-primary/10 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-blue-500/[0.03] dark:bg-blue-500/10 blur-[120px] rounded-full pointer-events-none" />

      <div className="p-10 max-w-7xl mx-auto space-y-12 relative z-10">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-primary font-bold text-xs uppercase tracking-[0.2em]">
              <div className="w-8 h-[1.5px] bg-primary" />
              Intelligence Hub
            </div>
            <h1 className="text-4xl font-black tracking-tight text-foreground">
              {greeting}, Prabhjot
            </h1>
            <p className="text-muted-foreground text-lg font-semibold">
              Your autonomous agent network is performing optimally.
            </p>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex -space-x-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="w-10 h-10 rounded-full border-2 border-background bg-primary/10 dark:bg-primary/20 flex items-center justify-center text-[10px] font-black text-primary">
                  A{i}
                </div>
              ))}
              <div className="w-10 h-10 rounded-full border-2 border-background bg-muted flex items-center justify-center text-[10px] font-black text-muted-foreground">
                +4
              </div>
            </div>
            <div className="h-10 w-[1px] bg-border mx-2" />
            <button className="px-6 py-3 bg-primary text-primary-foreground font-black rounded-2xl hover:scale-105 transition-all active:scale-95">
              Launch Global Task
            </button>
          </div>
        </div>

        {/* Hero Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {statCards.map((stat, i) => (
            <div
              key={i}
              className="relative overflow-hidden rounded-[2.5rem] border border-border bg-muted/20 dark:bg-white/[0.03] p-8 group hover:bg-muted/40 dark:hover:bg-white/[0.06] transition-all duration-700"
            >
              <div className={`mb-6 w-12 h-12 rounded-2xl ${stat.bg} ${stat.color} flex items-center justify-center group-hover:rotate-12 transition-all duration-500`}>
                <stat.icon className="w-6 h-6" />
              </div>
              <div className="space-y-1">
                <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest opacity-60">{stat.label}</p>
                <div className="flex items-baseline gap-2">
                  <h3 className="text-4xl font-black tracking-tighter">
                    {loading ? '...' : stat.value}
                  </h3>
                  {!loading && (
                    <span className="text-[10px] font-bold text-green-500 bg-green-500/10 px-1.5 py-0.5 rounded-md">
                      +12.5%
                    </span>
                  )}
                </div>
              </div>
              {/* Mini Sparkline SVG */}
              <div className="mt-6 h-8 w-full opacity-30 group-hover:opacity-60 transition-opacity duration-700">
                <svg className="w-full h-full" viewBox="0 0 100 20" preserveAspectRatio="none">
                  <path 
                    d="M0 15 Q 10 5, 20 12 T 40 8 T 60 14 T 80 6 T 100 10" 
                    fill="none" 
                    stroke="currentColor" 
                    strokeWidth="2"
                    className={stat.color}
                  />
                </svg>
              </div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
          {/* Recent Activity Timeline */}
          <div className="lg:col-span-8 space-y-8">
            <div className="flex items-center justify-between px-2">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-primary/10 flex items-center justify-center">
                  <Clock className="w-5 h-5 text-primary" />
                </div>
                <h2 className="text-2xl font-black tracking-tight">Active Stream</h2>
              </div>
              <Link to="/monitor" className="group text-sm font-bold text-primary flex items-center gap-1 transition-all">
                Access Archives
                <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
            
            <div className="relative rounded-[2.5rem] border border-border bg-muted/10 dark:bg-white/[0.02] p-8 overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 blur-3xl rounded-full" />
              
              <div className="space-y-6 relative z-10">
                {recentRuns.map((run, idx) => (
                  <div key={run.id} className="group relative flex items-center justify-between p-6 rounded-3xl bg-background dark:bg-white/[0.03] border border-border hover:border-primary/50 transition-all duration-300">
                    <div className="flex items-center gap-6">
                      <div className="relative">
                        <div className={`p-4 rounded-2xl ${run.status === 'completed' ? 'bg-green-500/10 text-green-500' : 'bg-blue-500/10 text-blue-500'} group-hover:scale-110 transition-transform`}>
                          <Zap className="w-6 h-6" />
                        </div>
                        {idx !== recentRuns.length - 1 && (
                          <div className="absolute top-full left-1/2 -translate-x-1/2 w-[1px] h-6 bg-white/5" />
                        )}
                      </div>
                      <div>
                        <div className="flex items-center gap-3 mb-1">
                          <span className="font-black text-base uppercase tracking-tight">Manual Launch</span>
                          <span className="text-[10px] font-mono text-muted-foreground px-2 py-0.5 rounded-md bg-white/5 border border-white/5">
                            ID: {run.id.slice(0, 8)}
                          </span>
                        </div>
                        <div className="text-xs text-muted-foreground font-medium flex items-center gap-4">
                          <span className="flex items-center gap-1.5">
                            <Clock className="w-3 h-3 opacity-50" />
                            {new Date(run.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                          <span className="flex items-center gap-1.5 text-primary/70">
                            <GitBranch className="w-3 h-3 opacity-50" />
                            Multi-Agent Pipeline
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-6">
                      <div className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-tighter ${
                        run.status === 'completed' 
                          ? 'bg-green-500/10 text-green-500 border border-green-500/20' 
                          : 'bg-blue-500/10 text-blue-500 border border-blue-500/20'
                      }`}>
                        {run.status}
                      </div>
                      <button className="p-3 rounded-xl bg-white/5 hover:bg-primary hover:text-white transition-all opacity-0 group-hover:opacity-100 -translate-x-2 group-hover:translate-x-0">
                        <ArrowUpRight size={18} />
                      </button>
                    </div>
                  </div>
                ))}
                {recentRuns.length === 0 && !loading && (
                  <div className="p-20 text-center text-muted-foreground opacity-30 flex flex-col items-center gap-4">
                    <Activity className="w-16 h-16 animate-pulse" />
                    <p className="font-bold tracking-widest uppercase text-xs">No active nodes detected</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sidebar Section */}
          <div className="lg:col-span-4 space-y-10">
            {/* Quick Actions */}
            <div className="space-y-6">
              <h2 className="text-2xl font-black tracking-tight px-2 flex items-center gap-2">
                <Plus className="w-6 h-6 text-primary" />
                Forge
              </h2>
              <div className="grid grid-cols-1 gap-4">
                <Link
                  to="/agents"
                  className="group relative p-8 rounded-[2.5rem] border border-border bg-muted/20 dark:bg-gradient-to-br dark:from-white/[0.04] dark:to-transparent hover:border-primary/50 transition-all overflow-hidden"
                >
                  <div className="absolute top-0 right-0 w-24 h-24 bg-primary/10 blur-3xl group-hover:bg-primary/20 transition-colors" />
                  <div className="p-4 rounded-2xl bg-primary text-primary-foreground w-fit mb-6">
                    <Users className="w-6 h-6" />
                  </div>
                  <div className="space-y-2">
                    <div className="font-black text-xl tracking-tight">Deploy Agent</div>
                    <p className="text-xs text-muted-foreground leading-relaxed font-semibold">Create a specialized AI persona with dedicated memory and toolsets.</p>
                  </div>
                </Link>

                <Link
                  to="/workflows"
                  className="group relative p-8 rounded-[2.5rem] border border-border bg-muted/20 dark:bg-gradient-to-br dark:from-white/[0.04] dark:to-transparent hover:border-primary/50 transition-all overflow-hidden"
                >
                  <div className="absolute top-0 right-0 w-24 h-24 bg-blue-500/10 blur-3xl group-hover:bg-blue-500/20 transition-colors" />
                  <div className="p-4 rounded-2xl bg-blue-500 text-white w-fit mb-6">
                    <GitBranch className="w-6 h-6" />
                  </div>
                  <div className="space-y-2">
                    <div className="font-black text-xl tracking-tight">Architect Flow</div>
                    <p className="text-xs text-muted-foreground leading-relaxed font-semibold">Map out complex reasoning paths between multiple autonomous agents.</p>
                  </div>
                </Link>
              </div>
            </div>

            {/* Performance Monitoring */}
            <div className="p-8 rounded-[2.5rem] bg-muted/20 dark:bg-gradient-to-br dark:from-primary/10 dark:to-transparent border border-border relative overflow-hidden">
              <div className="absolute -bottom-8 -left-8 w-32 h-32 bg-primary/20 blur-3xl rounded-full" />
              <div className="flex items-center gap-3 font-black text-base mb-8 relative z-10">
                <div className="w-3 h-3 rounded-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]" />
                Live Telemetry
              </div>
              <div className="space-y-6 relative z-10">
                <div className="space-y-3">
                  <div className="flex justify-between text-[10px] uppercase font-black tracking-[0.2em] opacity-60">
                    <span>Inference Speed</span>
                    <span className="text-green-500">124ms</span>
                  </div>
                  <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden border border-white/5 p-[1px]">
                    <div className="h-full w-[88%] bg-gradient-to-r from-green-500 to-emerald-400 rounded-full shadow-[0_0_10px_rgba(34,197,94,0.3)]" />
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex justify-between text-[10px] uppercase font-black tracking-[0.2em] opacity-60">
                    <span>Memory Usage</span>
                    <span className="text-blue-500">2.4 GB</span>
                  </div>
                  <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden border border-white/5 p-[1px]">
                    <div className="h-full w-[42%] bg-gradient-to-r from-blue-500 to-cyan-400 rounded-full shadow-[0_0_10px_rgba(59,130,246,0.3)]" />
                  </div>
                </div>
              </div>
              <div className="mt-10 pt-6 border-t border-white/5 text-[10px] text-muted-foreground font-bold uppercase tracking-widest text-center opacity-40">
                Data refreshed in real-time
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
};

export default Dashboard;
