import { useState } from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  ArrowDown,
  CheckCircle2,
  XCircle,
  AlertOctagon,
  Layers,
  Lock,
  Zap,
} from 'lucide-react';
import { Badge } from '../components/Badge';

interface SafetyScenario {
  id: string;
  name: string;
  caseId: string;
  modelRecommendation: string;
  supportLevel: 'HIGH' | 'LOW' | 'INSUFFICIENT';
  supportValue: string;
  economicCheck: 'PASS' | 'NEGATIVE_NET_VALUE';
  economicValue: string;
  governorStatus: 'APPROVED' | 'REJECTED';
  rejectionReason?: string;
  finalAuthorization: string;
  rationale: string;
}

const SCENARIOS: SafetyScenario[] = [
  {
    id: 'SCENARIO_D',
    name: 'Hard Policy Velocity Violation (Case D)',
    caseId: 'CASE_D_POLICY_REJECT',
    modelRecommendation: 'RETRY_NOW (Estimated Uplift: +15%)',
    supportLevel: 'HIGH',
    supportValue: '90% Positivity Support',
    economicCheck: 'PASS',
    economicValue: '+₹373.30 Expected Net Value',
    governorStatus: 'REJECTED',
    rejectionReason: 'MAX_RETRY_VELOCITY_EXCEEDED (4 retries attempted >= 3 maximum limit)',
    finalAuthorization: 'NO_ACTION (Dispatched suppression ticket)',
    rationale: 'Even though the causal model estimated high uplift and positive economics, the deterministic governor hard-blocked the retry to protect merchant brand reputation and avoid issuer card-locking penalties.',
  },
  {
    id: 'SCENARIO_C',
    name: 'Out of Support / Positivity Violation (Case C)',
    caseId: 'CASE_C_OUT_OF_SUPPORT',
    modelRecommendation: 'ALTERNATE_METHOD (Estimated Uplift: +45%)',
    supportLevel: 'INSUFFICIENT',
    supportValue: '1% Positivity Support (< 5% minimum bound)',
    economicCheck: 'PASS',
    economicValue: '+₹4,500.00 Raw Estimate',
    governorStatus: 'REJECTED',
    rejectionReason: 'INSUFFICIENT_SUPPORT (Common support violation)',
    finalAuthorization: 'NO_ACTION (Conservative Fallback)',
    rationale: 'The model has no observational overlap for this bank and failure combination. Extrapolating here carries severe counterfactual variance; the support gate intervenes and suppresses the recommendation.',
  },
  {
    id: 'SCENARIO_B',
    name: 'Natural Recovery Trap Suppression (Case B)',
    caseId: 'CASE_B_NATURAL_TRAP',
    modelRecommendation: 'RETRY_NOW (Estimated Uplift: +0.5%)',
    supportLevel: 'HIGH',
    supportValue: '80% Positivity Support',
    economicCheck: 'NEGATIVE_NET_VALUE',
    economicValue: '-₹1.20 Net Value after retry fee',
    governorStatus: 'APPROVED',
    rejectionReason: undefined,
    finalAuthorization: 'NO_ACTION (Economic Prudence)',
    rationale: 'Customer has a 99% historical self-recovery probability. Intervening burns retry transaction fees with zero net incremental gain. The economic gate correctly selects NO_ACTION.',
  },
  {
    id: 'SCENARIO_A',
    name: 'Full Verification & Authorization (Case A)',
    caseId: 'CASE_A_POS_UPLIFT',
    modelRecommendation: 'RETRY_LATER (Estimated Uplift: +12%)',
    supportLevel: 'HIGH',
    supportValue: '85% Positivity Support',
    economicCheck: 'PASS',
    economicValue: '+₹178.70 Net Incremental Value',
    governorStatus: 'APPROVED',
    rejectionReason: undefined,
    finalAuthorization: 'RETRY_LATER (Dispatched to Razorpay smart queue)',
    rationale: 'All gates cleared. High support, positive incremental margin, and full compliance with retry frequency limits.',
  },
];

export default function Safety() {
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>('SCENARIO_D');
  const scenario = SCENARIOS.find(s => s.id === selectedScenarioId) || SCENARIOS[0];

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-md bg-blue-600 text-white">
              <ShieldCheck className="w-4 h-4" />
            </span>
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              Safety Governor & Policy Gatekeeper
            </h1>
            <Badge variant="success">Deterministic Enforcement</Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Visualizing the multi-stage hard gatekeeper architecture preventing unsafe ML execution.
          </p>
        </div>
      </div>

      {/* Scenario Selector Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        {SCENARIOS.map((sc) => {
          const isSelected = sc.id === selectedScenarioId;
          return (
            <button
              key={sc.id}
              onClick={() => setSelectedScenarioId(sc.id)}
              className={`px-3 py-2 rounded-lg text-xs font-semibold whitespace-nowrap transition-all border ${
                isSelected
                  ? 'bg-slate-900 text-white border-slate-900 shadow-xs'
                  : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
              }`}
            >
              {sc.name}
            </button>
          );
        })}
      </div>

      {/* 5-STAGE SAFETY FLOW DIAGRAM */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs space-y-6">
        <div className="border-b border-slate-100 pb-3 flex items-center justify-between">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block">
              Live Pipeline Evaluation
            </span>
            <h2 className="text-sm font-bold text-slate-900">
              {scenario.name} · <span className="font-mono text-blue-600">{scenario.caseId}</span>
            </h2>
          </div>
          <Badge
            variant={scenario.governorStatus === 'REJECTED' || scenario.finalAuthorization.startsWith('NO_ACTION') ? 'warning' : 'success'}
            size="md"
          >
            Outcome: {scenario.finalAuthorization.split(' ')[0]}
          </Badge>
        </div>

        {/* Vertical Visual Gatekeeper Stepper */}
        <div className="max-w-2xl mx-auto space-y-4">
          {/* STAGE 1: MODEL RECOMMENDATION */}
          <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/50 flex items-start gap-4">
            <div className="w-8 h-8 rounded-full bg-blue-600 text-white font-mono font-bold text-xs flex items-center justify-center shrink-0">
              1
            </div>
            <div className="flex-1 text-xs">
              <span className="text-[11px] font-bold uppercase tracking-wider text-blue-600 block">
                Model Recommendation (T-Learner / DR-Learner)
              </span>
              <div className="font-mono font-bold text-slate-900 text-sm mt-0.5">
                {scenario.modelRecommendation}
              </div>
              <p className="text-slate-500 mt-1">
                Individual treatment effect (CATE) estimated from propensity-weighted historical payments.
              </p>
            </div>
          </div>

          <div className="flex justify-center text-slate-400">
            <ArrowDown className="w-5 h-5 animate-bounce" />
          </div>

          {/* STAGE 2: SUPPORT CHECK */}
          <div className={`p-4 rounded-xl border flex items-start gap-4 ${
            scenario.supportLevel === 'INSUFFICIENT'
              ? 'border-rose-300 bg-rose-50/60'
              : 'border-slate-200 bg-slate-50'
          }`}>
            <div className={`w-8 h-8 rounded-full font-mono font-bold text-xs flex items-center justify-center shrink-0 text-white ${
              scenario.supportLevel === 'INSUFFICIENT' ? 'bg-rose-600' : 'bg-slate-700'
            }`}>
              2
            </div>
            <div className="flex-1 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">
                  Support & Positivity Check
                </span>
                <Badge variant={scenario.supportLevel === 'INSUFFICIENT' ? 'danger' : 'success'}>
                  {scenario.supportLevel} SUPPORT
                </Badge>
              </div>
              <div className="font-mono font-bold text-slate-900 text-sm mt-0.5">
                {scenario.supportValue}
              </div>
              <p className="text-slate-500 mt-1">
                Verifies strict overlap condition: $P(A=a|X) \ge 0.05$. Suppresses recommendations in unobserved regions.
              </p>
            </div>
          </div>

          <div className="flex justify-center text-slate-400">
            <ArrowDown className="w-5 h-5" />
          </div>

          {/* STAGE 3: ECONOMIC CHECK */}
          <div className={`p-4 rounded-xl border flex items-start gap-4 ${
            scenario.economicCheck === 'NEGATIVE_NET_VALUE'
              ? 'border-amber-300 bg-amber-50/60'
              : 'border-slate-200 bg-slate-50'
          }`}>
            <div className={`w-8 h-8 rounded-full font-mono font-bold text-xs flex items-center justify-center shrink-0 text-white ${
              scenario.economicCheck === 'NEGATIVE_NET_VALUE' ? 'bg-amber-600' : 'bg-slate-700'
            }`}>
              3
            </div>
            <div className="flex-1 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">
                  Economic Net Value Check
                </span>
                <Badge variant={scenario.economicCheck === 'NEGATIVE_NET_VALUE' ? 'warning' : 'success'}>
                  {scenario.economicCheck}
                </Badge>
              </div>
              <div className="font-mono font-bold text-slate-900 text-sm mt-0.5">
                {scenario.economicValue}
              </div>
              <p className="text-slate-500 mt-1">
                Enforces Net Value = (Amount × Uplift) - Action Cost - Friction &gt; 0.
              </p>
            </div>
          </div>

          <div className="flex justify-center text-slate-400">
            <ArrowDown className="w-5 h-5" />
          </div>

          {/* STAGE 4: GOVERNOR STATUS */}
          <div className={`p-4 rounded-xl border flex items-start gap-4 ${
            scenario.governorStatus === 'REJECTED'
              ? 'border-rose-400 bg-rose-50 shadow-xs'
              : 'border-emerald-300 bg-emerald-50/50'
          }`}>
            <div className={`w-8 h-8 rounded-full font-mono font-bold text-xs flex items-center justify-center shrink-0 text-white ${
              scenario.governorStatus === 'REJECTED' ? 'bg-rose-600' : 'bg-emerald-600'
            }`}>
              4
            </div>
            <div className="flex-1 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-bold uppercase tracking-wider block font-semibold text-slate-600">
                  Deterministic Policy Governor
                </span>
                <Badge variant={scenario.governorStatus === 'REJECTED' ? 'danger' : 'success'}>
                  {scenario.governorStatus}
                </Badge>
              </div>
              {scenario.rejectionReason && (
                <div className="font-mono font-bold text-rose-700 text-sm mt-1 flex items-center gap-1.5">
                  <AlertOctagon className="w-4 h-4 text-rose-600 shrink-0" />
                  <span>REASON: {scenario.rejectionReason}</span>
                </div>
              )}
              <p className="text-slate-500 mt-1">
                Zero-tolerance hard rules: Velocity limits (max 3), card-stolen blocklists, and amount exposure boundaries.
              </p>
            </div>
          </div>

          <div className="flex justify-center text-slate-400">
            <ArrowDown className="w-5 h-5" />
          </div>

          {/* STAGE 5: FINAL AUTHORIZATION */}
          <div className="p-4 rounded-xl border border-slate-900 bg-slate-900 text-white flex items-start gap-4 shadow-md">
            <div className="w-8 h-8 rounded-full bg-emerald-500 text-slate-950 font-mono font-bold text-xs flex items-center justify-center shrink-0">
              5
            </div>
            <div className="flex-1 text-xs">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
                Final Execution Authorization (Razorpay Adapter)
              </span>
              <div className="font-mono font-bold text-emerald-400 text-base mt-0.5">
                {scenario.finalAuthorization}
              </div>
              <p className="text-slate-300 mt-1">
                {scenario.rationale}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
