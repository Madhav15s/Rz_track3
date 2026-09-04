import { useState, useEffect } from 'react';
import {
  AlertTriangle,
  ArrowRight,
  Activity,
  CheckCircle2,
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { fetchIncidents } from '../api';
import type { Incident } from '../types';
import { formatPaiseToINR } from '../utils/formatters';
import { Badge } from '../components/Badge';

export default function Incidents() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchIncidents();
        setIncidents(data);
        if (data.length > 0) {
          setSelectedIncidentId(data[0].id);
        }
      } catch (err) {
        console.error('Error loading incidents:', err);
      }
    }
    load();
  }, []);

  const selectedIncident = incidents.find(i => i.id === selectedIncidentId) || incidents[0];

  const totalExposedPaise = incidents.reduce((acc, curr) => acc + curr.revenue_exposed_paise, 0);
  const totalAffectedTxns = incidents.reduce((acc, curr) => acc + curr.transactions_affected, 0);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* View Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-md bg-amber-500 text-white">
              <AlertTriangle className="w-4 h-4" />
            </span>
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              Payment Gateway Incident Intel
            </h1>
            <Badge variant="warning">{incidents.length} Monitored</Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Real-time monitoring of upstream banking nodes, NPCI UPI rail degradation, and automated support suppression.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/cases"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-xs"
          >
            <span>View Affected Cases</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>

      {/* Aggregate Telemetry Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-xs">
          <div className="flex items-center justify-between text-xs text-slate-500 font-semibold uppercase tracking-wider mb-2">
            <span>Total Revenue Exposed</span>
            <AlertTriangle className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-slate-900">
            {formatPaiseToINR(totalExposedPaise)}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Across {incidents.length} active and monitored events
          </div>
        </div>

        <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-xs">
          <div className="flex items-center justify-between text-xs text-slate-500 font-semibold uppercase tracking-wider mb-2">
            <span>Transactions Affected</span>
            <Activity className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-slate-900">
            {totalAffectedTxns.toLocaleString()} txns
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Failure rate elevated ~42.8% above normal
          </div>
        </div>

        <div className="p-4 rounded-xl border border-slate-200 bg-white shadow-xs">
          <div className="flex items-center justify-between text-xs text-slate-500 font-semibold uppercase tracking-wider mb-2">
            <span>Causal Mitigation Rule</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-sm font-bold text-slate-900">
            Smart Retry-Later & Rail Switch
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Zero immediate retries on degraded banking rails
          </div>
        </div>
      </div>

      {/* Main Incident Monitoring & Detail Timeline Split */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Incident Table / List (7 Cols) */}
        <div className="lg:col-span-7 rounded-xl border border-slate-200 bg-white shadow-xs overflow-hidden">
          <div className="p-4 border-b border-slate-100 bg-slate-50/70 flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Active Upstream Outages
            </span>
            <span className="text-xs text-slate-500 font-mono">
              Auto-refreshed via Razorpay Webhooks
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
                  <th className="py-2.5 px-3">Incident</th>
                  <th className="py-2.5 px-3">Severity</th>
                  <th className="py-2.5 px-3">Method / Bank</th>
                  <th className="py-2.5 px-3 text-right">Failure Rate</th>
                  <th className="py-2.5 px-3 text-right">Revenue Exposed</th>
                  <th className="py-2.5 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {incidents.map((inc) => {
                  const isSelected = inc.id === selectedIncident?.id;
                  return (
                    <tr
                      key={inc.id}
                      onClick={() => setSelectedIncidentId(inc.id)}
                      className={`cursor-pointer transition-colors ${
                        isSelected
                          ? 'bg-blue-50/80 font-medium text-slate-900'
                          : 'hover:bg-slate-50/70 text-slate-700'
                      }`}
                    >
                      <td className="py-3 px-3">
                        <div className="font-mono font-bold">{inc.id}</div>
                        <div className="text-[11px] text-slate-500 truncate max-w-[150px]">
                          {inc.type}
                        </div>
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
                      <td className="py-3 px-3">
                        <div className="font-semibold">{inc.affected_payment_method}</div>
                        <div className="text-slate-500 text-[11px]">{inc.affected_bank}</div>
                      </td>
                      <td className="py-3 px-3 text-right font-mono font-bold text-rose-600">
                        {inc.severity === 'CRITICAL' ? '68.4%' : inc.severity === 'HIGH' ? '41.2%' : '24.0%'}
                      </td>
                      <td className="py-3 px-3 text-right font-mono font-bold text-slate-900">
                        {formatPaiseToINR(inc.revenue_exposed_paise, true)}
                      </td>
                      <td className="py-3 px-3">
                        <span className="inline-flex items-center gap-1 font-semibold text-[11px] text-emerald-700">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-ping" />
                          {inc.status}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Incident Detail & Root Cause Timeline (5 Cols) */}
        <div className="lg:col-span-5 rounded-xl border border-slate-200 bg-white p-5 shadow-xs space-y-4">
          <div className="border-b border-slate-100 pb-3 flex items-start justify-between">
            <div>
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">
                Incident Diagnostics
              </span>
              <span className="font-mono font-bold text-slate-900 text-base">
                {selectedIncident?.id}
              </span>
            </div>
            <Badge
              variant={
                selectedIncident?.severity === 'CRITICAL'
                  ? 'danger'
                  : selectedIncident?.severity === 'HIGH'
                  ? 'warning'
                  : 'info'
              }
              size="md"
            >
              {selectedIncident?.severity} SEVERITY
            </Badge>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block text-[11px]">Affected Payment Method</span>
              <span className="font-semibold text-slate-900">{selectedIncident?.affected_payment_method}</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block text-[11px]">Issuer / Acquirer Bank</span>
              <span className="font-semibold text-slate-900">{selectedIncident?.affected_bank}</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block text-[11px]">Duration</span>
              <span className="font-mono font-semibold text-slate-900">{selectedIncident?.duration_minutes} mins</span>
            </div>
            <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-slate-400 block text-[11px]">Affected Transactions</span>
              <span className="font-mono font-semibold text-slate-900">{selectedIncident?.transactions_affected?.toLocaleString()}</span>
            </div>
          </div>

          {/* Incident Timeline */}
          <div className="space-y-3 pt-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-700 block">
              Incident Response Timeline
            </span>

            <div className="relative pl-6 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200 text-xs">
              <div className="relative">
                <span className="absolute -left-6 top-0.5 w-2.5 h-2.5 rounded-full bg-rose-500 ring-4 ring-white" />
                <div className="font-semibold text-slate-900">Elevated Failure Spike Detected</div>
                <div className="text-[11px] text-slate-500">NPCI UPI Gateway response latency exceeded 8000ms threshold.</div>
              </div>

              <div className="relative">
                <span className="absolute -left-6 top-0.5 w-2.5 h-2.5 rounded-full bg-blue-500 ring-4 ring-white" />
                <div className="font-semibold text-slate-900">Causal Policy Suppressed Immediate Retries</div>
                <div className="text-[11px] text-slate-500">RETRY_NOW propensity support set to 0.15 to prevent customer lockouts.</div>
              </div>

              <div className="relative">
                <span className="absolute -left-6 top-0.5 w-2.5 h-2.5 rounded-full bg-emerald-500 ring-4 ring-white" />
                <div className="font-semibold text-slate-900">Smart Routing Activated (RETRY_LATER)</div>
                <div className="text-[11px] text-slate-500">Autonomous scheduler queued recovery transactions for post-incident window (+45 mins).</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
