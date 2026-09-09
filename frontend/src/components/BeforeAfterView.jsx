import React from 'react';
import { History, XCircle, CheckCircle2, ShieldCheck, ArrowRight } from 'lucide-react';

export default function BeforeAfterView({ setActiveView }) {
  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex justify-between items-center">
        <div>
          <h2 className="text-sm font-bold text-slate-100">Before vs After Demonstration</h2>
          <p className="text-xs text-slate-400 mt-1">Section 18 Compliance: Visualizing client experience transformation during inter-professional transfers.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* BEFORE CARD */}
        <div className="glass-panel p-6 rounded-2xl border border-rose-500/30 bg-rose-950/10 space-y-4">
          <div className="flex items-center justify-between border-b border-rose-500/20 pb-3">
            <div className="flex items-center gap-2">
              <XCircle className="w-5 h-5 text-rose-400" />
              <h3 className="text-sm font-bold text-rose-300">BEFORE: Traditional Handover Flow</h3>
            </div>
            <span className="px-2.5 py-1 rounded bg-rose-500/20 text-rose-300 text-[10px] font-mono font-bold">
              75.95% Client Repetition
            </span>
          </div>

          <div className="space-y-3 text-xs text-slate-300">
            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <div className="font-semibold text-rose-400">1. Incomplete Transfer Context</div>
              <p className="text-[11px] text-slate-400">New professional receives minimal or raw un-summarized notes, lacking clear structured goals or pending actions.</p>
            </div>

            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <div className="font-semibold text-rose-400">2. Repetitive Client Questioning</div>
              <p className="text-[11px] text-slate-400">Client is forced to re-explain sensitive traumatic personal histories, causing distress and dissatisfaction with EAP support.</p>
            </div>

            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <div className="font-semibold text-rose-400">3. Privacy Boundary Risks</div>
              <p className="text-[11px] text-slate-400">Full raw counselling notes are transferred without verifying explicit consent per recipient role, increasing privacy leakage risk.</p>
            </div>
          </div>
        </div>

        {/* AFTER CARD */}
        <div className="glass-panel p-6 rounded-2xl border border-emerald-500/40 bg-emerald-950/10 space-y-4">
          <div className="flex items-center justify-between border-b border-emerald-500/30 pb-3">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <h3 className="text-sm font-bold text-emerald-300">AFTER: Consent-Aware Continuity System</h3>
            </div>
            <span className="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-mono font-bold">
              91.52% Repetition Reduction
            </span>
          </div>

          <div className="space-y-3 text-xs text-slate-300">
            <div className="p-3 rounded-xl bg-slate-950 border border-emerald-500/30 space-y-1">
              <div className="font-semibold text-emerald-400">1. Deterministic Privacy Boundaries</div>
              <p className="text-[11px] text-slate-400">Session data passes through code-enforced consent checks before summary generation. Unconsented topics are automatically excluded.</p>
            </div>

            <div className="p-3 rounded-xl bg-slate-950 border border-emerald-500/30 space-y-1">
              <div className="font-semibold text-emerald-400">2. Authoritative Structured Summary</div>
              <p className="text-[11px] text-slate-400">Receiving professional immediately gets approved goals, progress notes, and assigned pending actions with zero client re-questioning required.</p>
            </div>

            <div className="p-3 rounded-xl bg-slate-950 border border-emerald-500/30 space-y-1">
              <div className="font-semibold text-emerald-400">3. Safe Fallback Guardrails</div>
              <p className="text-[11px] text-slate-400">Low confidence or contradictory notes automatically trigger human review recommendation rather than displaying inaccurate information.</p>
            </div>
          </div>

          <div className="pt-2 flex justify-end">
            <button
              onClick={() => setActiveView('demo-c001')}
              className="px-4 py-2 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold rounded-xl text-xs flex items-center gap-2"
            >
              <span>Test Live Demo C001</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
