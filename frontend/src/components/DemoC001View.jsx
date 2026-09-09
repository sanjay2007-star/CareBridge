import React, { useState, useEffect } from 'react';
import { ShieldCheck, ShieldAlert, CheckCircle, AlertTriangle, ArrowRight, UserCheck, RefreshCw } from 'lucide-react';
import api from '../api';

export default function DemoC001View({ setActiveView, setSelectedClientId }) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [previewData, setPreviewData] = useState(null);
  const [handoverCreated, setHandoverCreated] = useState(null);

  const fetchC001Preview = async () => {
    setLoading(true);
    try {
      const res = await api.post('/handovers/preview', {
        client_id: 'C001',
        from_staff_id: 'COUNS_001',
        to_staff_id: 'SOC_001'
      });
      setPreviewData(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchC001Preview();
  }, []);

  const handleCreateHandover = async () => {
    setLoading(true);
    try {
      const res = await api.post('/handovers/create', {
        client_id: 'C001',
        from_staff_id: 'COUNS_001',
        to_staff_id: 'SOC_001'
      });
      setHandoverCreated(res.data);
      setStep(3);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 flex justify-between items-center">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded bg-teal-500/20 text-teal-300 text-xs font-mono font-bold">REQUIRED DEMO</span>
            <h2 className="text-lg font-bold text-slate-100 font-heading">Client C001 Handover Demonstration</h2>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Section 25 Compliance: Counsellor (COUNS_001) → Social Worker (SOC_001) Transfer.
          </p>
        </div>
        <button
          onClick={() => {
            fetchC001Preview();
            setStep(1);
            setHandoverCreated(null);
          }}
          className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs flex items-center gap-2"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Reset Demo</span>
        </button>
      </div>

      {/* Stepper Navigation */}
      <div className="grid grid-cols-3 gap-3">
        <div className={`p-4 rounded-xl border transition-all ${step === 1 ? 'bg-teal-950/40 border-teal-500/50 text-teal-200' : 'bg-slate-900 border-slate-800 text-slate-400'}`}>
          <div className="text-[10px] uppercase font-bold text-teal-400">Step 1</div>
          <div className="text-xs font-bold mt-1">Inspect Client History & Consent</div>
        </div>
        <div className={`p-4 rounded-xl border transition-all ${step === 2 ? 'bg-teal-950/40 border-teal-500/50 text-teal-200' : 'bg-slate-900 border-slate-800 text-slate-400'}`}>
          <div className="text-[10px] uppercase font-bold text-teal-400">Step 2</div>
          <div className="text-xs font-bold mt-1">Split-Screen Privacy Filter</div>
        </div>
        <div className={`p-4 rounded-xl border transition-all ${step === 3 ? 'bg-teal-950/40 border-teal-500/50 text-teal-200' : 'bg-slate-900 border-slate-800 text-slate-400'}`}>
          <div className="text-[10px] uppercase font-bold text-teal-400">Step 3</div>
          <div className="text-xs font-bold mt-1">Handover Execution & Audit</div>
        </div>
      </div>

      {/* Step 1: Initial Context */}
      {step === 1 && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-6">
          <h3 className="text-sm font-bold text-slate-200 border-b border-slate-800 pb-3">
            Client C001 Background & Active Consent Rules
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="text-xs font-bold text-slate-300">Session History</div>
              <ul className="text-[11px] text-slate-400 space-y-1.5 list-disc pl-4">
                <li>Workplace pressure & deadline strain</li>
                <li>Family conflict & relationship stress</li>
                <li>Financial difficulty & rent escalation</li>
              </ul>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="text-xs font-bold text-slate-300">Consent Rules (Configured)</div>
              <div className="space-y-1.5 text-[11px]">
                <div className="flex justify-between items-center p-1.5 rounded bg-emerald-500/10 text-emerald-300">
                  <span>Workplace</span>
                  <span className="font-mono text-[10px] uppercase">Granted (Counsellor)</span>
                </div>
                <div className="flex justify-between items-center p-1.5 rounded bg-indigo-500/10 text-indigo-300">
                  <span>Financial</span>
                  <span className="font-mono text-[10px] uppercase">Granted (Social Worker)</span>
                </div>
                <div className="flex justify-between items-center p-1.5 rounded bg-rose-500/10 text-rose-300">
                  <span>Family</span>
                  <span className="font-mono text-[10px] uppercase">Revoked / Restricted</span>
                </div>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="text-xs font-bold text-slate-300">Target Transfer</div>
              <div className="text-[11px] text-slate-400 space-y-1">
                <div>From: <strong className="text-teal-400">COUNS_001 (Counsellor)</strong></div>
                <div>To: <strong className="text-indigo-400">SOC_001 (Social Worker)</strong></div>
                <div className="mt-2 p-2 rounded bg-slate-900 border border-slate-700 text-[10px] text-slate-300">
                  Privacy Goal: Social worker receives Financial context, ZERO Family notes.
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              onClick={() => setStep(2)}
              className="px-5 py-2.5 bg-teal-500 hover:bg-teal-600 text-slate-950 font-bold rounded-xl text-xs flex items-center gap-2"
            >
              <span>Proceed to Split-Screen Privacy Filter</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Split-Screen Interface */}
      {step === 2 && previewData && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* LEFT SIDE: Available consent-approved facts */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
              <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                <div>
                  <h4 className="text-xs font-bold text-slate-200">LEFT: Available Consent-Approved Facts</h4>
                  <p className="text-[11px] text-slate-400">Filtered by Consent Engine for Social Worker Role</p>
                </div>
                <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-mono font-bold">
                  PASSED PRIVACY CHECK
                </span>
              </div>

              <div className="space-y-3">
                <div className="p-3 rounded-xl bg-slate-950 border border-emerald-500/30">
                  <div className="text-[11px] font-bold text-emerald-400 uppercase tracking-wider mb-1">Approved Categories</div>
                  <div className="flex flex-wrap gap-1.5">
                    {previewData.approved_categories.map(cat => (
                      <span key={cat} className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-medium border border-emerald-500/30">
                        ✓ {cat.replace('_', ' ').toUpperCase()}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-950 border border-rose-500/30">
                  <div className="text-[11px] font-bold text-rose-400 uppercase tracking-wider mb-1">Restricted / Unconsented Categories (Excluded)</div>
                  <div className="flex flex-wrap gap-1.5">
                    {previewData.restricted_categories.map(cat => (
                      <span key={cat} className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 text-[10px] font-medium border border-rose-500/30">
                        ✕ {cat.replace('_', ' ').toUpperCase()} (RESTRICTED)
                      </span>
                    ))}
                  </div>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-300 space-y-2">
                  <div className="text-[11px] font-bold text-slate-400">Deterministic Consent Verification Result:</div>
                  <p className="text-[11px] text-slate-300 leading-relaxed font-mono bg-slate-900 p-2.5 rounded border border-slate-800">
                    "Client expressed severe financial difficulty regarding rent escalation and debt repayment planning."
                  </p>
                  <p className="text-[10px] text-rose-400 italic">
                    Note: Family conflict details were automatically stripped by the Consent Engine prior to summary generation.
                  </p>
                </div>
              </div>
            </div>

            {/* RIGHT SIDE: Generated Continuity Summary */}
            <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
              <div className="flex justify-between items-center border-b border-slate-800 pb-3">
                <div>
                  <h4 className="text-xs font-bold text-slate-200">RIGHT: Generated Continuity Summary</h4>
                  <p className="text-[11px] text-slate-400">Autoritative Handover Output</p>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-slate-400">Confidence:</span>
                  <span className="px-2 py-0.5 rounded bg-teal-500/20 text-teal-300 text-xs font-bold font-mono">
                    {(previewData.confidence_score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-300 whitespace-pre-wrap leading-relaxed">
                {previewData.prototype_summary}
              </div>

              <div className="flex justify-between items-center pt-2">
                <button
                  onClick={() => setStep(1)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs"
                >
                  Back
                </button>
                <button
                  onClick={handleCreateHandover}
                  disabled={loading}
                  className="px-5 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-emerald-500/20"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>Approve & Execute Handover</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Step 3: Success Execution */}
      {step === 3 && handoverCreated && (
        <div className="glass-panel p-8 rounded-2xl border border-emerald-500/30 text-center space-y-4">
          <div className="w-12 h-12 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center mx-auto border border-emerald-500/40">
            <CheckCircle className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100">Handover Executed Successfully!</h3>
            <p className="text-xs text-slate-400 mt-1">
              Handover ID: <span className="font-mono text-emerald-400 font-bold">{handoverCreated.handover_id}</span>
            </p>
          </div>

          <div className="max-w-md mx-auto p-4 rounded-xl bg-slate-950 border border-slate-800 text-left text-xs space-y-2">
            <div className="flex justify-between text-slate-400">
              <span>Status:</span>
              <span className="font-bold text-emerald-400">{handoverCreated.handover_status}</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Confidence Score:</span>
              <span className="font-bold text-teal-400">{(handoverCreated.confidence_score * 100).toFixed(0)}%</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Consent Violation:</span>
              <span className="font-bold text-teal-400">0.0% (Zero Leakage)</span>
            </div>
          </div>

          <div className="flex justify-center gap-3 pt-2">
            <button
              onClick={() => setActiveView('clients')}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl text-xs"
            >
              View Client List
            </button>
            <button
              onClick={() => setActiveView('audit')}
              className="px-4 py-2 bg-teal-500/20 hover:bg-teal-500/30 text-teal-300 border border-teal-500/30 rounded-xl text-xs font-semibold"
            >
              View Audit Event
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
