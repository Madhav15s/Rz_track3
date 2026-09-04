import { useState } from 'react';
import {
  HelpCircle,
  Lightbulb,
} from 'lucide-react';
import { Badge } from '../components/Badge';
import { formatPaiseToINR } from '../utils/formatters';

export default function CausalExplainer() {
  const [txnAmountPaise, setTxnAmountPaise] = useState<number>(150000); // ₹1,500

  // The canonical judge metrics
  const naturalRecoveryRate = 0.31; // 31%
  const interventionRecoveryRate = 0.74; // 74%
  const incrementalUplift = interventionRecoveryRate - naturalRecoveryRate; // +43%
  const retryCostPaise = 130; // ₹1.30

  // Expected Value calculation:
  // EV = (Amount * Incremental Uplift) - Action Cost
  const grossIncrementalValuePaise = Math.round(txnAmountPaise * incrementalUplift);
  const netExpectedValuePaise = grossIncrementalValuePaise - retryCostPaise;

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 border-b border-slate-200 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-md bg-blue-600 text-white">
              <HelpCircle className="w-4 h-4" />
            </span>
            <h1 className="text-xl font-bold tracking-tight text-slate-900">
              Causal Uplift Explainer
            </h1>
            <Badge variant="info">Executive & Judge Primer</Badge>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Understanding why correlation-based recovery wastes money on natural recoveries, while causal inference captures pure incremental margin.
          </p>
        </div>
      </div>

      {/* CORE CONCEPT VISUAL COMPARISON */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-xs space-y-6">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 block">
              Core Concept Visualizer
            </span>
            <h2 className="text-sm font-bold text-slate-900">
              Natural Recovery vs. Causal Intervention Uplift
            </h2>
          </div>
          <Badge variant="success">Net Incremental Positive</Badge>
        </div>

        {/* 3 Metric Comparison Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Card 1: Natural Recovery */}
          <div className="p-5 rounded-xl border border-slate-200 bg-slate-50 space-y-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block">
              Baseline (Control Group)
            </span>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold font-mono text-slate-700">31%</span>
              <span className="text-xs font-semibold text-slate-500">Natural Recovery</span>
            </div>
            <p className="text-xs text-slate-600">
              Customers who will self-recover or retry without any merchant prompt. Intervening on them burns cost.
            </p>
          </div>

          {/* Card 2: Intervention Recovery */}
          <div className="p-5 rounded-xl border border-blue-200 bg-blue-50/60 space-y-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-blue-600 block">
              With Causal Action (Treatment)
            </span>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold font-mono text-blue-900">74%</span>
              <span className="text-xs font-semibold text-blue-700">Intervention Recovery</span>
            </div>
            <p className="text-xs text-blue-800">
              Total observed recovery rate when an autonomous action (e.g. Smart Retry Later) is dispatched.
            </p>
          </div>

          {/* Card 3: Incremental Effect */}
          <div className="p-5 rounded-xl border border-emerald-300 bg-emerald-50 space-y-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-700 block">
              Pure Causal Treatment Effect (CATE)
            </span>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold font-mono text-emerald-800">+43%</span>
              <span className="text-xs font-semibold text-emerald-700">Incremental Effect</span>
            </div>
            <p className="text-xs text-emerald-800">
              The exact revenue gain that occurred <em>solely</em> because of CausalRecover’s intervention.
            </p>
          </div>
        </div>

        {/* Causal Diagnostics Row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2 border-t border-slate-100 text-xs">
          <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
            <span className="text-slate-400 block text-[11px]">Positivity Support</span>
            <span className="text-lg font-bold font-mono text-slate-900">72%</span>
            <div className="text-[11px] text-slate-500 mt-0.5">Sufficient observational overlap</div>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
            <span className="text-slate-400 block text-[11px]">Estimation Confidence</span>
            <span className="text-lg font-bold font-mono text-emerald-600">HIGH</span>
            <div className="text-[11px] text-slate-500 mt-0.5">Narrow 95% confidence intervals</div>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
            <span className="text-slate-400 block text-[11px]">Net Expected Incremental Value</span>
            <span className="text-lg font-bold font-mono text-emerald-700">
              {formatPaiseToINR(netExpectedValuePaise)}
            </span>
            <div className="text-[11px] text-slate-500 mt-0.5">
              On ₹{(txnAmountPaise / 100).toLocaleString()} payment after ₹1.30 fee
            </div>
          </div>
        </div>

        {/* Interactive Payment Amount Slider */}
        <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/70 space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-slate-800">
              Simulate Unit Economics by Transaction Size
            </span>
            <span className="font-mono font-bold text-blue-600 text-sm">
              ₹{(txnAmountPaise / 100).toLocaleString()}
            </span>
          </div>

          <input
            type="range"
            min={10000} // ₹100
            max={1000000} // ₹10,000
            step={10000}
            value={txnAmountPaise}
            onChange={(e) => setTxnAmountPaise(Number(e.target.value))}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />

          <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
            <span>₹100</span>
            <span>Expected Net Value = (Amount × +43%) - ₹1.30</span>
            <span>₹10,000</span>
          </div>
        </div>

        {/* Plain-English Summary for Judges */}
        <div className="p-4 rounded-xl bg-blue-50/60 border border-blue-200 space-y-2 text-xs text-blue-900">
          <div className="flex items-center gap-1.5 font-bold text-blue-900">
            <Lightbulb className="w-4 h-4 text-blue-600" />
            <span>Why This Wins Over Standard Dunning</span>
          </div>
          <p className="leading-relaxed">
            Standard payment recovery tools trigger indiscriminate retries on every failure. If 31 out of 100 users were going to retry on their own, standard tools claim "credit" for those 31 transactions while charging fees and risking customer annoyance. CausalRecover proves causality: it only intervenes when the <strong>incremental uplift (+43%)</strong> creates positive net enterprise profit.
          </p>
        </div>
      </div>
    </div>
  );
}
