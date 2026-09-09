import React from 'react';
import { Network, ShieldCheck, Database, Server, Cpu, Lock, CheckCircle2 } from 'lucide-react';

export default function ArchitectureView() {
  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex justify-between items-center">
        <div>
          <h2 className="text-sm font-bold text-slate-100">System Architecture &amp; Privacy Boundaries</h2>
          <p className="text-xs text-slate-400 mt-1">Section 19 Compliance: End-to-end data pipeline and deterministic privacy safeguards.</p>
        </div>
      </div>

      {/* Architecture Flow Box */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
        <h3 className="text-xs font-bold text-slate-200 border-b border-slate-800 pb-3">
          Pipeline Processing Architecture Diagram
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2 text-center">
            <div className="p-2 bg-teal-500/20 text-teal-400 rounded-lg w-fit mx-auto">
              <Server className="w-5 h-5" />
            </div>
            <div className="text-xs font-bold text-slate-200">1. React Dashboard</div>
            <p className="text-[11px] text-slate-400">Split-screen handover interface, persona switcher, and Recharts analytics UI.</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-teal-500/40 space-y-2 text-center">
            <div className="p-2 bg-teal-500/20 text-teal-400 rounded-lg w-fit mx-auto">
              <Lock className="w-5 h-5" />
            </div>
            <div className="text-xs font-bold text-teal-300">2. RBAC &amp; Consent Engine</div>
            <p className="text-[11px] text-slate-400">Mandatory privacy boundary verifying explicit active client consent for category and recipient role.</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-indigo-500/40 space-y-2 text-center">
            <div className="p-2 bg-indigo-500/20 text-indigo-400 rounded-lg w-fit mx-auto">
              <Cpu className="w-5 h-5" />
            </div>
            <div className="text-xs font-bold text-indigo-300">3. Continuity Engine</div>
            <p className="text-[11px] text-slate-400">Generates structured handover, computes confidence score (0.0 to 1.0), and enforces safe fallbacks.</p>
          </div>

          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2 text-center">
            <div className="p-2 bg-emerald-500/20 text-emerald-400 rounded-lg w-fit mx-auto">
              <Database className="w-5 h-5" />
            </div>
            <div className="text-xs font-bold text-slate-200">4. SQLite &amp; Audit DB</div>
            <p className="text-[11px] text-slate-400">SQLAlchemy ORM database with full audit trail logging for all access and consent updates.</p>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-teal-500/10 border border-teal-500/30 text-xs text-teal-300 space-y-1">
          <div className="font-bold flex items-center gap-1.5">
            <ShieldCheck className="w-4 h-4 text-teal-400" />
            <span>Deterministic Privacy Boundary Rule:</span>
          </div>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            No session note may enter a handover summary merely because it appeared in prior sessions. Information MUST explicitly pass deterministic consent status check, recipient role matching, and sensitivity filtering prior to summary generation.
          </p>
        </div>
      </div>
    </div>
  );
}
