import React, { useState, useEffect, useRef } from 'react';
import { Activity, Terminal, Clock, MessageSquare, Database, AlertCircle, Cpu, FileText, ChevronRight, ChevronLeft } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { runsApi } from '../api/api';

const MemoizedMarkdown = React.memo(({ content, isReport = false }) => {
  if (!content) return null;

  return (
    <ReactMarkdown 
      remarkPlugins={[remarkGfm]}
      components={{
        img: ({node, src, alt, ...props}) => {
          const isBase64 = src?.startsWith('data:image');
          return (
            <div className="my-6 flex flex-col items-center group">
              <div className="relative overflow-hidden rounded-xl bg-black/20 border border-white/10 shadow-2xl transition-all duration-500 hover:border-primary/50">
                <img 
                  src={src} 
                  alt={alt || "Generated Image"} 
                  className={isReport 
                    ? "max-w-full h-auto block mx-auto transition-transform duration-700 group-hover:scale-[1.02]"
                    : "max-w-full max-h-[600px] w-auto h-auto object-contain block mx-auto"
                  } 
                  loading="lazy"
                  onLoad={(e) => {
                    // Force a small delay to ensure rendering engine has caught up
                    e.target.style.opacity = '1';
                  }}
                  onError={(e) => {
                    console.error("Image failed to load:", alt);
                    e.target.src = "https://placehold.co/800x600/1a1a1a/666666?text=Image+Load+Error";
                    e.target.className = "opacity-50 grayscale p-10";
                  }}
                />
                {isBase64 && (
                  <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="bg-black/60 backdrop-blur-md text-[10px] text-white/70 px-2 py-1 rounded-full border border-white/10">
                      AI Generated
                    </span>
                  </div>
                )}
              </div>
              {alt && alt !== "Generated Image" && (
                <p className="mt-3 text-[11px] text-muted-foreground font-medium italic opacity-70 italic tracking-wide">
                  {alt}
                </p>
              )}
            </div>
          );
        },
        p: ({node, ...props}) => <p {...props} className="mb-5 leading-relaxed text-foreground/90 last:mb-0" />,
        pre: ({node, ...props}) => (
          <div className="relative my-6 group">
            <pre {...props} className="bg-[#0d1117] p-5 rounded-xl overflow-x-auto border border-white/5 shadow-inner text-xs font-mono leading-normal" />
            <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
              <div className="w-2 h-2 rounded-full bg-primary/40 animate-pulse" />
            </div>
          </div>
        ),
        code: ({node, inline, ...props}) => (
          inline 
            ? <code {...props} className="bg-primary/10 text-primary-foreground/90 px-1.5 py-0.5 rounded-md font-mono text-[0.85em] border border-primary/20" />
            : <code {...props} />
        ),
        h1: ({node, ...props}) => <h1 {...props} className="text-2xl font-bold text-primary mb-6 mt-8 pb-2 border-b border-white/10" />,
        h2: ({node, ...props}) => <h2 {...props} className="text-xl font-semibold text-primary/90 mb-4 mt-6" />,
        li: ({node, ...props}) => <li {...props} className="mb-2 last:mb-0" />,
        ul: ({node, ...props}) => <ul {...props} className="list-disc pl-5 mb-5 space-y-1" />,
        ol: ({node, ...props}) => <ol {...props} className="list-decimal pl-5 mb-5 space-y-1" />,
      }}
    >
      {content}
    </ReactMarkdown>
  );
}, (prevProps, nextProps) => prevProps.content === nextProps.content);

const LogEntry = React.memo(({ log, index }) => {
  if (!log) return null;
  
  if (log.type === 'log') {
    return (
      <div className="flex items-center gap-3 text-xs text-muted-foreground bg-muted/5 p-2 rounded-lg border border-border/10">
        <span className="opacity-40">{log.timestamp}</span>
        <span className="font-mono">{log.message}</span>
      </div>
    );
  }

  if (log.type === 'message') {
    return (
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-primary/20 flex items-center justify-center">
            <Cpu className="w-3.5 h-3.5 text-primary" />
          </div>
          <span className="text-xs font-bold text-primary">{log.sender}</span>
          <span className="text-[10px] text-muted-foreground">{log.timestamp}</span>
        </div>
        <div className="pl-8">
          <div className="bg-card border border-border/40 rounded-2xl rounded-tl-none p-5 text-sm text-foreground shadow-sm prose prose-invert max-w-none prose-sm overflow-hidden">
            <MemoizedMarkdown content={log.content || log.message || ''} />
          </div>
        </div>
      </div>
    );
  }

  if (log.type === 'error') {
    return (
      <div className="flex items-start gap-3 text-xs text-destructive bg-destructive/10 p-4 rounded-xl border border-destructive/20">
        <AlertCircle className="w-4 h-4 mt-0.5" />
        <div>
          <p className="font-bold mb-1">Execution Error</p>
          <p className="opacity-90">{log.message}</p>
        </div>
      </div>
    );
  }

  return null;
});

const Monitor = () => {
  const [logs, setLogs] = useState([]);
  const [runs, setRuns] = useState([]);
  const [selectedRunMessages, setSelectedRunMessages] = useState([]);
  const [selectedRun, setSelectedRun] = useState(null);
  const [viewMode, setViewMode] = useState('stream'); // 'stream' or 'report'
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const logEndRef = useRef(null);
  const socketRef = useRef(null);

  useEffect(() => {
    fetchRuns();
    setupWebSocket();
    return () => {
      if (socketRef.current) socketRef.current.close();
    };
  }, []);

  useEffect(() => {
    if (logEndRef.current) {
      logEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const fetchRuns = async () => {
    try {
      const data = await runsApi.list();
      setRuns(data);
    } catch (err) {
      console.error('Failed to fetch runs', err);
    }
  };

  const setupWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.hostname === 'localhost' ? '127.0.0.1:8000' : window.location.host;
    const socketUrl = `${protocol}//${host}/ws/logs`;
    
    socketRef.current = new WebSocket(socketUrl);

    socketRef.current.onopen = () => {
      setLogs((prev) => [...prev, {
        type: 'log',
        message: 'Connected to live stream.',
        timestamp: new Date().toLocaleTimeString()
      }]);
    };

    socketRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        console.log("WebSocket message received:", data);
        
        setLogs((prev) => {
          // If logs are empty, just add the first one
          if (prev.length === 0) {
            return [{ ...data, timestamp: new Date().toLocaleTimeString() }];
          }

          // Duplicate detection logic - specifically for 'message' types from agents
          if (data.type === 'message') {
            const isDuplicate = prev.some(l => 
              l.type === 'message' && 
              l.content === data.content && 
              l.sender === data.sender
            );
            if (isDuplicate) return prev;
          }

          // Return everything, limited to last 100 entries for performance
          return [...prev, {
            ...data,
            timestamp: new Date().toLocaleTimeString()
          }].slice(-100);
        });
        
        if (data.type === 'log' && data.message.includes('completed')) {
          fetchRuns();
        }
      } catch (err) {
        setLogs((prev) => [...prev, {
          type: 'raw',
          message: event.data,
          timestamp: new Date().toLocaleTimeString()
        }].slice(-50));
      }
    };

    socketRef.current.onclose = () => {
      setTimeout(setupWebSocket, 5000);
    };
  };

  const selectRun = async (run) => {
    setSelectedRun(run);
    if (run.status === 'completed' && run.result) {
      setViewMode('report');
    } else {
      setViewMode('stream');
    }

    try {
      const data = await runsApi.getMessages(run.id);
      setSelectedRunMessages(data);
    } catch (err) {
      console.error('Failed to fetch messages', err);
    }
  };

  return (
    <main className="flex-1 flex flex-col overflow-hidden bg-background relative">
      <div className="p-8 pb-4 flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-blue-500 bg-clip-text text-transparent">
            Live Monitor
          </h1>
          <p className="text-muted-foreground mt-2">Real-time execution logs and history</p>
        </div>
        <button 
          onClick={() => setIsHistoryOpen(!isHistoryOpen)}
          className={`flex items-center gap-2 px-6 py-3 rounded-2xl transition-all font-bold text-sm shadow-xl ${
            isHistoryOpen 
              ? 'bg-primary text-primary-foreground scale-95' 
              : 'bg-card border border-border text-foreground hover:bg-accent'
          }`}
        >
          <Clock className="w-4 h-4" />
          {isHistoryOpen ? 'Close History' : 'View Memory & History'}
        </button>
      </div>

      <div className="flex-1 flex p-8 pt-0 overflow-hidden relative">
        <div className="flex-1 flex flex-col bg-card border border-border rounded-2xl overflow-hidden shadow-xl transition-all duration-500">
          <div className="p-4 border-b border-border bg-muted/30 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <button 
                onClick={() => setViewMode('stream')}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all font-medium text-xs ${
                  viewMode === 'stream' ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20' : 'hover:bg-accent text-muted-foreground'
                }`}
              >
                <Terminal className="w-4 h-4" />
                Execution Stream
              </button>
              {selectedRun?.result && (
                <button 
                  onClick={() => setViewMode('report')}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all font-medium text-xs ${
                    viewMode === 'report' ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20' : 'hover:bg-accent text-muted-foreground'
                  }`}
                >
                  <FileText className="w-4 h-4" />
                  Final Report
                </button>
              )}
            </div>
            <div className="flex items-center gap-2 px-3 py-1 bg-background/50 rounded-full border border-border">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
              <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Live</span>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto bg-[#0a0a0c]">
            {viewMode === 'stream' || !selectedRun ? (
              <div className="p-6 space-y-6">
                {/* Historical messages for selected run (if any) */}
                {selectedRun && selectedRunMessages.map((msg, i) => (
                  <div key={`hist-${msg.id || i}`} className="opacity-80">
                    <LogEntry 
                      log={{
                        type: 'message',
                        sender: msg.sender_name || 'System',
                        content: msg.content,
                        timestamp: new Date(msg.created_at).toLocaleTimeString()
                      }} 
                    />
                  </div>
                ))}

                {/* Live logs */}
                {logs.map((log, i) => (
                  <div key={log.id || `${log.run_id}-${i}`} className="animate-in fade-in slide-in-from-bottom-2 duration-500">
                    <LogEntry log={log} index={i} />
                  </div>
                ))}
                
                {logs.length === 0 && (!selectedRun || selectedRunMessages.length === 0) && (
                  <div className="h-full flex flex-col items-center justify-center text-muted-foreground opacity-20 py-20">
                    <Activity className="w-16 h-16 mb-4 animate-pulse" />
                    <p className="text-lg font-medium">Listening for workflow events...</p>
                  </div>
                )}
                <div ref={logEndRef} />
              </div>
            ) : (
              <div className="p-8 max-w-4xl mx-auto animate-in fade-in slide-in-from-bottom-4 duration-700">
                <div className="bg-card border border-border rounded-3xl p-10 shadow-2xl min-h-[600px] relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-purple-500 via-blue-500 to-cyan-500" />
                  <div className="flex justify-between items-center mb-10 border-b border-border pb-6">
                    <div>
                      <h2 className="text-sm font-bold text-primary uppercase tracking-widest mb-1">Polished Output</h2>
                      <p className="text-[10px] font-mono text-muted-foreground">REF: {selectedRun?.id}</p>
                      <div className="mt-2 flex items-center gap-2">
                        <span className="text-[10px] bg-primary/10 text-primary px-2 py-0.5 rounded-full font-bold uppercase tracking-tighter">
                          {selectedRun?.usage_tokens || 0} Tokens
                        </span>
                        <span className="text-[10px] text-muted-foreground font-medium">Est. Cost: ${((selectedRun?.usage_tokens || 0) * 0.000002).toFixed(4)}</span>
                      </div>
                    </div>
                    <div className="flex flex-col items-end">
                      <span className="text-[10px] text-muted-foreground mb-1 uppercase font-bold tracking-tighter">Generated At</span>
                      <span className="text-xs font-medium">{selectedRun?.created_at ? new Date(selectedRun.created_at).toLocaleString() : 'N/A'}</span>
                    </div>
                  </div>
                  <article className="prose prose-invert prose-blue max-w-none prose-headings:text-primary prose-a:text-blue-400 prose-p:leading-relaxed prose-li:my-1">
                    <MemoizedMarkdown content={selectedRun?.result || ''} isReport={true} />
                  </article>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Floating History/Memory Panel */}
        <div className={`absolute right-8 top-0 bottom-8 w-80 bg-card border border-border rounded-2xl shadow-2xl z-40 transition-all duration-500 transform ${
          isHistoryOpen ? 'translate-x-0 opacity-100' : 'translate-x-[120%] opacity-0 pointer-events-none'
        } flex flex-col overflow-hidden`}>
          <div className="p-4 border-b border-border bg-muted/30 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-primary" />
              <span className="font-bold text-sm">Execution History</span>
            </div>
            <button onClick={() => setIsHistoryOpen(false)} className="text-muted-foreground hover:text-foreground">
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {runs.map((run) => (
              <div 
                key={run.id}
                onClick={() => {
                  selectRun(run);
                  setIsHistoryOpen(false);
                }}
                className={`p-4 rounded-xl cursor-pointer transition-all border ${
                  selectedRun?.id === run.id 
                    ? 'bg-primary/10 border-primary/40 shadow-inner' 
                    : 'hover:bg-muted/50 border-transparent bg-muted/20'
                }`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-[10px] font-mono text-muted-foreground bg-background px-1.5 py-0.5 rounded border border-border">
                    #{run.id.slice(0, 8)}
                  </span>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold uppercase tracking-tight ${
                    run.status === 'completed' ? 'bg-green-500/10 text-green-500' : 
                    run.status === 'running' ? 'bg-blue-500/10 text-blue-500 animate-pulse' : 
                    'bg-red-500/10 text-red-500'
                  }`}>
                    {run.status}
                  </span>
                </div>
                <div className="text-xs font-bold truncate mb-1">Manual Execution</div>
                <div className="text-[10px] text-muted-foreground flex items-center gap-1">
                  <Database className="w-3 h-3 opacity-50" />
                  {new Date(run.created_at).toLocaleDateString()} {new Date(run.created_at).toLocaleTimeString()}
                </div>
              </div>
            ))}
            {runs.length === 0 && (
              <div className="py-20 text-center opacity-30 flex flex-col items-center gap-3">
                <Database className="w-10 h-10" />
                <p className="text-xs">No run history found</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  );
};

export default Monitor;
