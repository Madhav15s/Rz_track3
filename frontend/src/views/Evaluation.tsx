import { useState, useEffect } from 'react';

import api from '../api';
import { FileText } from 'lucide-react';

export default function Evaluation() {
  const [content, setContent] = useState<string>('');

  useEffect(() => {
    api.get('/evaluation').then(res => setContent(res.data.report || JSON.stringify(res.data, null, 2))).catch(e => {
        console.error(e);
        setContent('Error loading evaluation report.');
    });
  }, []);

  return (
    <div className="p-8 h-full flex flex-col">
      <h2 className="text-2xl font-bold text-slate-800 mb-6 flex items-center">
        <FileText className="mr-2 text-slate-700" /> Evaluation Report
      </h2>

      <div className="bg-white rounded-lg shadow-sm border border-slate-200 flex-1 p-6 overflow-y-auto">
        <div className="prose prose-slate max-w-none prose-h2:border-b prose-h2:pb-2">
          {/* Simple plain text rendering for markdown to avoid installing extra dependencies, 
              or rendering as preformatted text if it's raw text */}
          <pre className="whitespace-pre-wrap font-sans text-sm text-slate-700">
            {content || 'Loading report...'}
          </pre>
        </div>
      </div>
    </div>
  );
}
