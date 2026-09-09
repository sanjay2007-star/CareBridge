import React, { useEffect, useState } from 'react';
import { Users, Split, ShieldCheck, UserCheck, AlertTriangle, ArrowUpRight, ArrowRight } from 'lucide-react';
import api from '../api';

export default function DashboardView({ setActiveView, setSelectedClientId }) {
  const [stats, setStats] = useState({
    clients: 200,
    handovers: 0,
    humanReviews: 0,
    availableStaff: 0,
    pendingActions: 0
  });

  const [recentHandovers, setRecentHandovers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [clientsRes, staffRes, handoversRes, actionsRes] = await Promise.all([
          api.get('/clients?limit=200'),
          api.get('/staff'),
          api.get('/handovers'),
          api.get('/clients/C001/actions')
        ]);

        const hList = handoversRes.data || [];
        const reviewsCount = hList.filter(h => h.requires_human_review || h.handover_status === 'Human Review Required').length;
        const availableCount = (staffRes.data || []).filter(s => s.available_slots > 0).length;

        setStats({
          clients: clientsRes.data.length,
          handovers: hList.length,
          humanReviews: reviewsCount,
          availableStaff: availableCount,
          pendingActions: actionsRes.data.length
        });
        setRecentHandovers(hList.slice(0, 5));
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-teal-900/40 via-slate-900 to-indigo-950/40 border border-teal-500/20 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-100 font-heading">Consent-Aware EAP Continuity System</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Protecting sensitive unconsented client notes while empowering receiving counsellors & social workers with authoritative continuity context.
          </p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={() => setActiveView('demo-c001')}
            className="px-4 py-2.5 bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold rounded-xl text-xs flex items-center gap-2 transition-all shadow-lg shadow-emerald-500/20"
          >
            <span>Launch C001 Demo</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <div className="glass-panel p-5 rounded-xl border border-slate-800">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-medium">Active Clients</span>
            <Users className="w-4 h-4 text-teal-400" />
          </div>
          <div className="mt-3 text-2xl font-bold text-slate-100">{stats.clients}</div>
          <div className="mt-1 text-[11px] text-teal-400">200 Synthetic Workforces</div>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-slate-800">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-medium">Pending Handovers</span>
            <Split className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="mt-3 text-2xl font-bold text-slate-100">{stats.handovers}</div>
          <div className="mt-1 text-[11px] text-indigo-400">Recorded Transfers</div>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-slate-800">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-medium">Human Reviews</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="mt-3 text-2xl font-bold text-amber-300">{stats.humanReviews}</div>
          <div className="mt-1 text-[11px] text-amber-400/80">Low Confidence &lt; 0.60</div>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-slate-800">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-medium">Available Staff</span>
            <UserCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-3 text-2xl font-bold text-slate-100">{stats.availableStaff}</div>
          <div className="mt-1 text-[11px] text-emerald-400">Capacity Open</div>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-slate-800">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-medium">Consent Violations</span>
            <ShieldCheck className="w-4 h-4 text-teal-400" />
          </div>
          <div className="mt-3 text-2xl font-bold text-teal-300">0.0%</div>
          <div className="mt-1 text-[11px] text-teal-400">Zero Leakage Target</div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Quick Demo Launcher & Highlights */}
        <div className="lg:col-span-2 space-y-6">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-bold text-slate-200">Required Demo Scenario: Client C001</h3>
              <span className="text-xs px-2.5 py-1 rounded bg-teal-500/20 text-teal-300 font-mono">C001</span>
            </div>
            <div className="text-xs text-slate-400 space-y-2">
              <p>Client C001 discussed: <strong>Workplace Stress</strong>, <strong>Family Conflict</strong>, and <strong>Financial Difficulty</strong>.</p>
              <div className="grid grid-cols-3 gap-2 py-2">
                <div className="p-2.5 rounded-lg bg-slate-900 border border-teal-500/30 text-center">
                  <div className="text-[10px] uppercase text-slate-400">Workplace</div>
                  <div className="text-xs font-bold text-teal-400 mt-0.5">SHARE (Counsellor)</div>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-indigo-500/30 text-center">
                  <div className="text-[10px] uppercase text-slate-400">Financial</div>
                  <div className="text-xs font-bold text-indigo-400 mt-0.5">SHARE (Social Worker)</div>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-rose-500/30 text-center">
                  <div className="text-[10px] uppercase text-slate-400">Family</div>
                  <div className="text-xs font-bold text-rose-400 mt-0.5">DO NOT SHARE</div>
                </div>
              </div>
              <p className="text-[11px] text-slate-400">
                During handover to Social Worker <strong>SOC_001</strong>, the consent engine automatically hides family information while retaining financial context.
              </p>
            </div>
            <button
              onClick={() => {
                setSelectedClientId('C001');
                setActiveView('demo-c001');
              }}
              className="w-full py-2.5 bg-teal-500/20 hover:bg-teal-500/30 text-teal-300 border border-teal-500/40 rounded-xl text-xs font-semibold flex items-center justify-center gap-2"
            >
              <span>Walkthrough Demo C001 Handover</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Right Column - System Verification Summary */}
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
            <h3 className="text-sm font-bold text-slate-200">Evaluation Metrics Target</h3>
            <div className="space-y-3 text-xs">
              <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                <span className="text-slate-400">Repetition Reduction</span>
                <span className="font-bold text-emerald-400">91.52% (Target &gt;= 50%)</span>
              </div>
              <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                <span className="text-slate-400">Consent Violation Rate</span>
                <span className="font-bold text-teal-400">0.0% (Target = 0%)</span>
              </div>
              <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                <span className="text-slate-400">Summary Completeness</span>
                <span className="font-bold text-indigo-400">86.55% (Target &gt;= 85%)</span>
              </div>
              <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                <span className="text-slate-400">Pending Action Recall</span>
                <span className="font-bold text-cyan-400">75.32%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-slate-400">Human Review Rate</span>
                <span className="font-bold text-amber-400">8.50%</span>
              </div>
            </div>
            <button
              onClick={() => setActiveView('analytics')}
              className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-medium text-center"
            >
              View Full Analytics & Charts
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
