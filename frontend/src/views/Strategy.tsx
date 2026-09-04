import { useState } from 'react';
import {
  Briefcase,
  Zap,
  Clock,
  MessageSquare,
  CreditCard,
  UserCheck,
  Ban,
  TrendingUp,
  AlertTriangle,
  ShieldCheck,
  CheckCircle2,
} from 'lucide-react';
import { Badge } from '../components/Badge';
import { formatPaiseToINR, formatPercentage } from '../utils/formatters';

interface StrategyAction {
  id: number;
  name: string;
  code: string;
  costPaise: number;
  friction: 'LOW' | 'MEDIUM' | 'HIGH';
  riskProfile: 'MINIMAL' | 'MODERATE' | 'HIGH';
  avgUplift: number;
  idealFor: string;
  counterfactualRule: string;
}

const STRATEGY_ACTIONS: StrategyAction[] = [
  {
    id: 1,
    name: 'Instant Retry (Now)',
    code: 'RETRY_NOW',
    costPaise: 150, // ₹1.50
    friction: 'LOW',
    riskProfile: 'MODERATE',
    avgUplift: 0.15,
    idealFor: 'Transient network disconnects, gateway 504 timeouts with 0 previous retries.',
    counterfactualRule: 'Only allowed if retries < 3 AND affected banking rail is healthy (no active outage).',
  },
  {
    id: 2,
    name: 'Scheduled Retry (Later)',
    code: 'RETRY_LATER',
    costPaise: 130, // ₹1.30
    friction: 'LOW',
    riskProfile: 'MINIMAL',
    avgUplift: 0.12,
    idealFor: 'Bank node maintenance windows, high latency spikes, or temporary customer balance sync delays.',
    counterfactualRule: 'Triggers when upstream bank is degraded; delays execution by 15-45 minutes.',
  },
  {
    id: 3,
    name: 'Smart Payment Link Message',
    code: 'PAYMENT_MESSAGE',
    costPaise: 25, // ₹0.25 (SMS/WhatsApp)
    friction: 'MEDIUM',
    riskProfile: 'MINIMAL',
    avgUplift: 0.08,
    idealFor: 'Mobile UPI app auth failures, abandoned checkout screens, or expired sessions.',
    counterfactualRule: 'Capped at 1 message per failed transaction to avoid customer notification fatigue.',
  },
  {
    id: 4,
    name: 'Alternate Rail Switch',
    code: 'ALTERNATE_METHOD',
    costPaise: 200, // ₹2.00
    friction: 'MEDIUM',
    riskProfile: 'MODERATE',
    avgUplift: 0.22,
    idealFor: 'Card decline / issuer block when user has saved alternate UPI or Netbanking accounts.',
    counterfactualRule: 'Requires common support verification (p >= 0.05) on user payment instrument history.',
  },
  {
    id: 5,
    name: 'Human Concierge Escalation',
    code: 'HUMAN_ESCALATION',
    costPaise: 5000, // ₹50.00
    friction: 'HIGH',
    riskProfile: 'HIGH',
    avgUplift: 0.35,
    idealFor: 'Enterprise B2B tier accounts with transactions > ₹50,000 where automated retries failed.',
    counterfactualRule: 'Restricted strictly to HIGH customer value bands where expected recovery value > ₹1,000.',
  },
  {
    id: 0,
    name: 'Autonomous Abstention',
    code: 'NO_ACTION',
    costPaise: 0,
    friction: 'LOW',
    riskProfile: 'MINIMAL',
    avgUplift: 0.0,
    idealFor: 'Natural recovery traps (user already returning) or hard card-stolen permanent declines.',
    counterfactualRule: 'Default fallback when expected net incremental recovery <= 0 or velocity cap exceeded.',
  },
];

export default function Strategy() {
  const [selectedActionId, setSelectedActionId] = useState<number>(2);
  const selectedAction = STRATEGY_ACTIONS.find(a => a.id === selectedActionId) || STRATEGY_ACTIONS[1];

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-md bg-blue-600 text-white">
              <Briefcase className="w-4 h-4" />
            </span>
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              Recovery Strategy & Action Portfolio
            </h1>
            <Badge variant="info">Counterfactual Policy Engine</Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Standard operating procedures, friction matrices, and unit economics governing automated interventions.
          </p>
        </div>
      </div>

      {/* Action Portfolio Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {STRATEGY_ACTIONS.map((act) => {
          const isSelected = act.id === selectedActionId;
          return (
            <div
              key={act.id}
              onClick={() => setSelectedActionId(act.id)}
              className={`cursor-pointer rounded-xl border p-5 shadow-xs transition-all ${
                isSelected
                  ? 'border-blue-600 bg-blue-50/40 ring-2 ring-blue-600/20'
                  : 'border-slate-200 bg-white hover:border-slate-300'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="font-mono text-xs font-bold text-slate-500">
                  {act.code}
                </span>
                <Badge
                  variant={
                    act.riskProfile === 'MINIMAL'
                      ? 'success'
                      : act.riskProfile === 'MODERATE'
                      ? 'warning'
                      : 'danger'
                  }
                >
                  {act.riskProfile} RISK
                </Badge>
              </div>

              <h3 className="font-bold text-slate-900 text-sm mb-1">{act.name}</h3>
              <p className="text-xs text-slate-600 line-clamp-2 mb-4">
                {act.idealFor}
              </p>

              <div className="grid grid-cols-3 gap-2 border-t border-slate-100 pt-3 text-[11px]">
                <div>
                  <span className="text-slate-400 block">Unit Cost</span>
                  <span className="font-mono font-bold text-slate-800">
                    {formatPaiseToINR(act.costPaise)}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block">Friction</span>
                  <span className="font-semibold text-slate-800">{act.friction}</span>
                </div>
                <div className="text-right">
                  <span className="text-slate-400 block">Avg Uplift</span>
                  <span className="font-mono font-bold text-emerald-600">
                    {formatPercentage(act.avgUplift, true)}
                  </span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Action Deep Dive */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block">
              Policy Specification
            </span>
            <h2 className="text-base font-bold text-slate-900">
              {selectedAction.name} ({selectedAction.code})
            </h2>
          </div>
          <Badge variant="info">Action ID: {selectedAction.id}</Badge>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs">
          <div className="space-y-3">
            <h4 className="font-bold text-slate-800 uppercase tracking-wider text-[11px]">
              Unit Economics & Friction Mechanics
            </h4>
            <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-500">API Dispatch Cost:</span>
                <span className="font-mono font-bold text-slate-800">{formatPaiseToINR(selectedAction.costPaise)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Customer Friction Score:</span>
                <span className="font-semibold text-slate-800">{selectedAction.friction}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Historical Treatment Uplift:</span>
                <span className="font-mono font-bold text-emerald-600">{formatPercentage(selectedAction.avgUplift, true)}</span>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <h4 className="font-bold text-slate-800 uppercase tracking-wider text-[11px]">
              Deterministic Counterfactual Decision Rule
            </h4>
            <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 text-slate-700 leading-relaxed font-mono text-[11px]">
              {selectedAction.counterfactualRule}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
