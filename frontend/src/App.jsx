import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';

import DashboardView from './components/DashboardView';
import DemoC001View from './components/DemoC001View';
import ClientsView from './components/ClientsView';
import ClientDetailView from './components/ClientDetailView';
import HandoverSplitView from './components/HandoverSplitView';
import PendingActionsView from './components/PendingActionsView';
import StaffCapacityView from './components/StaffCapacityView';
import ConsentManagementView from './components/ConsentManagementView';
import AnalyticsView from './components/AnalyticsView';
import FairnessView from './components/FairnessView';
import BeforeAfterView from './components/BeforeAfterView';
import ArchitectureView from './components/ArchitectureView';
import RiskRegisterView from './components/RiskRegisterView';
import StakeholderValidationView from './components/StakeholderValidationView';
import AuditLogsView from './components/AuditLogsView';

export default function App() {
  const [activeView, setActiveView] = useState('dashboard');
  const [currentRole, setCurrentRole] = useState('counsellor');
  const [userId, setUserId] = useState('COUNS_001');
  const [selectedClientId, setSelectedClientId] = useState('C001');

  const renderView = () => {
    switch (activeView) {
      case 'dashboard':
        return <DashboardView setActiveView={setActiveView} setSelectedClientId={setSelectedClientId} />;
      case 'demo-c001':
        return <DemoC001View setActiveView={setActiveView} setSelectedClientId={setSelectedClientId} />;
      case 'clients':
        return <ClientsView setActiveView={setActiveView} setSelectedClientId={setSelectedClientId} />;
      case 'client-detail':
        return <ClientDetailView clientId={selectedClientId} setActiveView={setActiveView} />;
      case 'handovers':
        return <HandoverSplitView selectedClientId={selectedClientId} />;
      case 'actions':
        return <PendingActionsView />;
      case 'staff':
        return <StaffCapacityView />;
      case 'consent':
        return <ConsentManagementView />;
      case 'analytics':
        return <AnalyticsView />;
      case 'fairness':
        return <FairnessView />;
      case 'before-after':
        return <BeforeAfterView setActiveView={setActiveView} />;
      case 'architecture':
        return <ArchitectureView />;
      case 'risks':
        return <RiskRegisterView />;
      case 'validation':
        return <StakeholderValidationView />;
      case 'audit':
        return <AuditLogsView />;
      default:
        return <DashboardView setActiveView={setActiveView} setSelectedClientId={setSelectedClientId} />;
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans antialiased">
      <Sidebar activeView={activeView} setActiveView={setActiveView} />
      <div className="flex-1 flex flex-col min-w-0">
        <Header 
          currentRole={currentRole} 
          setCurrentRole={setCurrentRole} 
          userId={userId} 
          setUserId={setUserId} 
        />
        <main className="flex-1 p-6 overflow-y-auto">
          {renderView()}
        </main>
      </div>
    </div>
  );
}
