
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Target, AlertTriangle, Briefcase, Shield, Zap, List, FileText, HelpCircle } from 'lucide-react';

import Overview from './views/Overview';
import DecisionConsole from './views/DecisionConsole';
import Incidents from './views/Incidents';
import Strategy from './views/Strategy';
import Safety from './views/Safety';
import Execution from './views/Execution';
import AuditTrail from './views/AuditTrail';
import Evaluation from './views/Evaluation';
import CausalExplainer from './views/CausalExplainer';

const navItems = [
  { path: '/', label: 'Overview', icon: LayoutDashboard },
  { path: '/incidents', label: 'Incident Intel', icon: AlertTriangle },
  { path: '/cases', label: 'Decision Console', icon: Target },
  { path: '/strategy', label: 'Recovery Strategy', icon: Briefcase },
  { path: '/safety', label: 'Safety / Governor', icon: Shield },
  { path: '/execution', label: 'Execution', icon: Zap },
  { path: '/audit', label: 'Audit Trail', icon: List },
  { path: '/evaluation', label: 'Evaluation', icon: FileText },
  { path: '/explainer', label: 'Causal Explainer', icon: HelpCircle },
];

function Sidebar() {
  const location = useLocation();
  return (
    <div className="w-64 bg-slate-900 text-slate-300 min-h-screen flex flex-col">
      <div className="p-4 border-b border-slate-800">
        <h1 className="text-xl font-bold text-white flex items-center">
          <Zap className="mr-2 h-6 w-6 text-blue-500" />
          CausalRecover
        </h1>
        <div className="text-xs text-slate-500 mt-1 uppercase tracking-wider">Phase 8 Dashboard</div>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${
                isActive ? 'bg-slate-800 text-white' : 'hover:bg-slate-800 hover:text-white'
              }`}
            >
              <Icon className={`mr-3 h-5 w-5 ${isActive ? 'text-blue-500' : 'text-slate-400'}`} />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-slate-800 text-xs text-slate-500">
        <p>Demo Mode Active</p>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <div className="flex h-screen bg-slate-50 overflow-hidden font-sans">
        <Sidebar />
        <main className="flex-1 overflow-y-auto bg-slate-100">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/incidents" element={<Incidents />} />
            <Route path="/cases" element={<DecisionConsole />} />
            <Route path="/strategy" element={<Strategy />} />
            <Route path="/safety" element={<Safety />} />
            <Route path="/execution" element={<Execution />} />
            <Route path="/audit" element={<AuditTrail />} />
            <Route path="/evaluation" element={<Evaluation />} />
            <Route path="/explainer" element={<CausalExplainer />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
