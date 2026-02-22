import React from 'react';
import { 
  ReactFlow,
} from '@xyflow/react';
import { 
  Zap, 
  Layers, 
  Search,
  Database,
} from 'lucide-react';
import { Panel, MitreItem, MitigationItem, AgentTicketItem, FixSuggestionItem } from './DashboardComponents';

export default function FixerDashboard({ 
  nodes, 
  edges, 
  onNodesChange, 
  onEdgesChange, 
  latestRisk, 
  agentTickets 
}) {
  return (
    <div className="w-full h-full flex flex-col overflow-hidden">
      <div className="px-8 py-6 border-b border-zinc-900 flex-shrink-0">
        <h2 className="text-2xl font-bold text-white mb-1 tracking-tight">Fixer Agent</h2>
        <p className="text-zinc-400 text-sm">Automated mitigations and security patching lifecycle</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 flex-grow p-6 h-full overflow-auto animate-in fade-in duration-1000 slide-in-from-bottom-2">
        
        {/* COLUMN 1: FIXER GRAPH */}
        <div className="xl:col-span-2 flex flex-col gap-6 h-full min-h-[400px]">
          <Panel title="Mitigation Workflow" icon={Database} color="bg-blue-600" glowColor="bg-blue-500">
            <div className="h-full w-full bg-zinc-950/50 rounded-lg overflow-hidden border border-zinc-900">
              <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                nodesDraggable={false}
                fitView
              />
            </div>
          </Panel>
        </div>

        {/* COLUMN 2: MITRE & MITIGATIONS (Stacked) */}
        <div className="flex flex-col gap-6 h-full">
          <div className="h-1/3 min-h-[200px]">
            <Panel title="MITRE ATT&CK Tracking" icon={Layers} color="bg-blue-400" glowColor="bg-blue-300">
              {!latestRisk?.mitre_attack ? (
                <div className="flex flex-col items-center justify-center h-full text-zinc-600 uppercase font-bold text-[9px] text-center px-8">
                  Awaiting classification data...
                </div>
              ) : (
                latestRisk.mitre_attack.map((m, i) => <MitreItem key={i} data={m} />)
              )}
            </Panel>
          </div>
          
          <div className="h-1/3 min-h-[200px]">
            <Panel title="Mitigations" icon={Search} color="bg-emerald-400" glowColor="bg-emerald-300">
              {!latestRisk?.mitigations ? (
                <div className="flex flex-col items-center justify-center h-full text-zinc-600 uppercase font-bold text-[9px] text-center px-8">
                  Actionable mitigations will appear here
                </div>
              ) : (
                <>
                  {latestRisk.mitigations.map((m, i) => <MitigationItem key={i} data={m} />)}
                  {latestRisk.fix_suggestion && (
                    <FixSuggestionItem suggestion={latestRisk.fix_suggestion} />
                  )}
                </>
              )}
            </Panel>
          </div>

          <div className="h-1/3 min-h-[200px]">
            <Panel title="Agent Tickets" icon={Zap} color="bg-indigo-600" glowColor="bg-indigo-500">
              {(!agentTickets || agentTickets.length === 0) ? (
                <div className="flex flex-col items-center justify-center h-full text-zinc-500 uppercase font-black text-[10px]">
                  Standing By...
                </div>
              ) : (
                agentTickets.map((t, i) => <AgentTicketItem key={i} data={t} />)
              )}
            </Panel>
          </div>
        </div>

      </div>
    </div>
  );
}
