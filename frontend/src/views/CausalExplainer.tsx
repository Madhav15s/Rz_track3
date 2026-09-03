
import { HelpCircle, ArrowRight } from 'lucide-react';

export default function CausalExplainer() {
  return (
    <div className="p-8 max-w-5xl">
      <h2 className="text-2xl font-bold text-slate-800 mb-6 flex items-center">
        <HelpCircle className="mr-2 text-slate-700" /> Causal Inference Explainer
      </h2>

      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-8">
        <h3 className="text-xl font-bold text-slate-800 mb-8 text-center">Understanding Incremental Value</h3>

        <div className="flex flex-col md:flex-row items-center justify-center gap-12">
          
          {/* Natural Recovery */}
          <div className="flex flex-col items-center w-64">
            <div className="h-48 w-24 bg-slate-100 rounded-t-md border border-slate-300 relative flex items-end justify-center pb-4">
              <div className="absolute top-4 text-xs font-bold text-slate-500 uppercase tracking-wide w-full text-center px-2">
                Will recover anyway
              </div>
              <div className="w-16 h-24 bg-slate-300 rounded-sm"></div>
            </div>
            <div className="mt-4 text-center">
              <h4 className="font-bold text-slate-700">Natural Recovery</h4>
              <p className="text-xs text-slate-500 mt-1">Control Group Baseline</p>
            </div>
          </div>

          <ArrowRight className="text-slate-300 w-8 h-8 hidden md:block" />

          {/* Treatment Result */}
          <div className="flex flex-col items-center w-64">
            <div className="h-48 w-24 bg-slate-100 rounded-t-md border border-slate-300 relative flex flex-col justify-end items-center pb-4">
              {/* Incremental Block */}
              <div className="w-16 h-12 bg-blue-500 rounded-t-sm relative flex items-center justify-center">
                <span className="text-white text-xs font-bold">UPLIFT</span>
                <div className="absolute -right-24 top-2 text-xs font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded border border-blue-200 shadow-sm whitespace-nowrap">
                  Incremental Value
                </div>
              </div>
              {/* Base Block */}
              <div className="w-16 h-24 bg-slate-300 rounded-b-sm relative flex items-center justify-center">
                <span className="text-slate-500 text-xs font-bold">BASE</span>
              </div>
            </div>
            <div className="mt-4 text-center">
              <h4 className="font-bold text-slate-700">Treatment Effect</h4>
              <p className="text-xs text-slate-500 mt-1">With Causal Intervention</p>
            </div>
          </div>

        </div>

        <div className="mt-12 bg-slate-50 p-6 rounded-lg border border-slate-200">
          <h4 className="font-bold text-slate-800 mb-2">Why this matters</h4>
          <p className="text-slate-600 text-sm leading-relaxed mb-4">
            Traditional models optimize for <strong>Gross Recovery</strong>, targeting customers who are likely to recover regardless of intervention. This leads to wasted spend (giving discounts to customers who would have paid anyway).
          </p>
          <p className="text-slate-600 text-sm leading-relaxed">
            CausalRecover specifically identifies <strong>Persuadables</strong>: customers whose behavior changes <em>because</em> of the intervention. The goal is to maximize the blue "Uplift" block while minimizing intervention costs on the grey "Base" block.
          </p>
        </div>
      </div>
    </div>
  );
}
