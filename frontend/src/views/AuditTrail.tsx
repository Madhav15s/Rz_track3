import { useState, useEffect } from 'react';
import {
  List,
  Clock,
  Filter,
  RefreshCw,
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  Search,
} from 'lucide-react';
import { fetchAudit } from '../api';
import type { AuditEvent } from '../types';
import { formatDateTime } from '../utils/formatters';
import { Badge } from '../components/Badge';

export default function AuditTrail() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [filterCase, setFilterCase] = useState<string>('ALL');
  const [loading, setLoading] = useState(true);

  const loadAuditData = async () => {
    setLoading(true);
    try {
      const data = await fetchAudit(filterCase === 'ALL' ? undefined : filterCase);
      setEvents(data);
    } catch (err) {
      console.error('Error fetching audit:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAuditData();
  }, [filterCase]);

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-md bg-slate-800 text-white">
              <List className="w-4 h-4" />
            </span>
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              Immutable Governance Audit Trail
            </h1>
            <Badge variant="default">Append-Only Event Ledger</Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Complete cryptographic trace of model estimates, support checks, governor rulings, and payment outcomes.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Case Filter */}
          <select
            value={filterCase}
            onChange={(e) => setFilterCase(e.target.value)}
            className="text-xs border border-slate-200 rounded-lg px-2.5 py-1.5 bg-white text-slate-700 font-mono shadow-xs"
          >
            <option value="ALL">All Cases</option>
            <option value="CASE_A_POS_UPLIFT">CASE_A_POS_UPLIFT</option>
            <option value="CASE_B_NATURAL_TRAP">CASE_B_NATURAL_TRAP</option>
            <option value="CASE_C_OUT_OF_SUPPORT">CASE_C_OUT_OF_SUPPORT</option>
            <option value="CASE_D_POLICY_REJECT">CASE_D_POLICY_REJECT</option>
            <option value="CASE_E_VERIFIED">CASE_E_VERIFIED</option>
          </select>

          <button
            onClick={loadAuditData}
            className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-600 hover:bg-slate-50 shadow-xs"
            title="Refresh Audit Logs"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Structured Timeline Table */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-xs overflow-hidden">
        <div className="p-4 border-b border-slate-100 bg-slate-50/70 flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-700">
            Audit Ledger ({events.length} records)
          </span>
          <span className="text-xs text-slate-500 font-mono">
            Compliant with SOC-2 & ISO-27001 Financial Auditing
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 text-slate-500 font-semibold uppercase tracking-wider text-[11px]">
                <th className="py-2.5 px-3">Timestamp</th>
                <th className="py-2.5 px-3">Case ID</th>
                <th className="py-2.5 px-3">Decision / Event</th>
                <th className="py-2.5 px-3">Model</th>
                <th className="py-2.5 px-3">Policy</th>
                <th className="py-2.5 px-3">Execution & Details</th>
                <th className="py-2.5 px-3">Verification</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {events.map((evt) => {
                const isVerified = evt.event_type.includes('VERIFIED');
                const isRejected = evt.event_type.includes('REJECTED');

                return (
                  <tr key={evt.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="py-3 px-3 whitespace-nowrap text-slate-500 font-mono text-[11px]">
                      {formatDateTime(evt.timestamp)}
                    </td>

                    <td className="py-3 px-3 whitespace-nowrap font-mono font-bold text-slate-900">
                      {evt.case_id}
                    </td>

                    <td className="py-3 px-3 whitespace-nowrap">
                      <Badge
                        variant={
                          isVerified
                            ? 'success'
                            : isRejected
                            ? 'danger'
                            : evt.event_type.includes('ABSTAINED')
                            ? 'warning'
                            : 'info'
                        }
                      >
                        {evt.event_type}
                      </Badge>
                    </td>

                    <td className="py-3 px-3 whitespace-nowrap font-mono text-slate-600 text-[11px]">
                      {evt.model_version || 'T-Learner v1.4'}
                    </td>

                    <td className="py-3 px-3 whitespace-nowrap font-mono text-slate-600 text-[11px]">
                      {evt.policy_version || 'Gov-v2.1'}
                    </td>

                    <td className="py-3 px-3 text-slate-700">
                      <div className="font-mono text-[11px] text-slate-500 mb-0.5">
                        {evt.correlation_id}
                      </div>
                      <div className="text-slate-800 text-xs">{evt.description}</div>
                    </td>

                    <td className="py-3 px-3 whitespace-nowrap">
                      {isVerified ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700">
                          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                          <span>CAPTURED</span>
                        </span>
                      ) : isRejected ? (
                        <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-rose-700">
                          <ShieldAlert className="w-3.5 h-3.5 text-rose-600" />
                          <span>BLOCKED</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[11px] text-slate-400">
                          <span>PENDING</span>
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })}

              {events.length === 0 && (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-slate-400 text-xs">
                    No audit records matching criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
