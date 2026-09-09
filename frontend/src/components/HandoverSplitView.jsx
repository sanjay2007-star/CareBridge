import React, { useState, useEffect } from 'react';
import { Split, ShieldCheck, ShieldAlert, AlertTriangle, CheckCircle, Clock, UserCheck, RefreshCw } from 'lucide-react';
import api from '../api';

export default function HandoverSplitView({ selectedClientId }) {
  const [clientId, setClientId] = useState(selectedClientId || 'C001');
  const [staffList, setStaffList] = useState([]);
  const [targetStaffId, setTargetStaffId] = useState('SOC_001');
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [executedHandover, setExecutedHandover] = useState(null);

  useEffect(() => {
    fetchStaff();
  }, []);

  useEffect(() => {
    if (clientId && targetStaffId) {
      handlePreview();
    }
  }, [clientId, targetStaffId]);

  const fetchStaff = async () => {
    try {
      const res = await api.get('/staff');
      setStaffList(res.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handlePreview = async () => {
    setLoading(true);
    setExecutedHandover(null);
    try {
      const res = await api.post('/handovers/preview', {
        client_id: clientId,
        from_staff_id: 'COUNS_001',
        to_staff_id: targetStaffId
      });
      setPreview(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async () => {
    setLoading(true);
    try {
      const res = await api.post('/handovers/create', {
        client_id: clientId,
        from_staff_id: 'COUNS_001',
        to_staff_id: targetStaffId
      });
      setExecutedHandover(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Controls Bar */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col md:flex-row justify-between items-center gap-4">
        <div className="flex items-center gap-3 w-full md:w-auto">
          <div className="p-2 rounded-lg bg-teal-500/20 text-teal-400">
            <Split className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-100">Inter-Professional Continuity Handover Screen</h2>
            <p className="text-[11px] text-slate-400">Deterministic Consent Filtering &amp; Safe Fallback Summary Engine</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 text-xs w-full md:w-auto">
          <div className="flex items-center gap-1.5 text-slate-400">
            <span>Client:</span>
            <input
              type="text"
              value={clientId}
              onChange={(e) => setClientId(e.target.value.toUpperCase())}
              placeholder="e.g. C001"
              className="bg-slate-950 border border-slate-800 text-teal-400 font-mono font-bold rounded-lg px-2.5 py-1.5 w-24 text-xs focus:outline-none"
            />
          </div>

          <div className="flex items-center gap-1.5 text-slate-400">
            <span>Recipient Staff:</span>
            <select
              value={targetStaffId}
              onChange={(e) => setTargetStaffId(e.target.value)}
              className="bg-slate-950 border border-slate-800 text-slate-200 rounded-lg px-3 py-1.5 text-xs focus:outline-none"
            >
              {staffList.map(s => (
                <option key={s.staff_id} value={s.staff_id}>
                  {s.name} ({s.role.replace('_', ' ').toUpperCase()} • Slots: {s.available_slots})
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handlePreview}
            disabled={loading}
            className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Refresh Preview</span>
          </button>
        </div>
      </div>

      {/* Staff Capacity Status Banner */}
      {preview && !preview.staff_available && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center gap-3 text-amber-300 text-xs">
          <AlertTriangle className="w-5 h-5 shrink-0 text-amber-400" />
          <div>
            <strong>Staff Capacity Limit Warning:</strong> Recipient staff member has reached maximum active cases. Handover will be placed on <strong>WAITLIST / MANUAL SCHEDULING REQUIRED</strong> upon submission.
          </div>
        </div>
      )}

      {/* Main Split Screen Grid */}
      {preview && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* LEFT PANEL */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">LEFT: Consent-Approved Data</h3>
                <p className="text-[11px] text-slate-400">Allowed Categories for Recipient Role: <span className="font-semibold text-teal-400">{preview.recipient_role}</span></p>
              </div>
              <span className="px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold font-mono border border-emerald-500/30">
                PRIVACY FILTER PASSED
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-950 border border-emerald-500/30">
                <div className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider mb-1.5">Approved Information Categories</div>
                <div className="flex flex-wrap gap-1.5">
                  {preview.approved_categories.length === 0 ? (
                    <span className="text-slate-500 italic text-[11px]">No active categories approved by consent.</span>
                  ) : (
                    preview.approved_categories.map(cat => (
                      <span key={cat} className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-semibold border border-emerald-500/30">
                        ✓ {cat.replace('_', ' ').toUpperCase()}
                      </span>
                    ))
                  )}
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-950 border border-rose-500/30">
                <div className="text-[10px] font-bold text-rose-400 uppercase tracking-wider mb-1.5">Restricted / Unconsented Categories (Excluded)</div>
                <div className="flex flex-wrap gap-1.5">
                  {preview.restricted_categories.length === 0 ? (
                    <span className="text-slate-500 italic text-[11px]">No categories restricted by client.</span>
                  ) : (
                    preview.restricted_categories.map(cat => (
                      <span key={cat} className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 text-[10px] font-semibold border border-rose-500/30">
                        ✕ {cat.replace('_', ' ').toUpperCase()} (RESTRICTED)
                      </span>
                    ))
                  )}
                </div>
              </div>

              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                <div className="text-[10px] text-slate-400 font-bold uppercase">Baseline Handover Comparison (Naive Output)</div>
                <div className="font-mono text-[10px] text-slate-400 whitespace-pre-wrap bg-slate-900 p-2.5 rounded border border-slate-800">
                  {preview.baseline_summary}
                </div>
              </div>
            </div>
          </div>

          {/* RIGHT PANEL */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">RIGHT: Generated Continuity Summary</h3>
                <p className="text-[11px] text-slate-400">Safe Continuity Summary Pipeline Output</p>
              </div>

              <div className="flex items-center gap-2">
                <span className="text-[10px] text-slate-400">Confidence:</span>
                <span className={`px-2.5 py-1 rounded text-xs font-bold font-mono border ${
                  preview.confidence_score >= 0.80 ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' :
                  preview.confidence_score >= 0.60 ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' :
                  'bg-rose-500/20 text-rose-300 border-rose-500/30'
                }`}>
                  {(preview.confidence_score * 100).toFixed(0)}%
                </span>
              </div>
            </div>

            {preview.requires_human_review && (
              <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0 text-amber-400" />
                <span><strong>Review Recommended:</strong> {preview.review_reasons.join('; ')}</span>
              </div>
            )}

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-200 whitespace-pre-wrap leading-relaxed min-h-[220px]">
              {preview.prototype_summary}
            </div>

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
              <button
                onClick={handlePreview}
                className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-xs"
              >
                Regenerate Summary
              </button>

              <div className="flex items-center gap-2">
                <button
                  onClick={handleCreate}
                  disabled={loading}
                  className="px-5 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold rounded-xl text-xs flex items-center gap-2 shadow-lg shadow-emerald-500/20"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>Approve &amp; Send Handover</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Handover Created Confirmation Modal/Box */}
      {executedHandover && (
        <div className="p-6 rounded-2xl bg-emerald-950/40 border border-emerald-500/40 text-emerald-200 space-y-3">
          <div className="flex items-center gap-2 font-bold text-sm">
            <CheckCircle className="w-5 h-5 text-emerald-400" />
            <span>Handover Submitted Successfully!</span>
          </div>
          <p className="text-xs text-slate-300">
            Handover record ID: <strong className="font-mono text-emerald-400">{executedHandover.handover_id}</strong> • Status: <strong className="text-teal-300">{executedHandover.handover_status}</strong>
          </p>
        </div>
      )}
    </div>
  );
}
