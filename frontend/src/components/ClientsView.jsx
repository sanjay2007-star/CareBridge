import React, { useState, useEffect } from 'react';
import { Search, Filter, Eye, ShieldCheck, User } from 'lucide-react';
import api from '../api';

export default function ClientsView({ setSelectedClientId, setActiveView }) {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [workModeFilter, setWorkModeFilter] = useState('');
  const [languageFilter, setLanguageFilter] = useState('');

  useEffect(() => {
    fetchClients();
  }, [workModeFilter, languageFilter]);

  const fetchClients = async () => {
    setLoading(true);
    try {
      let url = '/clients?limit=200';
      if (workModeFilter) url += `&work_mode=${workModeFilter}`;
      if (languageFilter) url += `&language=${languageFilter}`;
      const res = await api.get(url);
      setClients(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const filteredClients = clients.filter(c => 
    c.client_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.region.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Search and Filters */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800 flex flex-col md:flex-row justify-between gap-4 items-center">
        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search Client ID or Region..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-teal-500"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto text-xs">
          <div className="flex items-center gap-1.5 text-slate-400">
            <Filter className="w-3.5 h-3.5" />
            <span>Work Mode:</span>
          </div>
          <select
            value={workModeFilter}
            onChange={(e) => setWorkModeFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-teal-500"
          >
            <option value="">All Work Modes</option>
            <option value="Remote">Remote</option>
            <option value="Hybrid">Hybrid</option>
            <option value="On-site">On-site</option>
          </select>

          <select
            value={languageFilter}
            onChange={(e) => setLanguageFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-slate-200 rounded-xl px-3 py-2 text-xs focus:outline-none focus:border-teal-500"
          >
            <option value="">All Languages</option>
            <option value="English-primary">English-primary</option>
            <option value="Multilingual/non-English-primary">Multilingual</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900/80 text-slate-400 font-semibold border-b border-slate-800">
            <tr>
              <th className="p-4">Client ID</th>
              <th className="p-4">Age Group</th>
              <th className="p-4">Work Mode</th>
              <th className="p-4">Preferred Language</th>
              <th className="p-4">Region</th>
              <th className="p-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {loading ? (
              <tr>
                <td colSpan="6" className="p-8 text-center text-slate-500">Loading synthetic workforce dataset...</td>
              </tr>
            ) : filteredClients.length === 0 ? (
              <tr>
                <td colSpan="6" className="p-8 text-center text-slate-500">No clients match selected filter criteria.</td>
              </tr>
            ) : (
              filteredClients.map((client) => (
                <tr key={client.client_id} className="hover:bg-slate-800/30 transition-all">
                  <td className="p-4 font-mono font-bold text-teal-400">{client.client_id}</td>
                  <td className="p-4">{client.age_group}</td>
                  <td className="p-4">
                    <span className={`px-2.5 py-0.5 rounded text-[11px] font-medium border ${
                      client.work_mode === 'Remote' ? 'bg-cyan-500/10 text-cyan-300 border-cyan-500/20' :
                      client.work_mode === 'Hybrid' ? 'bg-indigo-500/10 text-indigo-300 border-indigo-500/20' :
                      'bg-emerald-500/10 text-emerald-300 border-emerald-500/20'
                    }`}>
                      {client.work_mode}
                    </span>
                  </td>
                  <td className="p-4 text-slate-300">{client.preferred_language}</td>
                  <td className="p-4 text-slate-400">{client.region}</td>
                  <td className="p-4 text-right">
                    <button
                      onClick={() => {
                        setSelectedClientId(client.client_id);
                        setActiveView('client-detail');
                      }}
                      className="px-3 py-1 rounded-lg bg-teal-500/15 hover:bg-teal-500/30 text-teal-300 border border-teal-500/30 text-[11px] font-medium inline-flex items-center gap-1.5 transition-all"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>View Profile</span>
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
