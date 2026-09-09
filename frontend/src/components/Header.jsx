import React from 'react';
import { UserCheck, ShieldAlert, HeartHandshake, Settings, User } from 'lucide-react';
import { setAuthHeaders } from '../api';

export default function Header({ currentRole, setCurrentRole, userId, setUserId }) {
  const roles = [
    { id: 'counsellor', label: 'Counsellor', defaultUserId: 'COUNS_001', color: 'bg-teal-500/20 text-teal-300 border-teal-500/30' },
    { id: 'social_worker', label: 'Social Worker', defaultUserId: 'SOC_001', color: 'bg-indigo-500/20 text-indigo-300 border-indigo-500/30' },
    { id: 'client', label: 'Client (C001)', defaultUserId: 'C001', color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' },
    { id: 'admin', label: 'Administrator', defaultUserId: 'ADMIN_001', color: 'bg-amber-500/20 text-amber-300 border-amber-500/30' }
  ];

  const handleRoleChange = (r) => {
    setCurrentRole(r.id);
    setUserId(r.defaultUserId);
    setAuthHeaders(r.id, r.defaultUserId);
  };

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/80 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center gap-3">
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Persona:</span>
        <div className="flex items-center gap-2">
          {roles.map((r) => {
            const isSelected = currentRole === r.id;
            return (
              <button
                key={r.id}
                onClick={() => handleRoleChange(r)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                  isSelected ? `${r.color} font-semibold ring-1 ring-slate-700` : 'bg-slate-800/40 text-slate-400 border-slate-700/50 hover:bg-slate-800'
                }`}
              >
                {r.label}
              </button>
            );
          })}
        </div>
      </div>

      <div className="flex items-center gap-4 text-xs">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/60 border border-slate-700/60 text-slate-300">
          <User className="w-3.5 h-3.5 text-teal-400" />
          <span>User ID: <strong className="text-slate-100">{userId}</strong></span>
        </div>

        {currentRole === 'admin' && (
          <div className="flex items-center gap-1.5 text-amber-400 bg-amber-500/10 px-2.5 py-1 rounded border border-amber-500/20 text-[11px]">
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>Admin View (Session Notes Restricted)</span>
          </div>
        )}
      </div>
    </header>
  );
}
