
import { Shield, ShieldCheck } from 'lucide-react';

export default function Safety() {
  return (
    <div className="p-8 max-w-5xl">
      <h2 className="text-2xl font-bold text-slate-800 mb-6">Safety & Governor</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-6">
          <div className="flex items-center text-emerald-700 mb-2">
            <ShieldCheck className="w-6 h-6 mr-2" />
            <h3 className="font-semibold text-lg">System Safe</h3>
          </div>
          <p className="text-emerald-600 text-sm">All governor limits are within normal operating bounds.</p>
        </div>
        
        <div className="bg-white border border-slate-200 rounded-lg p-6 text-center shadow-sm">
          <div className="text-4xl font-bold text-slate-800 mb-1">0</div>
          <div className="text-sm text-slate-500 font-medium uppercase tracking-wide">Policy Violations</div>
        </div>
        
        <div className="bg-white border border-slate-200 rounded-lg p-6 text-center shadow-sm">
          <div className="text-4xl font-bold text-slate-800 mb-1">99.9%</div>
          <div className="text-sm text-slate-500 font-medium uppercase tracking-wide">Action Confidence</div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-bold mb-6">Decision Pipeline Validation</h3>
        
        <div className="relative">
          <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-slate-200"></div>
          
          <div className="space-y-8 relative">
            <div className="flex items-start">
              <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center border-4 border-white z-10">
                <span className="font-bold text-blue-600">1</span>
              </div>
              <div className="ml-6 pt-2">
                <h4 className="font-bold text-slate-800">Causal Model</h4>
                <p className="text-sm text-slate-500 mt-1">Generates raw uplift estimates and candidate actions.</p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center border-4 border-white z-10">
                <span className="font-bold text-blue-600">2</span>
              </div>
              <div className="ml-6 pt-2">
                <h4 className="font-bold text-slate-800">Support Filter</h4>
                <p className="text-sm text-slate-500 mt-1">Eliminates actions with insufficient historical data context (requires &gt; 50 data points).</p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center border-4 border-white z-10">
                <span className="font-bold text-blue-600">3</span>
              </div>
              <div className="ml-6 pt-2">
                <h4 className="font-bold text-slate-800">Economic Value Threshold</h4>
                <p className="text-sm text-slate-500 mt-1">Validates that Net Incremental Value &gt; $0 accounting for discount costs.</p>
              </div>
            </div>

            <div className="flex items-start">
              <div className="w-12 h-12 rounded-full bg-emerald-100 flex items-center justify-center border-4 border-white z-10">
                <Shield className="w-5 h-5 text-emerald-600" />
              </div>
              <div className="ml-6 pt-2">
                <h4 className="font-bold text-emerald-800">Governor Policy Check</h4>
                <p className="text-sm text-emerald-700 mt-1">Final gate: Enforces global caps, brand safety rules, and frequency limits.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
