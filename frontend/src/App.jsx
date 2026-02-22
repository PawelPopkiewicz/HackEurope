/*
 * Main App Component
 * Entry point with routing and layout
 */

import React, { useState, useEffect } from 'react';
import { Terminal } from 'lucide-react';
import { useNodesState, useEdgesState } from '@xyflow/react';
import './App.css';

import Sidebar from './components/Sidebar';
import ErrorBoundary from './components/ErrorBoundary';
import Home from './components/Home';
import ClassificationDashboard from './components/ClassificationDashboard';
import HoneypotConfig from './components/HoneypotConfig';
import FixerDashboard from './components/FixerDashboard';

// Page imports
import Dashboard from './pages/Dashboard';
import Updates from './pages/Updates';
import Analytics from './pages/Analytics';
import Projects from './pages/Projects';
import Settings from './pages/Settings';

// Default empty states for the React Flow diagram in the Fixer Agent view
const initialNodes = [];
const initialEdges = [];

const NavigationItem = ({ icon: Icon, label, active, onClick }) => (
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
  const [activeView, setActiveView] = useState('home');
  const [status, setStatus] = useState('Connecting...');

  // Lifted Dashboard State
  const [liveLogs, setLiveLogs] = useState([]);
  const [riskScores, setRiskScores] = useState([]);
  const [attackChains, setAttackChains] = useState([]);
  const [latestRisk, setLatestRisk] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [agentPRs, setAgentPRs] = useState([
    { id: 42, title: "Mitigate brute-force IP 1.2.3.4", repo: "HackEurope", status: "PENDING_REVIEW", label: "FIXER" },
    { id: 41, title: "Add rate-limiting to SSH", repo: "Cowrie-Configs", status: "MERGED", label: "AUTO-PATCH" }
  ]);

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
          setRiskScores(prev => [data, ...prev].slice(0, 15));
          setLatestRisk(data);
        } else if (type === 'attack_chain') {
          setAttackChains(prev => [data, ...prev].slice(0, 5));
        } else if (type === 'agent_pr') {
          setAgentPRs(prev => [data, ...prev].slice(0, 5));
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
    switch (activeView) {
      case 'dashboard':
        return <Dashboard />;
      case 'updates':
        return <Updates />;
      case 'analytics':
        return <Analytics />;
      case 'projects':
        return <Projects />;
      case 'settings':
        return <Settings />;
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
            agentPRs={agentPRs}
          />
        );
      default:
        return <Dashboard />;
    }
  };

  return (
    <ErrorBoundary>
      <div className="flex h-screen bg-black text-zinc-300 font-sans selection:bg-blue-500/30">
        {/* Sidebar */}
        <Sidebar activeView={activeView} onViewChange={setActiveView} />

        {/* Main Content */}
        <main className="flex-grow flex flex-col overflow-hidden min-w-0">
          <div className="flex-grow overflow-auto bg-zinc-950">
            {renderContent()}
          </div>
        </main>
      </div>
    </ErrorBoundary>
  );
}
