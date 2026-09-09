import React, { useEffect, useState } from 'react';
import { Star, MessageSquare } from 'lucide-react';
import api from '../api';

export default function StakeholderValidationView() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetchValidation();
  }, []);

  const fetchValidation = async () => {
    try {
      const res = await api.get('/stakeholder-validation');
      setData(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  if (!data) return <div className="p-8 text-center text-slate-500">Loading simulated stakeholder validation feedback...</div>;

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex justify-between items-center">
        <div>
          <h2 className="text-sm font-bold text-slate-100">Stakeholder Validation Results (Simulated)</h2>
          <p className="text-xs text-slate-400 mt-1">Section 22 Compliance: Feedback from Counsellors, Social Workers, and EAP Administrators.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {data.responses.map((resp, i) => (
          <div key={i} className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-3">
            <div className="flex justify-between items-center border-b border-slate-800 pb-2">
              <span className="font-bold text-teal-300 text-xs">{resp.role}</span>
              <div className="flex items-center gap-1 text-amber-400 font-bold text-xs">
                <Star className="w-3.5 h-3.5 fill-amber-400" />
                <span>{resp.usefulness} / 5.0</span>
              </div>
            </div>

            <div className="space-y-1.5 text-[11px]">
              <div className="flex justify-between text-slate-400">
                <span>Summary Usefulness:</span>
                <span className="font-bold text-slate-200">{resp.usefulness} / 5.0</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Privacy Clarity:</span>
                <span className="font-bold text-slate-200">{resp.privacy_clarity} / 5.0</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>Handover Efficiency:</span>
                <span className="font-bold text-slate-200">{resp.efficiency} / 5.0</span>
              </div>
              <div className="flex justify-between text-slate-400">
                <span>System Trust:</span>
                <span className="font-bold text-slate-200">{resp.trust} / 5.0</span>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-[11px] text-slate-300 italic">
              "{resp.feedback}"
            </div>
          </div>
        ))}
      </div>

      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <h3 className="text-xs font-bold text-slate-200">Qualitative Stakeholder Feedback Summary</h3>
        <div className="space-y-3 text-xs">
          {data.qualitative_qa.map((qa, i) => (
            <div key={i} className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
              <div className="font-semibold text-teal-400">Q: {qa.question}</div>
              <div className="text-slate-300">A: {qa.answer}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
