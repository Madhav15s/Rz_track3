import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Target,
  AlertTriangle,
  Briefcase,
  Shield,
  Zap,
  List,
  FileText,
  HelpCircle,
  Activity,
  Layers,
} from 'lucide-react';

import Overview from './views/Overview';
import DecisionConsole from './views/DecisionConsole';
import Incidents from './views/Incidents';
import Strategy from './views/Strategy';
import Safety from './views/Safety';
import Execution from './views/Execution';
import AuditTrail from './views/AuditTrail';
import Evaluation from './views/Evaluation';
import CausalExplainer from './views/CausalExplainer';
import { TopBar } from './components/TopBar';

interface NavSection {
  title: string;
  items: {
    path: string;
    label: string;
    icon: any;
    badge?: string;
  }[];
}

const navSections: NavSection[] = [
  {
    title: 'Operations',
    items: [
      { path: '/', label: 'Overview', icon: LayoutDashboard },
      { path: '/incidents', label: 'Incidents', icon: AlertTriangle, badge: '3 Active' },
      { path: '/cases', label: 'Decision Console', icon: Target, badge: '5 Ready' },
      { path: '/strategy', label: 'Recovery Strategy', icon: Briefcase },
    ],
  },
  {
    title: 'Governance',
    items: [
      { path: '/safety', label: 'Safety / Governor', icon: Shield },
      { path: '/execution', label: 'Execution', icon: Zap },
      { path: '/audit', label: 'Audit Trail', icon: List },
    ],
  },
  {
    title: 'Causal Intelligence',
    items: [
      { path: '/evaluation', label: 'Evaluation', icon: FileText },
      { path: '/explainer', label: 'Causal Explainer', icon: HelpCircle },
    ],
  },
];

function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 bg-slate-950 text-slate-300 min-h-screen flex flex-col border-r border-slate-800 shrink-0 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-xs">
            <Layers className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-base font-bold text-white tracking-tight leading-none">
              CausalRecover
            </h1>
            <span className="text-[10px] text-blue-400 font-mono tracking-wider uppercase font-semibold">
              Razorpay Buildathon
            </span>
          </div>
        </div>
      </div>

      {/* Navigation Sections */}
      <nav className="flex-1 px-3 py-4 space-y-6 overflow-y-auto custom-scrollbar">
        {navSections.map((section) => (
          <div key={section.title} className="space-y-1">
            <div className="px-3 pb-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-500">
              {section.title}
            </div>
            <div className="space-y-0.5">
              {section.items.map((item) => {
                const Icon = item.icon;
                const isActive = item.path === '/'
                  ? location.pathname === '/'
                  : location.pathname.startsWith(item.path);

                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                      isActive
                        ? 'bg-blue-600 text-white font-semibold shadow-xs'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 truncate">
                      <Icon className={`h-4 w-4 shrink-0 ${isActive ? 'text-white' : 'text-slate-500'}`} />
                      <span className="truncate">{item.label}</span>
                    </div>
                    {item.badge && (
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded font-mono font-medium ${
                          isActive
                            ? 'bg-blue-700 text-blue-100'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Footer System Status */}
      <div className="p-4 border-t border-slate-900 bg-slate-950/60 text-xs text-slate-400 space-y-1.5">
        <div className="flex items-center justify-between">
          <span className="text-[11px] text-slate-500">Architecture</span>
          <span className="font-mono text-[11px] text-emerald-400">8-Layer Closed Loop</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-[11px] text-slate-500">Engine State</span>
          <span className="inline-flex items-center gap-1 font-mono text-[11px] text-slate-300">
            <Activity className="w-3 h-3 text-emerald-400" />
            Deterministic
          </span>
        </div>
      </div>
    </aside>
  );
}

export default function App() {
  return (
    <Router>
      <div className="flex h-screen bg-slate-100 text-slate-900 overflow-hidden font-sans">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <TopBar />
          <main className="flex-1 overflow-y-auto custom-scrollbar p-6 bg-slate-100">
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
      </div>
    </Router>
  );
}
