import { useState, useEffect } from 'react';

import api from '../api';
import { Target, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Case {
  id: string;
  customer_id: string;
  status: string;
  exposed_amount: number;
}

interface Action {
  id: string;
  type: string;
  uplift: number;
  support: number;
  confidence: number;
  value: number;
  status: string;
}

interface Decision {
  case_id: string;
  customer_context: any;
  candidate_actions: Action[];
  final_decision: string;
  logic: string;
}

export default function DecisionConsole() {
  const [cases, setCases] = useState<Case[]>([]);
  const [selectedCase, setSelectedCase] = useState<string | null>(null);
  const [decision, setDecision] = useState<Decision | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    api.get('/cases').then(res => setCases(res.data.cases)).catch(console.error);
  }, []);

  useEffect(() => {
    if (selectedCase) {
      api.get(`/cases/${selectedCase}/decision`).then(res => setDecision(res.data)).catch(console.error);
    }
  }, [selectedCase]);

  const handleExecute = (actionId: string) => {
    if (!selectedCase) return;
    api.post(`/cases/${selectedCase}/execute`, { action_id: actionId })
      .then(() => {
        alert('Execution triggered!');
        navigate('/audit');
      })
      .catch(console.error);
  };

  return (
    <div className="p-8 h-full flex flex-col">
      <h2 className="text-2xl font-bold text-slate-800 mb-6">Causal Decision Console</h2>
      
      <div className="flex gap-6 flex-1 min-h-0">
        {/* Cases List */}
        <div className="w-1/3 bg-white rounded-lg shadow-sm border border-slate-200 flex flex-col">
          <div className="p-4 border-b border-slate-200 bg-slate-50 font-medium">Active Cases</div>
          <div className="overflow-y-auto flex-1 p-2 space-y-2">
            {cases && cases.map(c => (
              <div 
                key={c.case_id} 
                onClick={() => setSelectedCase(c.case_id)}
                className={`p-3 rounded border cursor-pointer transition-colors ${selectedCase === c.case_id ? 'border-blue-500 bg-blue-50' : 'border-slate-200 hover:border-blue-300'}`}
              >
                <div className="flex justify-between items-center mb-1">
                  <span className="font-medium text-sm text-slate-900">{c.case_id}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-700`}>
                    {c.failure_code}
                  </span>
                </div>
                <div className="text-xs font-semibold text-slate-700 mt-1">{c.amount_paise} paise exposed</div>
              </div>
            ))}
          </div>
        </div>

        {/* Decision Detail */}
        <div className="flex-1 bg-white rounded-lg shadow-sm border border-slate-200 flex flex-col overflow-hidden">
          {decision ? (
            <div className="overflow-y-auto p-6">
              <h3 className="text-lg font-bold border-b pb-2 mb-4">Context & Decision Logic</h3>
              
              <div className="mb-6 bg-slate-50 p-4 rounded border border-slate-200">
                <h4 className="text-sm font-semibold text-slate-700 mb-2">Customer Context</h4>
                <pre className="text-xs bg-white p-2 rounded border">{JSON.stringify(decision.customer_context, null, 2)}</pre>
              </div>

              <div className="mb-6">
                <h4 className="text-sm font-semibold text-slate-700 mb-3">Candidate Actions</h4>
                <div className="space-y-3">
                  {decision.candidate_actions.map(action => (
                    <div key={action.action} className="border border-slate-200 rounded p-4 flex justify-between items-center">
                      <div>
                        <div className="font-medium text-sm mb-1">{action.name}</div>
                        <div className="text-xs text-slate-500 flex gap-4">
                          <span>Uplift: {(action.estimated_uplift * 100).toFixed(1)}%</span>
                          <span>Support: {(action.support * 100).toFixed(1)}%</span>
                          <span className="font-semibold text-blue-600">Value: {action.expected_incremental_value_paise}p</span>
                          <span className={`font-semibold ${action.status === 'SELECTED' ? 'text-emerald-600' : action.status === 'POLICY_REJECTED' ? 'text-rose-600' : 'text-slate-600'}`}>{action.status}</span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleExecute(action.action)}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm font-medium flex items-center transition-colors"
                      >
                        Execute
                        <ArrowRight className="w-4 h-4 ml-2" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-slate-900 text-white p-5 rounded-lg">
                <h4 className="text-sm font-semibold text-slate-300 mb-2">Final Decision Logic</h4>
                <div className="font-medium mb-1 text-slate-300">Governor: {decision.governor_status}</div>
                <div className="text-sm text-rose-400 mb-2">{decision.rejection_reason}</div>
                <p className="text-sm text-slate-400">{decision.explanation}</p>
              </div>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-slate-400 flex-col">
              <Target className="w-12 h-12 mb-4 opacity-20" />
              <p>Select a case to view decision logic</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
