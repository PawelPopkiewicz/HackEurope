import React from 'react';
import { 
  Activity, 
  Database,
  Cpu,
  Layers,
  ShieldCheck
} from 'lucide-react';
import { Panel, LogItem, RiskItem, AttackChainItem, MitreItem, MitigationItem } from './DashboardComponents';

export default function ClassificationDashboard({ 
  liveLogs, 
  riskScores, 
  attackChains, 
  latestRisk, 
  setLatestRisk, 
  isProcessing 
}) {
  const hasMitreDetail = latestRisk?.mitre_attack && latestRisk.mitre_attack.length > 0;
  const hasMitigations = latestRisk?.mitigations && latestRisk.mitigations.length > 0;

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

      <div className="flex flex-col flex-grow p-6 gap-6 overflow-auto animate-in fade-in duration-1000 slide-in-from-bottom-2">

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* COLUMN 1: LIVE FEED */}
          <div className="flex flex-col gap-6 min-h-[300px]">
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

          {/* COLUMN 2: DIAGNOSTICS & CORRELATION */}
          <div className="flex flex-col gap-6">
            <div className="min-h-[300px]">
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
                      active={latestRisk?.timestamp === score.timestamp && latestRisk?.eventid === score.eventid}
                      onClick={() => setLatestRisk(score)}
                    />
                  ))
                )}
              </Panel>
            </div>
            <div className="min-h-[300px]">
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
          </div>

        </div>

        {/* MITRE DETAIL ROW: shown when a risk item with MITRE data is selected */}
        {(hasMitreDetail || hasMitigations) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
            
            {hasMitreDetail && (
              <Panel title="MITRE ATT&CK Techniques" icon={Layers} color="bg-blue-400" glowColor="bg-blue-300">
                {latestRisk.mitre_attack.map((m, i) => <MitreItem key={i} data={m} />)}
              </Panel>
            )}

            {hasMitigations && (
              <Panel title="Recommended Mitigations" icon={ShieldCheck} color="bg-emerald-400" glowColor="bg-emerald-300">
                {latestRisk.mitigations.map((m, i) => <MitigationItem key={i} data={m} />)}
              </Panel>
            )}

          </div>
        )}

      </div>
    </div>
  );
}
