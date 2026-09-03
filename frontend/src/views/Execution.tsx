
import { Zap, PlayCircle, CheckCircle, RefreshCw, Server } from 'lucide-react';

export default function Execution() {
  return (
    <div className="p-8 max-w-5xl">
      <h2 className="text-2xl font-bold text-slate-800 mb-6 flex items-center">
        <Zap className="mr-2 text-blue-500" /> Execution Gateway
      </h2>

      <div className="flex space-x-4 mb-8">
        <div className="flex-1 bg-gradient-to-r from-blue-900 to-slate-900 rounded-lg p-6 text-white shadow-lg">
          <div className="flex justify-between items-start mb-4">
            <h3 className="font-semibold text-blue-200">Execution Mode</h3>
            <span className="bg-blue-800 text-xs px-2 py-1 rounded font-mono border border-blue-600">TEST_MODE</span>
          </div>
          <div className="flex items-center space-x-2 text-sm text-slate-300">
            <Server className="w-4 h-4" />
            <span>Connected to Razorpay Sandbox</span>
          </div>
        </div>
        
        <div className="flex-1 bg-white border border-slate-200 rounded-lg p-6 shadow-sm">
           <h3 className="font-semibold text-slate-700 mb-2">Simulated vs Real</h3>
           <p className="text-sm text-slate-500">
             Actions routed to Razorpay Test Mode execute real API calls against the sandbox. Actions flagged as 'Simulated' are purely internal logical states.
           </p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <h3 className="text-lg font-bold mb-6">Action Lifecycle</h3>
        
        <div className="flex items-center justify-between max-w-3xl mx-auto py-8">
          <div className="flex flex-col items-center text-slate-400">
            <div className="w-12 h-12 rounded-full border-2 border-slate-300 flex items-center justify-center mb-2">
              <RefreshCw className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold uppercase">Proposed</span>
          </div>
          
          <div className="flex-1 h-0.5 bg-slate-200 mx-4"></div>
          
          <div className="flex flex-col items-center text-blue-500">
            <div className="w-12 h-12 rounded-full border-2 border-blue-500 bg-blue-50 flex items-center justify-center mb-2">
              <PlayCircle className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold uppercase">Approved</span>
          </div>
          
          <div className="flex-1 h-0.5 bg-slate-200 mx-4"></div>
          
          <div className="flex flex-col items-center text-amber-500">
            <div className="w-12 h-12 rounded-full border-2 border-amber-500 bg-amber-50 flex items-center justify-center mb-2">
              <RefreshCw className="w-5 h-5 animate-spin" />
            </div>
            <span className="text-xs font-bold uppercase">Pending</span>
          </div>
          
          <div className="flex-1 h-0.5 bg-slate-200 mx-4"></div>
          
          <div className="flex flex-col items-center text-emerald-500">
            <div className="w-12 h-12 rounded-full border-2 border-emerald-500 bg-emerald-50 flex items-center justify-center mb-2">
              <CheckCircle className="w-5 h-5" />
            </div>
            <span className="text-xs font-bold uppercase">Verified</span>
          </div>
        </div>
      </div>
    </div>
  );
}
