import React, { useEffect, useState } from 'react';
import { FileText, ShieldAlert, CheckCircle } from 'lucide-react';
import api from '../api';

export default function AuditLogsView() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await api.get('/audit-logs');
      setLogs(res.data || []);
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
          <h2 className="text-sm font-bold text-slate-100">System Audit Trail Log</h2>
          <p className="text-xs text-slate-400 mt-1">Section 3 &amp; 12 Compliance: Immutable audit events tracking role permissions, access attempts, and consent changes.</p>
        </div>
      </div>

      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900 text-slate-400 font-semibold border-b border-slate-800">
            <tr>
              <th className="p-3.5">Audit ID</th>
              <th className="p-3.5">User ID</th>
              <th className="p-3.5">Client ID</th>
              <th className="p-3.5">Action Executed</th>
              <th className="p-3.5">Resource</th>
              <th className="p-3.5">Timestamp</th>
              <th className="p-3.5">Result Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {logs.map((log) => (
              <tr key={log.audit_id} className="hover:bg-slate-800/30">
                <td className="p-3.5 font-mono text-teal-400 font-bold">{log.audit_id}</td>
                <td className="p-3.5 font-mono text-slate-300">{log.user_id}</td>
                <td className="p-3.5 font-mono text-slate-400">{log.client_id || 'N/A'}</td>
                <td className="p-3.5 font-semibold text-slate-200">{log.action}</td>
                <td className="p-3.5 uppercase text-[10px] text-slate-400 font-bold">{log.resource_type}</td>
                <td className="p-3.5 font-mono text-[11px] text-slate-400">{log.timestamp}</td>
                <td className="p-3.5">
                  <span className={`px-2.5 py-0.5 rounded text-[10px] font-bold ${
                    log.result === 'SUCCESS' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-rose-500/20 text-rose-300'
                  }`}>
                    {log.result}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
