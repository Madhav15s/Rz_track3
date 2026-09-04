import React from 'react';

interface StatCardProps {
  id?: string;
  title: string;
  value: string | number;
  subtext?: string;
  trend?: {
    value: string;
    isPositive?: boolean;
    neutral?: boolean;
  };
  icon?: React.ReactNode;
  highlight?: boolean;
  tag?: string;
}

export function StatCard({ id, title, value, subtext, trend, icon, highlight, tag }: StatCardProps) {
  return (
    <div
      id={id}
      className={`rounded-xl p-5 border transition-all ${
        highlight
          ? 'bg-gradient-to-br from-slate-900 to-slate-800 text-white border-slate-700 shadow-md'
          : 'bg-white text-slate-900 border-slate-200/80 shadow-xs hover:border-slate-300'
      }`}
    >
      <div className="flex items-center justify-between gap-2 mb-3">
        <span className={`text-xs font-semibold tracking-wider uppercase ${highlight ? 'text-slate-400' : 'text-slate-500'}`}>
          {title}
        </span>
        {icon && (
          <div className={`p-2 rounded-lg ${highlight ? 'bg-slate-800 text-blue-400' : 'bg-slate-50 text-slate-600 border border-slate-100'}`}>
            {icon}
          </div>
        )}
      </div>

      <div className="flex items-baseline gap-2 mb-1">
        <span className={`text-2xl font-bold tracking-tight ${highlight ? 'text-white' : 'text-slate-900'}`}>
          {value}
        </span>
        {tag && (
          <span className={`text-[11px] px-2 py-0.5 rounded font-medium ${
            highlight ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-blue-50 text-blue-700 border border-blue-200'
          }`}>
            {tag}
          </span>
        )}
      </div>

      {(subtext || trend) && (
        <div className="flex items-center gap-2 mt-2">
          {trend && (
            <span
              className={`text-xs font-medium ${
                trend.neutral
                  ? highlight ? 'text-slate-400' : 'text-slate-500'
                  : trend.isPositive
                  ? highlight ? 'text-emerald-400' : 'text-emerald-600'
                  : highlight ? 'text-rose-400' : 'text-rose-600'
              }`}
            >
              {trend.value}
            </span>
          )}
          {subtext && (
            <span className={`text-xs ${highlight ? 'text-slate-400' : 'text-slate-500'}`}>
              {subtext}
            </span>
          )}
        </div>
      )}
    </div>
  );
}
