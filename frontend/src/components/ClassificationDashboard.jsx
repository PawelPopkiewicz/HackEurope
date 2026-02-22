import React from 'react';
import { 
  Activity, 
  Database,
  Cpu,
  ShieldOff,
  TrendingUp
} from 'lucide-react';
import { Panel, LogItem, RiskItem, AttackChainItem } from './DashboardComponents';

export default function ClassificationDashboard({ 
  liveLogs, 
  riskScores, 
  attackChains, 
  latestRisk, 
  setLatestRisk, 
  isProcessing,
  blockedIps = []
}) {
  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Mini status bar */}
      {isProcessing && (
        <div className="mx-6 mt-4 p-2 bg-blue-600/10 border border-blue-500/20 rounded-lg flex items-center justify-center gap-3 animate-pulse">
           <Cpu className="text-blue-400 animate-spin" size={12} />
           <span className="text-[10px] font-black text-blue-400 uppercase tracking-widest">
             AI Agents analyzing threat landscape...
           </span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 flex-grow p-6 h-full overflow-auto animate-in fade-in duration-1000 slide-in-from-bottom-2">
        
        {/* COLUMN 1: LIVE FEED */}
        <div className="flex flex-col gap-6 h-full">
          <Panel title="Real-time Feed" icon={Cpu} color="bg-blue-600" glowColor="bg-blue-500">
            {liveLogs.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-zinc-500 uppercase font-black text-[10px]">
                Waiting for Uplink...
              </div>
            ) : (
              liveLogs.map((log, i) => <LogItem key={i} data={log} />)
            )}
          </Panel>
        </div>

        {/* COLUMN 2: DIAGNOSTICS, CORRELATION & BLOCKED IPs */}
        <div className="flex flex-col gap-6 h-full">
          <div className="h-1/3 min-h-[200px]">
            <Panel title="Live Diagnostics" icon={Activity} color="bg-orange-600" glowColor="bg-orange-500">
              {riskScores.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-zinc-500 uppercase font-black text-[10px]">
                  Awaiting Data...
                </div>
              ) : (
                riskScores.map((score, i) => (
                  <RiskItem 
                    key={i} 
                    data={score} 
                    active={latestRisk?.timestamp === score.timestamp}
                    onClick={() => setLatestRisk(score)}
                  />
                ))
              )}
            </Panel>
          </div>
          <div className="h-1/3 min-h-[200px]">
            <Panel title="Attack Correlation" icon={Database} color="bg-emerald-600" glowColor="bg-emerald-500">
              {attackChains.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-zinc-500 uppercase font-black text-[10px]">
                  Monitoring Patterns...
                </div>
              ) : (
                attackChains.map((chain, i) => <AttackChainItem key={i} data={chain} />)
              )}
            </Panel>
          </div>
          <div className="h-1/3 min-h-[200px]">
            <Panel title="Blocked IPs" icon={ShieldOff} color="bg-red-600" glowColor="bg-red-500">
              {blockedIps.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-zinc-500 uppercase font-black text-[10px]">
                  No IPs Blocked
                </div>
              ) : (
                blockedIps.map((ip, i) => (
                  <div key={ip} className="mb-2 px-3 py-2 bg-red-900/10 border border-red-900/30 rounded-lg flex items-center gap-3">
                    <ShieldOff className="text-red-400 flex-shrink-0" size={12} />
                    <span className="text-[11px] font-mono text-red-300">{ip}</span>
                  </div>
                ))
              )}
            </Panel>
          </div>
        </div>

      </div>
    </div>
  );
}
