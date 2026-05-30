import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  GitBranch, 
  Activity, 
  ChevronLeft, 
  ChevronRight,
  Moon,
  Sun
} from 'lucide-react';

const Sidebar = ({ isDark, setIsDark, isCollapsed, setIsCollapsed }) => {
  const location = useLocation();
  
  const navItems = [
    { name: 'Dashboard', path: '/', icon: LayoutDashboard },
    { name: 'Agents', path: '/agents', icon: Users },
    { name: 'Workflows', path: '/workflows', icon: GitBranch },
    { name: 'Monitor', path: '/monitor', icon: Activity },
  ];

  return (
    <aside className={`transition-all duration-300 border-r border-border bg-card flex flex-col h-screen relative ${isCollapsed ? 'w-20' : 'w-64'}`}>
      {/* Collapse Toggle */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="absolute -right-3 top-20 bg-background border border-border rounded-full p-1 shadow-md z-50 hover:text-primary transition-colors"
      >
        {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>

      {/* Logo */}
      <div className={`p-6 flex items-center gap-3 border-b border-border overflow-hidden whitespace-nowrap ${isCollapsed ? 'justify-center' : ''}`}>
        <div className="bg-gradient-to-br from-purple-500 to-blue-500 p-2 rounded-lg shrink-0">
          <span className="text-xl font-bold text-white">⚡</span>
        </div>
        {!isCollapsed && (
          <div className="animate-in fade-in duration-300">
            <h1 className="font-bold text-lg tracking-tight">AgentFlow</h1>
            <p className="text-xs text-muted-foreground">Agent Platform</p>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            title={isCollapsed ? item.name : ''}
            className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-all duration-200 ${
              location.pathname === item.path
                ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20'
                : 'text-muted-foreground hover:bg-accent'
            } ${isCollapsed ? 'justify-center px-0' : ''}`}
          >
            <item.icon size={20} className="shrink-0" />
            {!isCollapsed && <span className="animate-in fade-in duration-300">{item.name}</span>}
          </Link>
        ))}
      </nav>

      {/* Dark Mode Toggle */}
      <div className="p-4 border-t border-border overflow-hidden whitespace-nowrap">
        <button
          onClick={() => setIsDark(!isDark)}
          className={`w-full flex items-center rounded-xl hover:bg-accent transition-all duration-200 ${isCollapsed ? 'justify-center p-2' : 'justify-between px-4 py-3'}`}
        >
          <div className="flex items-center gap-3">
            {isDark ? <Moon size={20} /> : <Sun size={20} />}
            {!isCollapsed && <span className="text-sm font-medium animate-in fade-in duration-300">{isDark ? 'Dark Mode' : 'Light Mode'}</span>}
          </div>
          {!isCollapsed && (
            <div className={`w-8 h-4 rounded-full relative transition-colors ${isDark ? 'bg-primary' : 'bg-gray-300'}`}>
              <div className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-all ${isDark ? 'translate-x-4' : 'translate-x-0.5'}`} />
            </div>
          )}
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
