/**
 * Sidebar Navigation Component
 */

import React from 'react';
import {
  Home,
  Bell,
  BarChart3,
  Folder,
  Settings,
  Terminal,
  ShieldAlert,
  Wrench,
} from 'lucide-react';
import '../styles/Sidebar.css';

const NavigationItem = ({ icon: Icon, label, id, active, onClick, badge }) => (
  <button
    onClick={() => onClick(id)}
    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 text-left group ${
      active
        ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20'
        : 'text-zinc-400 hover:bg-zinc-800 hover:text-zinc-300'
    }`}
  >
    <Icon size={18} className={active ? 'text-white' : 'text-zinc-500 group-hover:text-zinc-400'} />
    <span className="text-sm font-medium flex-grow">{label}</span>
    {badge && (
      <span className="text-xs font-bold px-2 py-0.5 bg-red-500 text-white rounded-full">
        {badge}
      </span>
    )}
  </button>
);

const Divider = () => <div className="my-4 border-t border-zinc-800" />;

export default function Sidebar({ activeView, onViewChange }) {
  const mainItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'updates', label: 'Live Updates', icon: Bell, badge: 'Live' },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  ];

  const managementItems = [
    { id: 'projects', label: 'Projects', icon: Folder },
    { id: 'classification', label: 'Classification', icon: ShieldAlert },
    { id: 'honeypot', label: 'Honeypot Config', icon: Wrench },
  ];

  const systemItems = [
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar__header">
        <div className="sidebar__logo">
          <img src="/RedTrace-removebg-preview.png" alt="RedTrace" className="sidebar__logo-img" />
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 pb-4 space-y-1 overflow-y-auto">
        {/* Main Section */}
        <div className="mb-2">
          <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider px-2 mb-2">Main</p>
          <div className="space-y-1">
            {mainItems.map(item => (
              <NavigationItem
                key={item.id}
                {...item}
                active={activeView === item.id}
                onClick={onViewChange}
              />
            ))}
          </div>
        </div>

        <Divider />

        {/* Management Section */}
        <div className="mb-2">
          <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider px-2 mb-2">Management</p>
          <div className="space-y-1">
            {managementItems.map(item => (
              <NavigationItem
                key={item.id}
                {...item}
                active={activeView === item.id}
                onClick={onViewChange}
              />
            ))}
          </div>
        </div>

        <Divider />

        {/* System Section */}
        <div className="mb-2">
          <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider px-2 mb-2">System</p>
          <div className="space-y-1">
            {systemItems.map(item => (
              <NavigationItem
                key={item.id}
                {...item}
                active={activeView === item.id}
                onClick={onViewChange}
              />
            ))}
          </div>
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-zinc-800 flex-shrink-0">
        <div className="px-4 py-3 bg-zinc-900 rounded-lg">
          <p className="text-xs text-zinc-400 mb-1">Version</p>
          <p className="text-sm font-semibold text-white">1.0.0</p>
        </div>
      </div>
    </aside>
  );
}
