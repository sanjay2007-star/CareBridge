import React, { useEffect, useState } from 'react';
import { AlertTriangle, ShieldCheck } from 'lucide-react';
import api from '../api';

export default function RiskRegisterView() {
  const [risks, setRisks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRisks();
  }, []);

  const fetchRisks = async () => {
    setLoading(true);
    try {
      const res = await api.get('/risk-register');
      setRisks(res.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex justify-between items-center">
        <div>
          <h2 className="text-sm font-bold text-slate-100">System Risk Register &amp; Safeguards</h2>
          <p className="text-xs text-slate-400 mt-1">Section 20 Compliance: Identification, likelihood, impact, and mitigations for 11 key operational risks.</p>
        </div>
      </div>

      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900 text-slate-400 font-semibold border-b border-slate-800">
            <tr>
              <th className="p-3.5">Risk Description</th>
              <th className="p-3.5">Likelihood</th>
              <th className="p-3.5">Impact</th>
              <th className="p-3.5">System Safeguard / Mitigation</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {risks.map((r) => (
              <tr key={r.id} className="hover:bg-slate-800/30">
                <td className="p-3.5 font-semibold text-slate-200">{r.risk}</td>
                <td className="p-3.5">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    r.likelihood === 'High' ? 'bg-amber-500/20 text-amber-300' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {r.likelihood}
                  </span>
                </td>
                <td className="p-3.5">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    r.impact === 'Critical' ? 'bg-rose-500/20 text-rose-300' : 'bg-indigo-500/20 text-indigo-300'
                  }`}>
                    {r.impact}
                  </span>
                </td>
                <td className="p-3.5 text-slate-300">{r.mitigation}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
