import { useState } from 'react';
import {
  Zap,
  Server,
  Code2,
} from 'lucide-react';
import { Badge } from '../components/Badge';

export default function Execution() {
  const [selectedBranch, setSelectedBranch] = useState<'APPROVED' | 'REJECTED'>('APPROVED');

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-md bg-blue-600 text-white">
              <Zap className="w-4 h-4" />
            </span>
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              Execution Gateway & State Machine
            </h1>
            <Badge variant="info">Razorpay Adapter Loop</Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Tracking lifecycle states from initial causal proposal to governor authorization and verified webhook recovery.
          </p>
        </div>
      </div>

      {/* RAZORPAY TEST MODE vs SIMULATED Differentiation Banner */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-xl border border-blue-200 bg-blue-50/70 p-5 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-bold text-blue-900 text-sm">
              <Server className="w-4 h-4 text-blue-600" />
              <span>RAZORPAY TEST MODE</span>
            </div>
            <Badge variant="info">EXTERNAL API ADAPTER</Badge>
          </div>
          <p className="text-xs text-blue-800 leading-relaxed">
            Active gateway credentials (<code className="font-mono text-[11px] bg-blue-100 px-1 py-0.5 rounded">rzp_test_...</code>) authenticating direct API dispatches against Razorpay sandbox endpoints. Dispatches authentic orders, handles payment links, and receives cryptographic webhook events.
          </p>
          <div className="pt-2 text-[11px] font-mono text-blue-700 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-500" />
            <span>Endpoint: https://api.razorpay.com/v1/payments</span>
          </div>
        </div>

        <div className="rounded-xl border border-slate-300 bg-slate-50 p-5 shadow-xs space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-bold text-slate-800 text-sm">
              <Code2 className="w-4 h-4 text-slate-600" />
              <span>SIMULATED MODE</span>
            </div>
            <Badge variant="default">LOCAL EVENT LOOP</Badge>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Deterministic in-memory counterfactual generator (<code className="font-mono text-[11px] bg-slate-200 px-1 py-0.5 rounded">sim_req_...</code>) used during offline backtesting, synthetic benchmark evaluations, and demo verification when sandbox API calls are bypassed.
          </p>
          <div className="pt-2 text-[11px] font-mono text-slate-500 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-slate-400" />
            <span>Endpoint: local::sqlite::causal_recover.db</span>
          </div>
        </div>
      </div>

      {/* STATE MACHINE VISUALIZATION */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block">
              Execution Lifecycle State Machine
            </span>
            <h2 className="text-sm font-bold text-slate-900">
              State Transition Diagram & Guardrail Branching
            </h2>
          </div>

          <div className="flex items-center gap-2 bg-slate-100 p-1 rounded-lg text-xs">
            <button
              onClick={() => setSelectedBranch('APPROVED')}
              className={`px-3 py-1 rounded-md font-semibold transition-all ${
                selectedBranch === 'APPROVED' ? 'bg-white text-slate-900 shadow-xs' : 'text-slate-600'
              }`}
            >
              Happy Path (Approved)
            </button>
            <button
              onClick={() => setSelectedBranch('REJECTED')}
              className={`px-3 py-1 rounded-md font-semibold transition-all ${
                selectedBranch === 'REJECTED' ? 'bg-white text-rose-700 shadow-xs' : 'text-slate-600'
              }`}
            >
              Policy Rejection Path
            </button>
          </div>
        </div>

        {selectedBranch === 'APPROVED' ? (
          /* 4-Step Happy Path */
          <div className="py-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 relative">
              {/* Step 1: PROPOSED */}
              <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 text-xs space-y-2 relative">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-slate-400 font-bold">STATE 01</span>
                  <Badge variant="default">INPUT</Badge>
                </div>
                <div className="font-bold text-slate-900 text-sm">PROPOSED</div>
                <p className="text-slate-500 text-[11px]">
                  Causal model predicts optimal action based on individual treatment effects.
                </p>
                <div className="text-[10px] font-mono text-slate-400 pt-1">
                  Trigger: Failed webhook event
                </div>
              </div>

              {/* Step 2: APPROVED */}
              <div className="p-4 rounded-xl border border-blue-200 bg-blue-50/60 text-xs space-y-2 relative">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-blue-600 font-bold">STATE 02</span>
                  <Badge variant="info">VERIFIED</Badge>
                </div>
                <div className="font-bold text-slate-900 text-sm">APPROVED</div>
                <p className="text-slate-600 text-[11px]">
                  Governor confirms velocity &lt; 3, support &ge; 5%, and net expected value &gt; 0.
                </p>
                <div className="text-[10px] font-mono text-blue-700 pt-1">
                  Outcome: Governor Ticket Signed
                </div>
              </div>

              {/* Step 3: PENDING VERIFICATION */}
              <div className="p-4 rounded-xl border border-amber-200 bg-amber-50/60 text-xs space-y-2 relative">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-amber-600 font-bold">STATE 03</span>
                  <Badge variant="warning">DISPATCHED</Badge>
                </div>
                <div className="font-bold text-slate-900 text-sm">PENDING VERIFICATION</div>
                <p className="text-slate-600 text-[11px]">
                  Action transmitted to Razorpay adapter. Awaiting customer payment confirmation.
                </p>
                <div className="text-[10px] font-mono text-amber-700 pt-1">
                  Listener: Correlation ID registered
                </div>
              </div>

              {/* Step 4: VERIFIED RECOVERED */}
              <div className="p-4 rounded-xl border border-emerald-300 bg-emerald-50 text-xs space-y-2 relative">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-emerald-700 font-bold">STATE 04</span>
                  <Badge variant="success">CLOSED LOOP</Badge>
                </div>
                <div className="font-bold text-emerald-900 text-sm">VERIFIED RECOVERED</div>
                <p className="text-emerald-800 text-[11px]">
                  Cryptographic webhook confirms money captured into merchant settlement account.
                </p>
                <div className="text-[10px] font-mono text-emerald-700 pt-1">
                  Final: Net Incremental Logged
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* 2-Step Policy Rejection Path */
          <div className="py-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl mx-auto">
              <div className="p-4 rounded-xl border border-slate-200 bg-slate-50 text-xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-slate-400 font-bold">STATE 01</span>
                  <Badge variant="default">INPUT</Badge>
                </div>
                <div className="font-bold text-slate-900 text-sm">PROPOSED</div>
                <p className="text-slate-500 text-[11px]">
                  Causal model recommends high-velocity action (e.g., RETRY_NOW on 4th attempt).
                </p>
              </div>

              <div className="p-4 rounded-xl border border-rose-300 bg-rose-50 text-xs space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-mono text-rose-600 font-bold">STATE 02</span>
                  <Badge variant="danger">HARD BLOCKED</Badge>
                </div>
                <div className="font-bold text-rose-900 text-sm">POLICY REJECTED</div>
                <p className="text-rose-800 text-[11px]">
                  Governor halts execution. Reason: Max retry velocity exceeded. Dispatches NO_ACTION.
                </p>
                <div className="text-[10px] font-mono text-rose-700 pt-1">
                  Safety: Merchant brand saved
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
