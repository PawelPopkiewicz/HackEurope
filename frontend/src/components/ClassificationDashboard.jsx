import React, { useState, useEffect, useRef } from 'react';
import { 
  Activity, 
  Zap, 
  Layers, 
  ChevronRight,
  ChevronDown,
  Wifi,
  Radio,
  Search,
  Database,
  Cpu,
  Shield,
  BookOpen
} from 'lucide-react';

const Panel = ({ title, icon: Icon, children, color, glowColor }) => (
  <div className={`bg-zinc-950 border border-zinc-900 rounded-xl flex flex-col h-full shadow-lg overflow-hidden group/panel`}>
    <div className="px-5 py-4 border-b border-zinc-900 flex justify-between items-center bg-zinc-900/20">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg ${color} bg-opacity-20 relative`}>
          <div className={`absolute inset-0 rounded-lg ${glowColor} opacity-0 group-hover/panel:opacity-40 blur-md transition-opacity duration-500`} />
          <Icon className={`${color.replace('bg-', 'text-').replace('-600', '-400').replace('-500', '-400')} relative z-10`} size={18} />
        </div>
        <h3 className="font-bold text-white tracking-tight group-hover/panel:text-blue-400 transition-colors duration-300">{title}</h3>
      </div>
    </div>
    <div className="flex-grow overflow-auto p-4 custom-scrollbar bg-black/20">
      {children}
    </div>
  </div>
);

const LogItem = ({ data }) => (
  <div className="mb-2 p-3 font-mono text-[11px] bg-black/40 rounded border border-zinc-800/50 hover:border-zinc-700 hover:bg-zinc-900/40 transition-all duration-200 group/item">
    <div className="flex justify-between mb-1">
      <span className="text-blue-400/80">[{data?.timestamp}]</span>
      <span className="text-zinc-600 flex items-center gap-1 uppercase">{data?.eventid}</span>
    </div>
    <div className="text-zinc-400">{data?.message || data?.input}</div>
    {data?.src_ip && (
      <div className="text-zinc-500 mt-2 flex items-center gap-2">
        <span className="px-1.5 py-0.5 bg-zinc-900 rounded text-[9px] uppercase font-bold">IP</span>
        <span>{data?.src_ip}</span>
      </div>
    )}
  </div>
);

const RiskItem = ({ data }) => {
  const [expanded, setExpanded] = useState(false);
  const hasMitre = data?.mitre_attack && data.mitre_attack.length > 0;
  const hasMitigations = data?.mitigations && data.mitigations.length > 0;
  const hasDetails = hasMitre || hasMitigations;

  return (
    <div className="mb-3 bg-zinc-900/20 rounded-lg flex flex-col border border-zinc-900 hover:border-zinc-700 transition-all duration-300">
      <div className="p-3 flex flex-col gap-3">
        <div className="flex items-center gap-4">
          <div className="relative w-10 h-10 flex-shrink-0">
            <div className="absolute inset-0 rounded-full border-2" style={{ borderColor: data?.colour || '#f59e0b' }} />
            <div className="absolute inset-0 flex items-center justify-center text-[10px] font-black text-white">
              {data?.score ?? 50}
            </div>
          </div>
          <div className="flex-grow min-w-0">
            <div className="flex items-center justify-between gap-2">
              <span className="text-[10px] font-black uppercase" style={{ color: data?.colour || '#f59e0b' }}>
                {data?.severity || 'MEDIUM'}
              </span>
              <span className="text-[9px] text-zinc-600 truncate">{data?.timestamp}</span>
            </div>
            <h4 className="text-xs font-bold text-white truncate uppercase">{data?.eventid || 'THREAT-ANALYSIS'}</h4>
            {data?.analysis?.confidence && (
              <span className="text-[9px] text-zinc-500 uppercase">confidence: {data.analysis.confidence}</span>
            )}
          </div>
        </div>
        {data?.summary && (
          <div className="text-[10px] text-zinc-400 leading-relaxed border-l-2 border-zinc-800 pl-3 py-1 italic bg-black/20 rounded-r">
            {data.summary}
          </div>
        )}
        {hasDetails && (
          <button
            onClick={() => setExpanded(prev => !prev)}
            className="flex items-center gap-1 text-[9px] uppercase font-bold text-zinc-500 hover:text-blue-400 transition-colors duration-200 self-start"
          >
            {expanded ? <ChevronDown size={10} /> : <ChevronRight size={10} />}
            {expanded ? 'Hide' : 'Show'} MITRE Details
          </button>
        )}
      </div>

      {expanded && hasDetails && (
        <div className="border-t border-zinc-900 px-3 pb-3 pt-2 flex flex-col gap-3">
          {hasMitre && (
            <div>
              <div className="flex items-center gap-1 mb-2">
                <Shield size={10} className="text-blue-400" />
                <span className="text-[9px] font-black uppercase text-blue-400">MITRE ATT&CK</span>
              </div>
              <div className="flex flex-col gap-2">
                {data.mitre_attack.map((attack, idx) => (
                  <div key={idx} className="bg-black/30 rounded p-2 border border-zinc-800/60">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <span className="text-[9px] px-1.5 py-0.5 bg-blue-900/40 border border-blue-800/50 rounded text-blue-300 font-mono font-bold">{attack.tactic_id}</span>
                      <span className="text-[9px] text-zinc-400 font-bold uppercase">{attack.tactic_name}</span>
                      <ChevronRight size={8} className="text-zinc-600" />
                      <span className="text-[9px] px-1.5 py-0.5 bg-purple-900/40 border border-purple-800/50 rounded text-purple-300 font-mono font-bold">{attack.technique_id}</span>
                      <span className="text-[9px] text-zinc-400 font-bold uppercase">{attack.technique_name}</span>
                    </div>
                    {attack.evidence && attack.evidence.length > 0 && (
                      <div className="mt-1.5">
                        <span className="text-[8px] font-bold uppercase text-zinc-600 block mb-1">Evidence:</span>
                        {attack.evidence.map((ev, eidx) => (
                          <div key={eidx} className="text-[9px] font-mono text-emerald-400/80 bg-zinc-950/50 rounded px-2 py-0.5 mb-0.5 truncate">{ev}</div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {hasMitigations && (
            <div>
              <div className="flex items-center gap-1 mb-2">
                <BookOpen size={10} className="text-amber-400" />
                <span className="text-[9px] font-black uppercase text-amber-400">Mitigations</span>
              </div>
              <div className="flex flex-col gap-1.5">
                {data.mitigations.map((mit, idx) => (
                  <div key={idx} className="bg-black/30 rounded p-2 border border-zinc-800/60">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-[9px] px-1.5 py-0.5 bg-amber-900/40 border border-amber-800/50 rounded text-amber-300 font-mono font-bold">{mit.mitigation_id}</span>
                      <span className="text-[9px] text-zinc-300 font-bold">{mit.mitigation_name}</span>
                    </div>
                    <p className="text-[9px] text-zinc-500 leading-relaxed">{mit.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const AttackChainItem = ({ data }) => (
  <div className="mb-4 bg-zinc-950/40 border border-zinc-900 rounded-xl overflow-hidden group/chain hover:border-zinc-700 transition-all duration-300">
    <div className="p-3 border-b border-zinc-900 flex justify-between items-center bg-zinc-900/20">
      <h4 className="text-[10px] font-black text-white uppercase">{data?.chain_id || 'ATTACK-CHAIN'}</h4>
      <span className="text-[9px] text-zinc-600 uppercase">{data?.detected_at}</span>
    </div>
    <div className="p-3">
       <div className="text-[11px] text-blue-400 mb-1 font-bold uppercase">{data?.technique}</div>
       <div className="text-[10px] text-zinc-500 mb-4">{data?.attacker_ip}</div>
       
       {data?.stages && (
         <div className="space-y-4 relative before:absolute before:left-[5px] before:top-2 before:bottom-2 before:w-[1px] before:bg-zinc-800">
           {data.stages.map((stage, idx) => (
             <div key={idx} className="relative pl-6">
               <div className="absolute left-0 top-1.5 w-2.5 h-2.5 rounded-full bg-zinc-900 border border-zinc-700 group-hover/chain:bg-blue-600 group-hover/chain:border-blue-400 transition-colors duration-500" />
               <div className="text-[10px] font-black text-zinc-300 uppercase mb-1 tracking-wider">{stage.name}</div>
               <div className="text-[9px] text-zinc-500 leading-relaxed font-medium capitalize">{stage.desc}</div>
             </div>
           ))}
         </div>
       )}
    </div>
  </div>
);

export default function ClassificationDashboard() {
  const [liveLogs, setLiveLogs] = useState([]);
  const [riskScores, setRiskScores] = useState([]);
  const [attackChains, setAttackChains] = useState([]);

  useEffect(() => {
    const source = new EventSource('http://localhost:8000/api/v1/dashboard/stream');
    
    source.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const type = data.type || (data.eventid ? 'live_log' : null);

        if (type === 'live_log') {
          setLiveLogs(prev => [data, ...prev].slice(0, 20));
        } else if (type === 'risk_score') {
          setRiskScores(prev => [data, ...prev].slice(0, 15));
        } else if (type === 'attack_chain') {
          setAttackChains(prev => [data, ...prev].slice(0, 5));
        }
      } catch (err) {
        console.error("Error parsing dashboard push:", err);
      }
    };

    source.onerror = (err) => {
      console.error("Dashboard stream error:", err);
      source.close();
    };

    return () => source.close();
  }, []);

  return (
    <div className="grid grid-cols-1 xl:grid-cols-2 grid-rows-2 gap-6 h-full p-6 animate-in fade-in duration-1000 slide-in-from-bottom-2">
      <Panel title="Real-time Feed" icon={Cpu} color="bg-blue-600" glowColor="bg-blue-500">
        {liveLogs.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-zinc-500 uppercase font-black text-[10px]">
            Waiting for Uplink...
          </div>
        ) : (
          liveLogs.map((log, i) => <LogItem key={i} data={log} />)
        )}
      </Panel>

      <Panel title="Live Diagnostics" icon={Activity} color="bg-orange-600" glowColor="bg-orange-500">
        {riskScores.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-zinc-500 uppercase font-black text-[10px]">
            Awaiting Data...
          </div>
        ) : (
          riskScores.map((score, i) => <RiskItem key={i} data={score} />)
        )}
      </Panel>

      <div className="xl:col-span-2">
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
  );
}
