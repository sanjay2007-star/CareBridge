import React, { useEffect, useState } from 'react';
import { ShieldCheck, ShieldAlert, Clock, Target, Calendar, ArrowLeft, Split, AlertCircle } from 'lucide-react';
import api from '../api';

export default function ClientDetailView({ clientId, setActiveView }) {
  const targetId = clientId || 'C001';
  const [client, setClient] = useState(null);
  const [consents, setConsents] = useState([]);
  const [goals, setGoals] = useState([]);
  const [actions, setActions] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [adminRestricted, setAdminRestricted] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchClientProfile();
  }, [targetId]);

  const fetchClientProfile = async () => {
    setLoading(true);
    setAdminRestricted(false);
    try {
      const [cRes, cnRes, gRes, aRes] = await Promise.all([
        api.get(`/clients/${targetId}`),
        api.get(`/clients/${targetId}/consents`),
        api.get(`/clients/${targetId}/goals`),
        api.get(`/clients/${targetId}/actions`)
      ]);
      setClient(cRes.data);
      setConsents(cnRes.data);
      setGoals(gRes.data);
      setActions(aRes.data);

      try {
        const sRes = await api.get(`/clients/${targetId}/sessions`);
        setSessions(sRes.data);
      } catch (err) {
        if (err.response && err.response.status === 403) {
          setAdminRestricted(true);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getConsentBadge = (category) => {
    const rec = consents.find(c => c.information_category === category);
    if (!rec) {
      return <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px] border border-slate-700">CONSENT MISSING</span>;
    }
    if (rec.consent_status === 'revoked') {
      return <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 text-[10px] font-bold border border-rose-500/30">CONSENT REVOKED</span>;
    }
    if (rec.consent_status === 'granted') {
      return <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold border border-emerald-500/30">SHARING ALLOWED ({rec.allowed_recipient_role.toUpperCase()})</span>;
    }
    return <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 text-[10px] border border-amber-500/30">SHARING RESTRICTED</span>;
  };

  if (loading) {
    return <div className="p-8 text-center text-slate-500">Loading client profile details...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Top Bar */}
      <div className="flex justify-between items-center">
        <button
          onClick={() => setActiveView('clients')}
          className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 text-xs flex items-center gap-1.5 hover:bg-slate-800"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Clients</span>
        </button>

        <button
          onClick={() => setActiveView('handovers')}
          className="px-4 py-2 bg-teal-500 hover:bg-teal-600 text-slate-950 font-bold rounded-xl text-xs flex items-center gap-2"
        >
          <Split className="w-4 h-4" />
          <span>Initiate Continuity Handover</span>
        </button>
      </div>

      {/* Client Overview Card */}
      {client && (
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <div className="text-[10px] text-slate-500 uppercase font-bold">Client ID</div>
            <div className="text-xl font-bold font-mono text-teal-400 mt-0.5">{client.client_id}</div>
          </div>
          <div>
            <div className="text-[10px] text-slate-500 uppercase font-bold">Work Mode</div>
            <div className="text-sm font-semibold text-slate-200 mt-1">{client.work_mode}</div>
          </div>
          <div>
            <div className="text-[10px] text-slate-500 uppercase font-bold">Language Group</div>
            <div className="text-sm font-semibold text-slate-200 mt-1">{client.preferred_language}</div>
          </div>
          <div>
            <div className="text-[10px] text-slate-500 uppercase font-bold">Region & Age</div>
            <div className="text-sm font-semibold text-slate-200 mt-1">{client.region} • {client.age_group}</div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Consent Preferences & Goals */}
        <div className="space-y-6">
          {/* Consent Status Card */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
              <ShieldCheck className="w-4 h-4 text-teal-400" />
              <h3 className="text-xs font-bold text-slate-200">Consent Preferences Dashboard</h3>
            </div>
            <div className="space-y-2.5">
              {['workplace', 'financial', 'family', 'wellbeing', 'housing', 'legal_support'].map((cat) => (
                <div key={cat} className="flex justify-between items-center p-2.5 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-xs capitalize text-slate-300">{cat.replace('_', ' ')}</span>
                  {getConsentBadge(cat)}
                </div>
              ))}
            </div>
          </div>

          {/* Goals */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
              <Target className="w-4 h-4 text-indigo-400" />
              <h3 className="text-xs font-bold text-slate-200">Active Support Goals</h3>
            </div>
            {goals.length === 0 ? (
              <p className="text-xs text-slate-500">No active goals found.</p>
            ) : (
              <div className="space-y-2">
                {goals.map(g => (
                  <div key={g.goal_id} className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-1">
                    <div className="flex justify-between text-[10px] text-slate-400">
                      <span className="font-semibold uppercase text-indigo-300">{g.goal_category}</span>
                      <span className="text-teal-400">{g.goal_status}</span>
                    </div>
                    <p className="text-slate-300 leading-relaxed">{g.goal_description}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column - Sessions Timeline & Pending Actions */}
        <div className="lg:col-span-2 space-y-6">
          {/* Sessions Timeline */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-teal-400" />
                <h3 className="text-xs font-bold text-slate-200">Counselling Session Records</h3>
              </div>
              <span className="text-[11px] text-slate-500">Total: {sessions.length}</span>
            </div>

            {adminRestricted ? (
              <div className="p-6 rounded-xl bg-amber-500/10 border border-amber-500/20 text-center space-y-2">
                <ShieldAlert className="w-6 h-6 text-amber-400 mx-auto" />
                <h4 className="text-xs font-bold text-amber-300">Admin Role Restriction Enforced</h4>
                <p className="text-[11px] text-slate-400 max-w-md mx-auto">
                  Section 3 Compliance: Administrators are restricted from viewing raw confidential session summaries. Switch persona to Counsellor or Social Worker to view authorized session history.
                </p>
              </div>
            ) : sessions.length === 0 ? (
              <p className="text-xs text-slate-500">No session records available for this client.</p>
            ) : (
              <div className="space-y-3">
                {sessions.map(s => (
                  <div key={s.session_id} className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-mono text-teal-400 font-bold">{s.session_date}</span>
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">
                        Sensitivity: {s.sensitivity_level}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed">{s.session_summary}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Pending Actions */}
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
              <Clock className="w-4 h-4 text-emerald-400" />
              <h3 className="text-xs font-bold text-slate-200">Assigned Pending Actions</h3>
            </div>
            {actions.length === 0 ? (
              <p className="text-xs text-slate-500">No pending actions assigned.</p>
            ) : (
              <div className="space-y-2">
                {actions.map(act => (
                  <div key={act.action_id} className="p-3 rounded-xl bg-slate-950 border border-slate-800 flex justify-between items-center text-xs">
                    <div>
                      <div className="font-semibold text-slate-200">{act.action_description}</div>
                      <div className="text-[10px] text-slate-400 mt-0.5">Assigned: {act.assigned_role} • Due: {act.due_date}</div>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 text-[10px] font-bold">
                      {act.status}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
