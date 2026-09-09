import React, { useEffect, useState } from 'react';
import { UserCheck, ShieldAlert, AlertTriangle, Users } from 'lucide-react';
import api from '../api';

export default function StaffCapacityView() {
  const [staff, setStaff] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStaff();
  }, []);

  const fetchStaff = async () => {
    setLoading(true);
    try {
      const res = await api.get('/staff');
      setStaff(res.data || []);
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
          <h2 className="text-sm font-bold text-slate-100">Staff Workload &amp; Capacity Dashboard</h2>
          <p className="text-xs text-slate-400 mt-1">Section 13 Compliance: Enforcing maximum active case limits to prevent staff burnout.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {staff.map((s) => {
          const usagePct = Math.round((s.current_active_cases / s.maximum_active_cases) * 100);
          const isFull = s.current_active_cases >= s.maximum_active_cases;

          return (
            <div key={s.staff_id} className={`glass-panel p-5 rounded-2xl border space-y-3 ${isFull ? 'border-amber-500/40 bg-amber-950/20' : 'border-slate-800'}`}>
              <div className="flex justify-between items-start">
                <div>
                  <div className="font-bold text-slate-100 text-xs">{s.name}</div>
                  <div className="text-[10px] text-teal-400 uppercase tracking-wider font-mono font-semibold">{s.staff_id} • {s.role.replace('_', ' ')}</div>
                </div>
                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${isFull ? 'bg-amber-500/20 text-amber-300' : 'bg-emerald-500/20 text-emerald-300'}`}>
                  {isFull ? 'AT MAXIMUM CAPACITY' : `${s.available_slots} SLOTS OPEN`}
                </span>
              </div>

              <div className="space-y-1">
                <div className="flex justify-between text-[11px] text-slate-400">
                  <span>Workload Gauge:</span>
                  <span className="font-mono font-bold text-slate-200">{s.current_active_cases} / {s.maximum_active_cases} Cases ({usagePct}%)</span>
                </div>
                <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                  <div 
                    className={`h-full transition-all ${isFull ? 'bg-amber-400' : usagePct > 75 ? 'bg-teal-400' : 'bg-emerald-400'}`}
                    style={{ width: `${usagePct}%` }}
                  />
                </div>
              </div>

              {isFull && (
                <div className="p-2 rounded bg-amber-500/10 border border-amber-500/20 text-[10px] text-amber-300 flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                  <span>New assignments will trigger WAITLIST status.</span>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
