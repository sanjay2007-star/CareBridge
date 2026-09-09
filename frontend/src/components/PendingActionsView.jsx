import React, { useState, useEffect } from 'react';
import { Clock, CheckCircle, Plus, Filter } from 'lucide-react';
import api from '../api';

export default function PendingActionsView() {
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterRole, setFilterRole] = useState('');

  useEffect(() => {
    fetchActions();
  }, []);

  const fetchActions = async () => {
    setLoading(true);
    try {
      const res = await api.get('/clients/C001/actions');
      setActions(res.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusToggle = async (actionId, currentStatus) => {
    const nextStatus = currentStatus === 'Completed' ? 'Pending' : 'Completed';
    try {
      await api.put(`/actions/${actionId}/status?status=${nextStatus}`);
      fetchActions();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 flex justify-between items-center">
        <div>
          <h2 className="text-sm font-bold text-slate-100">Inter-Professional Pending Actions Tracker</h2>
          <p className="text-xs text-slate-400 mt-1">Track &amp; update follow-up responsibilities assigned to Counsellors or Social Workers.</p>
        </div>
      </div>

      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900/80 text-slate-400 font-semibold border-b border-slate-800">
            <tr>
              <th className="p-4">Action ID</th>
              <th className="p-4">Client ID</th>
              <th className="p-4">Assigned Role</th>
              <th className="p-4">Description</th>
              <th className="p-4">Priority</th>
              <th className="p-4">Due Date</th>
              <th className="p-4">Status</th>
              <th className="p-4 text-right">Toggle</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {actions.map((act) => (
              <tr key={act.action_id} className="hover:bg-slate-800/30 transition-all">
                <td className="p-4 font-mono font-bold text-teal-400">{act.action_id}</td>
                <td className="p-4 font-mono text-slate-300">{act.client_id}</td>
                <td className="p-4 capitalize">{act.assigned_role.replace('_', ' ')}</td>
                <td className="p-4 text-slate-200">{act.action_description}</td>
                <td className="p-4">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    act.priority === 'High' ? 'bg-rose-500/20 text-rose-300' : 'bg-amber-500/20 text-amber-300'
                  }`}>
                    {act.priority}
                  </span>
                </td>
                <td className="p-4 font-mono text-slate-400">{act.due_date}</td>
                <td className="p-4">
                  <span className={`px-2.5 py-0.5 rounded text-[11px] font-semibold ${
                    act.status === 'Completed' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-teal-500/20 text-teal-300'
                  }`}>
                    {act.status}
                  </span>
                </td>
                <td className="p-4 text-right">
                  <button
                    onClick={() => handleStatusToggle(act.action_id, act.status)}
                    className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px]"
                  >
                    Mark {act.status === 'Completed' ? 'Pending' : 'Completed'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
