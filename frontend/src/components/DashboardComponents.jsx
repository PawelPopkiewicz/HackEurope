import React from 'react';
import { 
  Activity, 
  Zap, 
  Layers, 
  ChevronRight,
  Wifi,
  Radio,
  Search,
  Database,
  Cpu,
  ShieldCheck,
  Layers as LayersIcon
} from 'lucide-react';

export const Panel = ({ title, icon: Icon, children, color, glowColor }) => (
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

export const LogItem = ({ data }) => (
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

export const RiskItem = ({ data, active, onClick }) => (
  <div 
    onClick={onClick}
    className={`mb-3 p-3 rounded-lg flex flex-col gap-3 border cursor-pointer transition-all duration-300 group
      ${active ? 'bg-zinc-800/40 border-zinc-600' : 'bg-zinc-900/20 border-zinc-900 hover:bg-zinc-800/20'}`}
  >
    <div className="flex items-center gap-4">
      <div className="relative w-10 h-10 flex-shrink-0">
        <div className={`absolute inset-0 rounded-full border-2 border-zinc-800`} />
        <div className="absolute inset-0 flex items-center justify-center text-[10px] font-black text-white">
          {data?.score || 50}
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
      </div>
    </div>
    {data?.summary && (
      <div className="text-[10px] text-zinc-400 leading-relaxed border-l-2 border-zinc-800 pl-3 py-1 italic bg-black/20 rounded-r">
        {data.summary}
      </div>
    )}
    {active && data?.mitre_attack && data.mitre_attack.length > 0 && (
      <div className="space-y-1 pt-1 border-t border-zinc-800">
        <div className="text-[9px] font-black text-zinc-500 uppercase tracking-widest mb-1">MITRE ATT&CK</div>
        {data.mitre_attack.map((t, i) => (
          <div key={i} className="flex items-start gap-2 p-1.5 bg-blue-900/10 border border-blue-900/20 rounded">
            <span className="text-[9px] font-black text-blue-400 shrink-0 bg-blue-500/10 px-1 rounded">{t.technique_id}</span>
            <span className="text-[9px] text-zinc-300 font-bold uppercase leading-tight">{t.technique_name}</span>
          </div>
        ))}
      </div>
    )}
    {active && data?.mitigations && data.mitigations.length > 0 && (
      <div className="space-y-1 pt-1 border-t border-zinc-800">
        <div className="text-[9px] font-black text-zinc-500 uppercase tracking-widest mb-1">Mitigations</div>
        {data.mitigations.map((m, i) => (
          <div key={i} className="flex items-start gap-2 p-1.5 bg-emerald-900/10 border border-emerald-900/20 rounded">
            <ShieldCheck className="text-emerald-500 shrink-0 mt-0.5" size={10} />
            <span className="text-[9px] text-zinc-300 font-bold uppercase leading-tight">{m.mitigation_name}</span>
          </div>
        ))}
      </div>
    )}
  </div>
);

export const AttackChainItem = ({ data }) => (
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

export const MitreItem = ({ data }) => (
  <div className="mb-3 p-3 bg-zinc-900/10 border border-zinc-900 rounded-lg hover:border-zinc-700 transition-colors">
    <div className="flex justify-between items-start mb-2">
      <div className="flex items-center gap-2">
        <div className="p-1 rounded bg-blue-700/10 text-blue-400">
          <LayersIcon size={14} />
        </div>
        <span className="text-[9px] font-black text-blue-300 uppercase tracking-tighter bg-blue-500/5 px-1.5 py-0.5 rounded">
          {data.technique_id}
        </span>
      </div>
      <span className="text-[10px] font-bold text-white uppercase text-right leading-none">
        {data.technique_name}
      </span>
    </div>
    <div className="text-[9px] text-zinc-400 font-bold uppercase mb-1">Tactic: {data.tactic_name}</div>
    {data.evidence && (
      <div className="mt-2 space-y-1">
        {data.evidence.map((ev, i) => (
          <div key={i} className="text-[9px] text-zinc-300 italic bg-black/20 p-1 rounded">
            • {ev}
          </div>
        ))}
      </div>
    )}
  </div>
);

export const MitigationItem = ({ data }) => (
  <div className="mb-2 p-3 bg-emerald-900/5 border border-emerald-900/20 rounded-lg hover:bg-emerald-900/10 transition-colors">
    <div className="flex items-center gap-3 mb-1">
      <div className="p-1 rounded bg-emerald-700/10 text-emerald-400">
        <ShieldCheck size={14} />
      </div>
      <span className="text-[10px] font-black text-emerald-300 uppercase">{data.mitigation_name}</span>
    </div>
    <p className="text-[10px] text-zinc-300 leading-relaxed">{data.description}</p>
  </div>
);

export const AgentTicketItem = ({ data }) => (
  <div className="mb-3 p-3 bg-zinc-900/20 border border-zinc-800 rounded-lg flex items-center justify-between">
    <div className="flex items-center gap-3">
      <div className="w-8 h-8 rounded bg-indigo-700/10 flex items-center justify-center">
        <Cpu className="text-indigo-400" size={14} />
      </div>
      <div>
        <div className="text-[10px] font-bold text-white">{data.title}</div>
        <div className="text-[9px] text-zinc-500">{data.repo} • {data.branch || 'suggested branch'}</div>
      </div>
    </div>
    <div className="px-2 py-1 bg-zinc-800 rounded text-[9px] font-bold text-zinc-400 uppercase">
      {data.label || data.priority}
    </div>
  </div>
);
