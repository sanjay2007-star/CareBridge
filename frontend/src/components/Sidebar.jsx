import React from 'react';
import { 
  LayoutDashboard, Users, FileText, ArrowRightLeft, Clock, 
  UserCheck, ShieldCheck, BarChart3, Scale, Split, Network, 
  AlertTriangle, CheckSquare, History
} from 'lucide-react';

export default function Sidebar({ activeView, setActiveView }) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'demo-c001', label: 'Demo Scenario (C001)', icon: ArrowRightLeft, highlight: true },
    { id: 'clients', label: 'Clients', icon: Users },
    { id: 'handovers', label: 'Handover Screen', icon: Split },
    { id: 'actions', label: 'Pending Actions', icon: Clock },
    { id: 'staff', label: 'Staff Capacity', icon: UserCheck },
    { id: 'consent', label: 'Consent Preferences', icon: ShieldCheck },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'fairness', label: 'Fairness Dashboard', icon: Scale },
    { id: 'before-after', label: 'Before & After Demo', icon: History },
    { id: 'architecture', label: 'Architecture', icon: Network },
    { id: 'risks', label: 'Risk Register', icon: AlertTriangle },
    { id: 'validation', label: 'Stakeholder Survey', icon: CheckSquare },
    { id: 'audit', label: 'Audit Logs', icon: FileText }
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col h-screen sticky top-0">
      <div className="p-5 border-b border-slate-800 flex items-center gap-3">
        <div className="p-2 bg-teal-500/20 text-teal-400 rounded-lg border border-teal-500/30">
          <ShieldCheck className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-bold text-slate-100 text-sm tracking-wide">EAP CONTINUITY</h1>
          <p className="text-xs text-teal-400 font-medium">Consent-Aware System</p>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto p-3 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveView(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                isActive 
                  ? 'bg-teal-500/15 text-teal-300 border border-teal-500/30' 
                  : item.highlight
                  ? 'text-emerald-400 hover:bg-emerald-500/10 border border-emerald-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-teal-400' : item.highlight ? 'text-emerald-400' : 'text-slate-400'}`} />
              <span>{item.label}</span>
              {item.highlight && !isActive && (
                <span className="ml-auto text-[10px] bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded font-semibold uppercase">
                  Required
                </span>
              )}
            </button>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800 text-[11px] text-slate-500 text-center">
        v1.0.0 MVP • Privacy-by-Default
      </div>
    </aside>
  );
}
