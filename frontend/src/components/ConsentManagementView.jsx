import React, { useEffect, useState } from 'react';
import { ShieldCheck, ShieldAlert, Check, X, RefreshCw } from 'lucide-react';
import api from '../api';

export default function ConsentManagementView() {
  const [clientId, setClientId] = useState('C001');
  const [consents, setConsents] = useState([]);
  const [loading, setLoading] = useState(true);

  const categories = [
    { id: 'workplace', label: 'Workplace & Career Pressure' },
    { id: 'financial', label: 'Financial & Housing Support' },
    { id: 'family', label: 'Family & Marital Matters' },
    { id: 'wellbeing', label: 'Mental Wellbeing & Self-Care' },
    { id: 'housing', label: 'Tenancy & Housing Relocation' },
    { id: 'legal_support', label: 'Legal Aid & Estate Support' }
  ];

  useEffect(() => {
    fetchConsents();
  }, [clientId]);

  const fetchConsents = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/clients/${clientId}/consents`);
      setConsents(res.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleConsent = async (category, recipientRole, currentStatus) => {
    const newStatus = currentStatus === 'granted' ? 'revoked' : 'granted';
    try {
      await api.post('/consents/update', {
        client_id: clientId,
        information_category: category,
        allowed_recipient_role: recipientRole,
        consent_status: newStatus
      });
      fetchConsents();
    } catch (err) {
      console.error(err);
    }
  };

  const isCategoryGranted = (category, role) => {
    const rec = consents.find(c => c.information_category === category && (c.allowed_recipient_role === role || c.allowed_recipient_role === 'all'));
    return rec && rec.consent_status === 'granted' && !rec.revoked_at;
  };

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex justify-between items-center">
        <div>
          <h2 className="text-sm font-bold text-slate-100">Client Consent Preferences Control Center</h2>
          <p className="text-xs text-slate-400 mt-1">Section 5 Compliance: Client has absolute authority to grant or revoke category permissions per recipient role.</p>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-400">Target Client ID:</span>
          <input
            type="text"
            value={clientId}
            onChange={(e) => setClientId(e.target.value.toUpperCase())}
            className="bg-slate-950 border border-slate-800 text-teal-400 font-mono font-bold px-3 py-1.5 rounded-lg w-24 text-xs focus:outline-none"
          />
        </div>
      </div>

      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex justify-between items-center border-b border-slate-800 pb-3 text-xs">
          <span className="font-bold text-slate-300">Information Category</span>
          <div className="flex gap-12 font-bold text-slate-400 pr-4">
            <span>Sharing with Counsellor</span>
            <span>Sharing with Social Worker</span>
          </div>
        </div>

        <div className="space-y-3">
          {categories.map((cat) => {
            const counsellorGranted = isCategoryGranted(cat.id, 'counsellor');
            const socialWorkerGranted = isCategoryGranted(cat.id, 'social_worker');

            return (
              <div key={cat.id} className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex justify-between items-center text-xs">
                <div>
                  <div className="font-bold text-slate-200">{cat.label}</div>
                  <div className="text-[10px] text-slate-500 font-mono">Category ID: {cat.id}</div>
                </div>

                <div className="flex items-center gap-12">
                  {/* Counsellor Toggle */}
                  <button
                    onClick={() => handleToggleConsent(cat.id, 'counsellor', counsellorGranted ? 'granted' : 'revoked')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 border transition-all ${
                      counsellorGranted ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' : 'bg-rose-500/10 text-rose-300 border-rose-500/30'
                    }`}
                  >
                    {counsellorGranted ? <Check className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
                    <span>{counsellorGranted ? 'Granted' : 'Revoked'}</span>
                  </button>

                  {/* Social Worker Toggle */}
                  <button
                    onClick={() => handleToggleConsent(cat.id, 'social_worker', socialWorkerGranted ? 'granted' : 'revoked')}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 border transition-all ${
                      socialWorkerGranted ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/40' : 'bg-rose-500/10 text-rose-300 border-rose-500/30'
                    }`}
                  >
                    {socialWorkerGranted ? <Check className="w-3.5 h-3.5" /> : <X className="w-3.5 h-3.5" />}
                    <span>{socialWorkerGranted ? 'Granted' : 'Revoked'}</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
