import { AlertTriangle, Cpu, ShieldCheck, Activity } from 'lucide-react';
import { Link } from 'react-router-dom';
import { formatPaiseToINR } from '../utils/formatters';

interface TopBarProps {
  revenueAtRiskPaise?: number;
  activeIncidentsCount?: number;
}

export function TopBar({ revenueAtRiskPaise = 202060897, activeIncidentsCount = 3 }: TopBarProps) {
  return (
    <header className="h-16 border-b border-slate-200 bg-white/95 backdrop-blur-xs px-6 flex items-center justify-between z-10 shrink-0">
      {/* Left: Operational Modes */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>LIVE CAUSAL ENGINE</span>
        </div>

        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-100 border border-slate-200 text-slate-700 text-xs font-medium">
          <span className="text-slate-400">Gateway:</span>
          <span className="font-semibold text-blue-700">Razorpay TEST_MODE</span>
          <span className="text-[10px] bg-slate-200 text-slate-600 px-1 rounded">SIMULATED</span>
        </div>
      </div>

      {/* Right: Telemetry & Model Metadata */}
      <div className="flex items-center gap-4">
        {/* Model & Policy Versions */}
        <div className="hidden lg:flex items-center gap-3 text-xs border-r border-slate-200 pr-4">
          <div className="flex items-center gap-1.5 text-slate-600">
            <Cpu className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-400">Model:</span>
            <span className="font-mono font-medium text-slate-800">DR-Learner v1.4</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-600">
            <ShieldCheck className="w-3.5 h-3.5 text-slate-400" />
            <span className="text-slate-400">Policy:</span>
            <span className="font-mono font-medium text-slate-800">Gov-v2.1</span>
          </div>
        </div>

        {/* Revenue at Risk Metric */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-lg bg-rose-50/70 border border-rose-200/80 text-xs">
          <Activity className="w-3.5 h-3.5 text-rose-500" />
          <span className="text-rose-700 font-medium">At Risk:</span>
          <span className="font-bold text-rose-900 font-mono">
            {formatPaiseToINR(revenueAtRiskPaise, true)}
          </span>
        </div>

        {/* Incident Alert Badge */}
        <Link
          to="/incidents"
          className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-amber-50 hover:bg-amber-100 border border-amber-200 text-amber-900 text-xs font-medium transition-colors"
        >
          <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
          <span>{activeIncidentsCount} Active Incidents</span>
        </Link>
      </div>
    </header>
  );
}
