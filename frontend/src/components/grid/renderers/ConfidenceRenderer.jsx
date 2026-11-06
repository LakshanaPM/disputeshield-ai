import React from 'react';
import { Zap, AlertCircle, AlertTriangle } from 'lucide-react';

export default function ConfidenceRenderer(props) {
  const rawValue = props.value;
  if (rawValue === null || rawValue === undefined) {
    return <span className="text-slate-400 text-xs italic">N/A</span>;
  }

  // Support both 0.0-1.0 scale and 0-100 scale
  const percentage = rawValue <= 1.0 ? Math.round(rawValue * 100) : Math.round(rawValue);

  return (
    <div className="flex items-center space-x-2.5 h-full">
      <div className="w-16 bg-slate-200 h-1.5 rounded-full overflow-hidden hidden sm:block">
        <div
          className="h-full rounded-full transition-all duration-500 bg-[#0079C1]"
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
      <span className="font-mono font-bold text-xs text-slate-800">
        {percentage}%
      </span>
    </div>
  );
}
