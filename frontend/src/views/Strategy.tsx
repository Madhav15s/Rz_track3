
import { Briefcase, CheckCircle2 } from 'lucide-react';

export default function Strategy() {
  return (
    <div className="p-8 max-w-4xl">
      <h2 className="text-2xl font-bold text-slate-800 mb-6">Recovery Strategy</h2>
      
      <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 mb-6">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <Briefcase className="w-5 h-5 mr-2 text-blue-600" />
          Active Policy Guidelines
        </h3>
        <p className="text-slate-600 mb-6 text-sm">
          The causal recovery engine balances aggressive revenue retrieval with customer lifetime value (LTV). Current strategies favor long-term retention over immediate extraction for high-value segments.
        </p>

        <div className="space-y-4">
          <div className="flex items-start">
            <CheckCircle2 className="w-5 h-5 text-emerald-500 mr-3 mt-0.5" />
            <div>
              <h4 className="font-medium text-slate-800">Dynamic Discounting</h4>
              <p className="text-sm text-slate-500">Only offer discounts if causal uplift probability &gt; 65% and net economic value is positive.</p>
            </div>
          </div>
          <div className="flex items-start">
            <CheckCircle2 className="w-5 h-5 text-emerald-500 mr-3 mt-0.5" />
            <div>
              <h4 className="font-medium text-slate-800">Communication Throttling</h4>
              <p className="text-sm text-slate-500">Maximum of 2 touchpoints per 7-day period to prevent alert fatigue.</p>
            </div>
          </div>
          <div className="flex items-start">
            <CheckCircle2 className="w-5 h-5 text-emerald-500 mr-3 mt-0.5" />
            <div>
              <h4 className="font-medium text-slate-800">VIP Fast-Track</h4>
              <p className="text-sm text-slate-500">Customers with LTV &gt; $10,000 bypass standard dunning and route directly to account managers.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
