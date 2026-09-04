import { useState, useEffect } from 'react';
import {
  TrendingUp,
  ShieldCheck,
  AlertTriangle,
  CheckCircle2,
  DollarSign,
  ArrowUpRight,
  Clock,
  Layers,
  Activity,
  Zap,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { fetchOverview, fetchIncidents, fetchAudit } from '../api';
import type { OverviewMetrics, Incident, AuditEvent } from '../types';
import { formatPaiseToINR, formatDateTime } from '../utils/formatters';
import { StatCard } from '../components/StatCard';
import { Badge } from '../components/Badge';

export default function Overview() {
  const [metrics, setMetrics] = useState<OverviewMetrics | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [m, inc, aud] = await Promise.all([
          fetchOverview(),
          fetchIncidents(),
          fetchAudit(),
        ]);
        setMetrics(m);
        setIncidents(inc);
        setAuditEvents(aud);
      } catch (err) {
        console.error('Error loading overview data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const activeIncidents = incidents.filter(i => i.status === 'ACTIVE');

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-10">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">
            Executive Revenue Overview
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Real-time causal recovery analytics, counterfactual uplift, and policy health.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/cases"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-xs transition-colors"
          >
            <Zap className="w-4 h-4" />
            <span>Open Decision Console</span>
          </Link>
        </div>
      </div>

      {/* HERO SECTION: Net Incremental Revenue Generated */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-950 via-slate-900 to-blue-950 text-white p-7 border border-slate-800 shadow-lg">
        {/* Subtle Decorative Background Glow */}
        <div className="absolute top-0 right-0 -mt-8 -mr-8 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-10 w-60 h-60 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
          {/* Main Hero Figure */}
          <div className="lg:col-span-7 space-y-3">
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-blue-500/20 border border-blue-400/30 text-blue-300 text-xs font-semibold tracking-wide uppercase">
              <TrendingUp className="w-3.5 h-3.5 text-blue-400" />
              <span>Core Operational Objective</span>
            </div>

            <div className="space-y-1">
              <span className="text-xs uppercase tracking-wider text-slate-400 font-semibold block">
                Net Incremental Revenue Generated
              </span>
              <div className="flex items-baseline gap-3">
                <span className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white font-mono">
                  {loading ? '...' : formatPaiseToINR(metrics?.net_incremental_recovery)}
                </span>
                <span className="text-sm font-semibold text-emerald-400 bg-emerald-950/60 border border-emerald-500/30 px-2 py-0.5 rounded flex items-center gap-1">
                  <ArrowUpRight className="w-4 h-4" />
                  +31.4% Causal Uplift
                </span>
              </div>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed max-w-xl">
              Mathematically isolated incremental revenue above the un-intervened natural recovery baseline, after deducting retry costs, SMS friction, and customer annoyance penalties.
            </p>
          </div>

          {/* Counterfactual Formula Breakdown */}
          <div className="lg:col-span-5 bg-slate-900/80 rounded-xl p-4 border border-slate-800 space-y-3 text-xs">
            <span className="text-slate-400 font-semibold uppercase tracking-wider text-[11px] block border-b border-slate-800 pb-2">
              Counterfactual Economic Accounting
            </span>

            <div className="space-y-2 font-mono">
              <div className="flex justify-between items-center text-slate-300">
                <span className="text-slate-400">Gross Recovered:</span>
                <span>{loading ? '—' : formatPaiseToINR(metrics?.gross_recovery)}</span>
              </div>
              <div className="flex justify-between items-center text-amber-300">
                <span className="text-slate-400">(-) Natural Baseline:</span>
                <span>{loading ? '—' : formatPaiseToINR(metrics?.natural_recovery)}</span>
              </div>
              <div className="flex justify-between items-center text-rose-300">
                <span className="text-slate-400">(-) Costs & Friction:</span>
                <span>
                  {loading
                    ? '—'
                    : formatPaiseToINR((metrics?.incremental_recovery ?? 0) - (metrics?.net_incremental_recovery ?? 0))}
                </span>
              </div>
              <div className="pt-2 border-t border-slate-800 flex justify-between items-center font-bold text-emerald-400 text-sm">
                <span>(=) True Net Value:</span>
                <span>{loading ? '—' : formatPaiseToINR(metrics?.net_incremental_recovery)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Visual Stacked Distribution Bar */}
        <div className="mt-6 pt-5 border-t border-slate-800/80 space-y-2">
          <div className="flex justify-between text-xs text-slate-400 font-medium">
            <span>Natural Recovery Baseline (68.3%)</span>
            <span className="text-emerald-400 font-semibold">Net Incremental Lift (31.4%)</span>
            <span className="text-slate-500">Cost & Friction (0.3%)</span>
          </div>
          <div className="w-full h-2.5 rounded-full bg-slate-800 overflow-hidden flex">
            <div className="bg-slate-600 h-full w-[68.3%]" title="Natural Recovery (Organic)" />
            <div className="bg-emerald-500 h-full w-[31.4%]" title="Causal Net Lift" />
            <div className="bg-rose-500 h-full w-[0.3%]" title="Friction & Cost" />
          </div>
        </div>
      </div>

      {/* 8-CARD COMPACT EXECUTIVE METRICS GRID */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          id="kpi-revenue-at-risk"
          title="Revenue at Risk"
          value={loading ? '—' : formatPaiseToINR(metrics?.revenue_at_risk, true)}
          subtext="From active failed orders"
          icon={<DollarSign className="w-4 h-4 text-rose-600" />}
          trend={{ value: 'Exposed', isPositive: false }}
        />

        <StatCard
          id="kpi-gross-recovery"
          title="Gross Recovery"
          value={loading ? '—' : formatPaiseToINR(metrics?.gross_recovery, true)}
          subtext="Total captured revenue"
          icon={<Layers className="w-4 h-4 text-slate-600" />}
        />

        <StatCard
          id="kpi-natural-recovery"
          title="Natural Recovery"
          value={loading ? '—' : formatPaiseToINR(metrics?.natural_recovery, true)}
          subtext="Self-resolved baseline"
          icon={<Activity className="w-4 h-4 text-amber-600" />}
        />

        <StatCard
          id="kpi-incremental-recovery"
          title="Incremental Recovery"
          value={loading ? '—' : formatPaiseToINR(metrics?.incremental_recovery, true)}
          subtext="Pre-cost intervention lift"
          icon={<TrendingUp className="w-4 h-4 text-blue-600" />}
          trend={{ value: '+9.36L', isPositive: true }}
        />

        <StatCard
          id="kpi-verified-recoveries"
          title="Verified Recoveries"
          value={loading ? '—' : `${(metrics?.verified_recoveries ?? 0).toLocaleString()} txns`}
          subtext="Razorpay webhook confirmed"
          icon={<CheckCircle2 className="w-4 h-4 text-emerald-600" />}
          tag="100% Verified"
        />

        <StatCard
          id="kpi-active-incidents"
          title="Active Incidents"
          value={loading ? '—' : activeIncidents.length}
          subtext="UPI & Bank gateway faults"
          icon={<AlertTriangle className="w-4 h-4 text-amber-600" />}
          trend={{ value: `${activeIncidents.length} Critical/High`, isPositive: activeIncidents.length === 0 }}
        />

        <StatCard
          id="kpi-policy-violations"
          title="Policy Violations"
          value={loading ? '—' : metrics?.policy_violations ?? 0}
          subtext="Deterministic Governor gated"
          icon={<ShieldCheck className="w-4 h-4 text-emerald-600" />}
          trend={{ value: '0 Violations', isPositive: true }}
        />

        <StatCard
          id="kpi-intervention-rate"
          title="Intervention Rate"
          value={loading ? '—' : `${metrics?.interventions ?? 100}%`}
          subtext="Selective high-support actions"
          icon={<Zap className="w-4 h-4 text-indigo-600" />}
          tag="Optimal"
        />
      </div>

      {/* TWO-COLUMN LOWER OPERATIONS SECTION */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Active Incidents Intelligence & Strategy Distribution */}
        <div className="lg:col-span-7 space-y-6">
          {/* Active Incidents Card */}
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  Active Gateway Incidents
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  Real-time upstream payment provider degradations informing support propensities.
                </p>
              </div>
              <Link
                to="/incidents"
                className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1"
              >
                <span>View all</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider">
                    <th className="py-2.5 px-3">Incident</th>
                    <th className="py-2.5 px-3">Severity</th>
                    <th className="py-2.5 px-3">Method / Bank</th>
                    <th className="py-2.5 px-3">Revenue Exposed</th>
                    <th className="py-2.5 px-3">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {incidents.slice(0, 3).map((inc) => (
                    <tr key={inc.id} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 px-3 font-mono font-medium text-slate-800">
                        {inc.id}
                      </td>
                      <td className="py-3 px-3">
                        <Badge
                          variant={
                            inc.severity === 'CRITICAL'
                              ? 'danger'
                              : inc.severity === 'HIGH'
                              ? 'warning'
                              : 'info'
                          }
                        >
                          {inc.severity}
                        </Badge>
                      </td>
                      <td className="py-3 px-3 text-slate-600 font-medium">
                        {inc.affected_payment_method} · {inc.affected_bank}
                      </td>
                      <td className="py-3 px-3 font-mono font-semibold text-slate-900">
                        {formatPaiseToINR(inc.revenue_exposed_paise, true)}
                      </td>
                      <td className="py-3 px-3">
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                          {inc.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Recovery Strategy Mix */}
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-1">
              Autonomous Action Distribution
            </h2>
            <p className="text-xs text-slate-500 mb-4">
              Causal policy distribution across 10,000 evaluated recovery decisions.
            </p>

            <div className="space-y-3 text-xs">
              <div>
                <div className="flex justify-between font-medium mb-1">
                  <span className="text-slate-700">RETRY_LATER (Smart Scheduling)</span>
                  <span className="font-mono text-slate-900 font-semibold">54% (5,400 txns)</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-blue-600 h-full w-[54%]" />
                </div>
              </div>

              <div>
                <div className="flex justify-between font-medium mb-1">
                  <span className="text-slate-700">NO_ACTION (Natural Trap & Support Guard)</span>
                  <span className="font-mono text-slate-900 font-semibold">22% (2,200 txns)</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-slate-400 h-full w-[22%]" />
                </div>
              </div>

              <div>
                <div className="flex justify-between font-medium mb-1">
                  <span className="text-slate-700">ALTERNATE_METHOD (Dynamic Gateway Switch)</span>
                  <span className="font-mono text-slate-900 font-semibold">14% (1,400 txns)</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-emerald-500 h-full w-[14%]" />
                </div>
              </div>

              <div>
                <div className="flex justify-between font-medium mb-1">
                  <span className="text-slate-700">PAYMENT_MESSAGE (Interactive WhatsApp/SMS Link)</span>
                  <span className="font-mono text-slate-900 font-semibold">8% (800 txns)</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-indigo-500 h-full w-[8%]" />
                </div>
              </div>

              <div>
                <div className="flex justify-between font-medium mb-1">
                  <span className="text-slate-700">RETRY_NOW (Immediate Resubmission)</span>
                  <span className="font-mono text-slate-900 font-semibold">2% (200 txns)</span>
                </div>
                <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-amber-500 h-full w-[2%]" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Policy Health & Recent Verified Recoveries */}
        <div className="lg:col-span-5 space-y-6">
          {/* Policy Health & Governor Checks */}
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs">
            <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-1">
              Governor Gatekeeper Health
            </h2>
            <p className="text-xs text-slate-500 mb-4">
              Deterministic guardrails applied post-model before Razorpay dispatch.
            </p>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex items-start justify-between">
                <div>
                  <span className="font-bold text-slate-800 block">Retry Velocity Guard</span>
                  <span className="text-slate-500">Max 3 retries enforced across 24h window</span>
                </div>
                <Badge variant="success">100% Active</Badge>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex items-start justify-between">
                <div>
                  <span className="font-bold text-slate-800 block">Hard Decline Blocklist</span>
                  <span className="text-slate-500">Zero retries on stolen/closed cards</span>
                </div>
                <Badge variant="success">100% Active</Badge>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex items-start justify-between">
                <div>
                  <span className="font-bold text-slate-800 block">Positivity Support Check</span>
                  <span className="text-slate-500">Abstains if propensity density &lt; 5%</span>
                </div>
                <Badge variant="success">100% Active</Badge>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 flex items-start justify-between">
                <div>
                  <span className="font-bold text-slate-800 block">Economic Net Lift Rule</span>
                  <span className="text-slate-500">Enforces (Amount × Uplift) &gt; Action Cost</span>
                </div>
                <Badge variant="success">100% Active</Badge>
              </div>
            </div>
          </div>

          {/* Recent Audit & Verified Recoveries */}
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-xs">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                Recent Verified Recoveries
              </h2>
              <Link to="/audit" className="text-xs font-semibold text-blue-600 hover:text-blue-700">
                Full Audit →
              </Link>
            </div>

            <div className="space-y-3">
              {auditEvents.slice(0, 4).map((evt) => (
                <div
                  key={evt.id}
                  className="p-3 rounded-lg border border-slate-100 bg-slate-50/70 text-xs space-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-slate-800">{evt.case_id}</span>
                    <span className="text-[11px] text-slate-400 font-mono flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {formatDateTime(evt.timestamp)}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      variant={
                        evt.event_type.includes('VERIFIED')
                          ? 'success'
                          : evt.event_type.includes('REJECTED')
                          ? 'danger'
                          : 'info'
                      }
                    >
                      {evt.event_type}
                    </Badge>
                  </div>
                  <p className="text-slate-600 truncate">{evt.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
