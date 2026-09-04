import { useState, useEffect } from 'react';
import {
  Target,
  ArrowRight,
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Zap,
  DollarSign,
  Activity,
  ChevronRight,
  Check,
  XCircle,
  RefreshCw,
} from 'lucide-react';
import { fetchCases, fetchCase, fetchCaseDecision, executeCaseAction, fetchIncidents } from '../api';
import type { Case, DecisionResponse, Incident } from '../types';
import { formatPaiseToINR, formatPercentage } from '../utils/formatters';
import { Badge } from '../components/Badge';

export default function DecisionConsole() {
  const [cases, setCases] = useState<Case[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<string>('CASE_A_POS_UPLIFT');
  const [caseDetails, setCaseDetails] = useState<Case | null>(null);
  const [decision, setDecision] = useState<DecisionResponse | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [executing, setExecuting] = useState(false);
  const [executionResult, setExecutionResult] = useState<{ status: string; correlation_id: string } | null>(null);
  const [executionError, setExecutionError] = useState<string | null>(null);

  useEffect(() => {
    async function init() {
      try {
        const [loadedCases, loadedIncidents] = await Promise.all([
          fetchCases(),
          fetchIncidents(),
        ]);
        setCases(loadedCases);
        setIncidents(loadedIncidents);
        if (loadedCases.length > 0) {
          setSelectedCaseId(loadedCases[0].case_id);
        }
      } catch (err) {
        console.error('Error loading cases:', err);
      }
    }
    init();
  }, []);

  const handleSelectCase = (id: string) => {
    setSelectedCaseId(id);
    setExecutionResult(null);
    setExecutionError(null);
  };

  useEffect(() => {
    if (!selectedCaseId) return;

    let isMounted = true;

    async function loadCaseData() {
      try {
        const [c, d] = await Promise.all([
          fetchCase(selectedCaseId),
          fetchCaseDecision(selectedCaseId),
        ]);
        if (isMounted) {
          setCaseDetails(c);
          setDecision(d);
        }
      } catch (err) {
        console.error('Error loading case detail:', err);
      }
    }

    loadCaseData();
    return () => { isMounted = false; };
  }, [selectedCaseId]);

  const handleExecute = async () => {
    if (!decision || !caseDetails) return;
    setExecuting(true);
    setExecutionError(null);
    setExecutionResult(null);

    try {
      const res = await executeCaseAction(selectedCaseId, decision.recommended_action);
      setExecutionResult(res);
    } catch (err: any) {
      setExecutionError(err.message || 'Execution failed');
    } finally {
      setExecuting(false);
    }
  };

  // Find associated incident
  const associatedIncident = incidents.find(
    i => i.affected_bank === caseDetails?.bank || i.affected_payment_method === caseDetails?.payment_method
  );

  return (
    <div className="space-y-5 max-w-7xl mx-auto pb-12">
      {/* View Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-md bg-blue-600 text-white">
              <Target className="w-4 h-4" />
            </span>
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              Causal Decision Console
            </h1>
            <Badge variant="info">Counterfactual ML Engine</Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Evaluating individual treatment effects, propensity support bounds, and deterministic governor checks.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-500 font-mono">
            Active Queue: {cases.length} Failed Payments
          </span>
        </div>
      </div>

      {/* THREE-COLUMN HERO LAYOUT */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-start">
        {/* COLUMN 1: RECOVERY QUEUE (3.5 COLS) */}
        <div className="lg:col-span-3 rounded-xl border border-slate-200 bg-white shadow-xs overflow-hidden">
          <div className="p-3.5 border-b border-slate-100 bg-slate-50/70 flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-600">
              Recovery Queue
            </span>
            <span className="text-[11px] font-mono text-slate-500 bg-slate-200/70 px-1.5 py-0.5 rounded">
              {cases.length} cases
            </span>
          </div>

          <div className="divide-y divide-slate-100 max-h-[720px] overflow-y-auto custom-scrollbar">
            {cases.map((c) => {
              const isSelected = c.case_id === selectedCaseId;
              return (
                <button
                  key={c.case_id}
                  id={`queue-case-${c.case_id}`}
                  onClick={() => handleSelectCase(c.case_id)}
                  className={`w-full text-left p-3.5 transition-all text-xs flex flex-col gap-1.5 ${
                    isSelected
                      ? 'bg-blue-50/90 border-l-4 border-l-blue-600 text-slate-900 shadow-xs'
                      : 'hover:bg-slate-50 text-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-slate-900">
                      {c.case_id}
                    </span>
                    <span className="font-mono font-bold text-slate-900">
                      {formatPaiseToINR(c.amount_paise)}
                    </span>
                  </div>

                  <div className="flex items-center gap-1.5 flex-wrap">
                    <Badge variant={c.payment_method === 'UPI' ? 'purple' : 'info'}>
                      {c.payment_method}
                    </Badge>
                    <span className="text-slate-500 font-medium">
                      {c.bank}
                    </span>
                    <span className="text-slate-400">·</span>
                    <span className="text-slate-500 font-mono">
                      {c.time_since_failure_minutes}m ago
                    </span>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-slate-500 pt-0.5">
                    <span className="truncate font-mono text-rose-600 bg-rose-50 px-1 rounded">
                      {c.failure_code}
                    </span>
                    {c.retries_attempted > 0 && (
                      <span className="text-amber-700 font-medium bg-amber-50 px-1 rounded">
                        {c.retries_attempted} retries
                      </span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* COLUMN 2: SELECTED PAYMENT DETAILS (4 COLS) */}
        <div className="lg:col-span-4 space-y-4">
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
                  Selected Transaction
                </span>
                <span className="font-mono font-extrabold text-slate-900 text-base">
                  {caseDetails?.case_id || '—'}
                </span>
              </div>
              <Badge variant="default" size="md">
                {caseDetails?.customer_value_band?.toUpperCase()} TIER
              </Badge>
            </div>

            {/* Financial & Payment Metadata */}
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block text-[11px]">Transaction Amount</span>
                <span className="font-mono font-bold text-slate-900 text-base">
                  {formatPaiseToINR(caseDetails?.amount_paise)}
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block text-[11px]">Failure Code</span>
                <span className="font-mono font-bold text-rose-700">
                  {caseDetails?.failure_code}
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block text-[11px]">Payment Method</span>
                <span className="font-semibold text-slate-800">
                  {caseDetails?.payment_method} · {caseDetails?.bank}
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block text-[11px]">Time Since Failure</span>
                <span className="font-mono font-semibold text-slate-800">
                  {caseDetails?.time_since_failure_minutes} minutes
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block text-[11px]">Retries Attempted</span>
                <span className={`font-mono font-bold ${
                  (caseDetails?.retries_attempted ?? 0) >= 3 ? 'text-rose-600' : 'text-slate-800'
                }`}>
                  {caseDetails?.retries_attempted} attempts
                </span>
                {(caseDetails?.retries_attempted ?? 0) >= 3 && (
                  <span className="text-[10px] text-rose-600 block mt-0.5 font-medium">Velocity Cap Triggered</span>
                )}
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                <span className="text-slate-400 block text-[11px]">Historical Success Rate</span>
                <span className="font-mono font-bold text-slate-800">
                  {formatPercentage(caseDetails?.historical_payment_success_rate)}
                </span>
              </div>
            </div>

            {/* Upstream Incident Correlation */}
            <div className="p-3 rounded-lg border border-amber-200 bg-amber-50/60 text-xs space-y-1">
              <div className="flex items-center gap-1.5 text-amber-800 font-semibold">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                <span>Correlated Gateway Incident</span>
              </div>
              {associatedIncident ? (
                <div className="text-slate-700">
                  <span className="font-mono font-medium">{associatedIncident.id}</span>: {associatedIncident.type} on {associatedIncident.affected_payment_method} ({associatedIncident.affected_bank}).
                </div>
              ) : (
                <div className="text-slate-600">
                  No upstream degradation detected. Isolated transaction timeout.
                </div>
              )}
            </div>

            {/* Customer Engagement Context */}
            <div className="space-y-1.5 pt-1 text-xs">
              <div className="flex justify-between text-slate-600">
                <span>Customer Engagement Score</span>
                <span className="font-mono font-bold">
                  {formatPercentage(caseDetails?.engagement_score)}
                </span>
              </div>
              <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                <div
                  className="bg-blue-600 h-full rounded-full"
                  style={{ width: `${(caseDetails?.engagement_score ?? 0) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* COLUMN 3: CAUSAL DECISION PANEL & COUNTERFACTUAL MATRIX (5 COLS) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Causal Matrix Card */}
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
                  Counterfactual Action Matrix
                </span>
                <h2 className="text-sm font-bold text-slate-900">
                  Estimated Causal Uplift & Support
                </h2>
              </div>
              <Badge
                variant={
                  decision?.governor_status === 'APPROVED'
                    ? 'success'
                    : decision?.governor_status === 'POLICY_REJECTED'
                    ? 'danger'
                    : 'warning'
                }
                size="md"
              >
                {decision?.governor_status}
              </Badge>
            </div>

            {/* Matrix Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
                    <th className="py-2 px-2">Action</th>
                    <th className="py-2 px-2 text-right">Uplift</th>
                    <th className="py-2 px-2 text-right">Support</th>
                    <th className="py-2 px-2">Conf</th>
                    <th className="py-2 px-2 text-right">Exp Value</th>
                    <th className="py-2 px-2 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  {decision?.candidate_actions.map((act) => {
                    const isSelected = act.status === 'SELECTED';
                    const isPolicyRejected = act.status === 'POLICY_REJECTED';
                    const isAbstained = act.status === 'ABSTAINED';

                    return (
                      <tr
                        key={act.action}
                        className={`transition-colors ${
                          isSelected
                            ? 'bg-blue-50/70 font-semibold text-slate-900'
                            : isPolicyRejected
                            ? 'bg-rose-50/50 text-slate-700'
                            : 'hover:bg-slate-50/60 text-slate-600'
                        }`}
                      >
                        <td className="py-2.5 px-2 font-sans font-medium">
                          {act.name}
                        </td>
                        <td className="py-2.5 px-2 text-right">
                          <span
                            className={
                              act.estimated_uplift > 0
                                ? 'text-emerald-600 font-semibold'
                                : act.estimated_uplift < 0
                                ? 'text-rose-600 font-semibold'
                                : 'text-slate-400'
                            }
                          >
                            {formatPercentage(act.estimated_uplift, true)}
                          </span>
                        </td>
                        <td className="py-2.5 px-2 text-right text-slate-700">
                          {formatPercentage(act.support)}
                        </td>
                        <td className="py-2.5 px-2 font-sans">
                          <span
                            className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                              act.confidence === 'HIGH'
                                ? 'bg-emerald-100 text-emerald-800'
                                : act.confidence === 'LOW'
                                ? 'bg-amber-100 text-amber-800'
                                : 'bg-slate-100 text-slate-700'
                            }`}
                          >
                            {act.confidence}
                          </span>
                        </td>
                        <td className="py-2.5 px-2 text-right">
                          <span
                            className={
                              act.expected_incremental_value_paise > 0
                                ? 'text-emerald-700 font-bold'
                                : act.expected_incremental_value_paise < 0
                                ? 'text-rose-700'
                                : 'text-slate-400'
                            }
                          >
                            {formatPaiseToINR(act.expected_incremental_value_paise)}
                          </span>
                        </td>
                        <td className="py-2.5 px-2 text-right font-sans">
                          {isSelected ? (
                            <Badge variant="success">SELECTED</Badge>
                          ) : isPolicyRejected ? (
                            <Badge variant="danger">REJECTED</Badge>
                          ) : isAbstained ? (
                            <Badge variant="warning">ABSTAINED</Badge>
                          ) : (
                            <span className="text-[11px] text-slate-400">AVAILABLE</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Explanation Note */}
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs space-y-1">
              <span className="font-bold text-slate-800 block uppercase tracking-wider text-[10px]">
                Autonomous Reasoning & Policy Explanation
              </span>
              <p className="text-slate-600 leading-relaxed">
                {decision?.explanation}
              </p>
              {decision?.rejection_reason && (
                <div className="mt-2 text-rose-700 font-medium flex items-center gap-1.5">
                  <ShieldAlert className="w-3.5 h-3.5" />
                  <span>Governor Block Reason: {decision.rejection_reason}</span>
                </div>
              )}
            </div>

            {/* Action Trigger Box */}
            <div className="pt-2 border-t border-slate-100 flex items-center justify-between gap-3">
              <div>
                <span className="text-[11px] text-slate-400 block font-semibold uppercase tracking-wider">
                  Recommended Action
                </span>
                <span className="font-mono font-bold text-slate-900 text-sm">
                  {decision?.candidate_actions.find(a => a.action === decision.recommended_action)?.name || 'NO_ACTION'}
                </span>
              </div>

              <button
                id="btn-execute-action"
                onClick={handleExecute}
                disabled={executing}
                className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-xs font-bold text-white shadow-xs transition-all ${
                  executing
                    ? 'bg-slate-400 cursor-not-allowed'
                    : 'bg-emerald-600 hover:bg-emerald-700 active:scale-98'
                }`}
              >
                {executing ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Authorizing...</span>
                  </>
                ) : (
                  <>
                    <Zap className="w-3.5 h-3.5" />
                    <span>Authorize & Dispatch</span>
                  </>
                )}
              </button>
            </div>

            {/* Inline Execution Feedback Notification */}
            {executionResult && (
              <div className="p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-xs space-y-1">
                <div className="flex items-center gap-1.5 text-emerald-800 font-bold">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Execution Authorized & Dispatched</span>
                </div>
                <div className="text-emerald-700 font-mono text-[11px]">
                  Correlation ID: {executionResult.correlation_id}
                </div>
                <div className="text-slate-600 text-[11px]">
                  State: <Badge variant="info">{executionResult.status}</Badge> · Webhook callback listener armed.
                </div>
              </div>
            )}

            {executionError && (
              <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs space-y-1">
                <div className="flex items-center gap-1.5 text-rose-800 font-bold">
                  <XCircle className="w-4 h-4 text-rose-600" />
                  <span>Execution Blocked</span>
                </div>
                <div className="text-rose-700 text-[11px]">
                  {executionError}
                </div>
              </div>
            )}
          </div>

          {/* VISUAL DECISION PIPELINE STEPPER */}
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs space-y-3">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
              Autonomous Governance Flow
            </span>

            <div className="grid grid-cols-6 gap-1 text-center font-mono text-[10px]">
              <div className="p-2 rounded bg-blue-50 border border-blue-200 text-blue-800 font-bold">
                1. MODEL
              </div>
              <div className="p-2 rounded bg-indigo-50 border border-indigo-200 text-indigo-800 font-bold">
                2. SUPPORT
              </div>
              <div className="p-2 rounded bg-amber-50 border border-amber-200 text-amber-800 font-bold">
                3. ECONOMICS
              </div>
              <div className={`p-2 rounded font-bold border ${
                decision?.governor_status === 'POLICY_REJECTED'
                  ? 'bg-rose-50 border-rose-300 text-rose-800'
                  : 'bg-purple-50 border-purple-200 text-purple-800'
              }`}>
                4. GOVERNOR
              </div>
              <div className="p-2 rounded bg-slate-100 border border-slate-300 text-slate-800 font-bold">
                5. RAZORPAY
              </div>
              <div className="p-2 rounded bg-emerald-50 border border-emerald-200 text-emerald-800 font-bold">
                6. VERIFIED
              </div>
            </div>

            <div className="text-[11px] text-slate-500 text-center">
              Deterministic 6-stage gate: No action reaches Razorpay without positivity support and governor sign-off.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
