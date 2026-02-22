import React, { useEffect, useState } from 'react';
import {
  ReactFlow,
  useNodesState,
  useEdgesState,
} from '@xyflow/react';
import { Settings, Shield, Wrench, Activity, Home as HomeIcon, FileSliders, Terminal } from 'lucide-react';
import '@xyflow/react/dist/style.css';
import './App.css';
import HoneypotConfig from './components/HoneypotConfig';
import Home from './components/Home';

import ClassificationDashboard from './components/ClassificationDashboard';
import FixerDashboard from './components/FixerDashboard';

const initialNodes = [];
const initialEdges = [];

const SidebarItem = ({ icon: Icon, label, active, onClick }) => (
    <div
    onClick={onClick}
    className={`flex items-center gap-3 px-4 py-3 cursor-pointer rounded-lg transition-all duration-200 mb-1 
      ${active ? 'bg-blue-600 text-white font-medium shadow-lg shadow-blue-500/20' : 'text-zinc-400 hover:bg-zinc-900'}`}
  >
    <Icon size={18} className={active ? 'text-white' : 'text-zinc-500'} />
    <span className="text-sm">{label}</span>
  </div>
);

export default function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [activeTab, setActiveTab] = useState('home');
  const [status, setStatus] = useState('Connecting...');

  // Lifted Dashboard State
  const [liveLogs, setLiveLogs] = useState([]);
  const [riskScores, setRiskScores] = useState([]);
  const [attackChains, setAttackChains] = useState([]);
  const [latestRisk, setLatestRisk] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [agentTickets, setAgentTickets] = useState([]);

  useEffect(() => {
    const source = new EventSource('http://localhost:8000/api/v1/dashboard/stream');
    
    source.onopen = () => setStatus('Connected');

    source.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const type = data.type || (data.eventid ? 'live_log' : null);

        if (type === 'live_log') {
          setLiveLogs(prev => [data, ...prev].slice(0, 20));
          setIsProcessing(true);
        } else if (type === 'risk_score') {
          const scored = { ...data, _uid: crypto.randomUUID() };
          setRiskScores(prev => [scored, ...prev].slice(0, 15));
          setLatestRisk(scored);
        } else if (type === 'attack_chain') {
          setAttackChains(prev => [data, ...prev].slice(0, 5));
        } else if (type === 'agent_pr' || type === 'agent_ticket') {
          setAgentTickets(prev => [data, ...prev].slice(0, 5));
        } else if (type === 'pipeline_finished') {
          setIsProcessing(false);
        }
      } catch (err) {
        console.error("Error parsing dashboard push:", err);
      }
    };

    source.onerror = (err) => {
      console.error("Dashboard stream error:", err);
      setStatus('Error');
      source.close();
    };

    return () => source.close();
  }, []);

  const renderContent = () => {
    switch (activeTab) {
      case 'home':
        return <Home />;
      case 'honeypot':
        return <HoneypotConfig />;
      case 'classification':
        return (
          <div className="w-full h-full flex flex-col">
            <div className="px-8 py-6 border-b border-zinc-900 flex-shrink-0">
               <h2 className="text-2xl font-bold text-white mb-1 tracking-tight">Classification Agent</h2>
               <p className="text-zinc-400 text-sm">Real-time threat intelligence and automated rule matching</p>
            </div>
            <div className="flex-grow overflow-hidden">
               <ClassificationDashboard 
                 liveLogs={liveLogs}
                 riskScores={riskScores}
                 attackChains={attackChains}
                 latestRisk={latestRisk}
                 setLatestRisk={setLatestRisk}
                 isProcessing={isProcessing}
               />
            </div>
          </div>
        );
      case 'fixer':
        return (
          <FixerDashboard 
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            latestRisk={latestRisk}
            agentTickets={agentTickets}
          />
        );
      default:
        return <Home />;
    }
  };

  return (
    <div className="flex h-screen bg-black text-zinc-300 font-sans selection:bg-blue-500/30">
      {/* Sidebar */}
      <aside className="w-72 bg-zinc-950 border-r border-zinc-900 flex flex-col shadow-2xl z-10 flex-shrink-0">
        <div className="p-8">
          <div className="flex items-center gap-3 group">
            <img src="/RedTrace-removebg-preview.png" alt="Logo" className="w-30 h-30 object-contain" />
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-2">
          <SidebarItem 
            icon={HomeIcon} 
            label="Home" 
            active={activeTab === 'home'} 
            onClick={() => setActiveTab('home')} 
          />
          <div className="my-6 border-t-2 border-zinc-800 mx-4 opacity-50" />
          <SidebarItem 
            icon={Settings} 
            label="Configure Honey Pot" 
            active={activeTab === 'honeypot'} 
            onClick={() => setActiveTab('honeypot')} 
          />
          <SidebarItem 
            icon={Shield} 
            label="Classification Agent" 
            active={activeTab === 'classification'} 
            onClick={() => setActiveTab('classification')} 
          />
          <SidebarItem 
            icon={Wrench} 
            label="Fixer Agent" 
            active={activeTab === 'fixer'} 
            onClick={() => setActiveTab('fixer')} 
          />
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-grow flex flex-col overflow-hidden min-w-0">
        <header className="px-6 py-4 bg-zinc-950 border-b border-zinc-900 flex justify-between items-center flex-shrink-0">
          <span className="text-sm text-zinc-400">
            Current View: <strong className="text-white capitalize">{activeTab.replace('_', ' ')}</strong>
          </span>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${status === 'Connected' ? 'bg-emerald-500' : 'bg-red-500'}`} />
            <span className="text-xs text-zinc-400">{status}</span>
          </div>
        </header>
        
        <div className="flex-grow overflow-auto bg-zinc-950/20">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}
