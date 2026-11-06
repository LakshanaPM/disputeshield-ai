import React from 'react';
import { ArrowRight, ChevronDown, ChevronUp } from 'lucide-react';

export default function ActionCellRenderer(props) {
  const data = props.data;
  if (!data) return null;

  const decision = data.agent_decision;
  const isExpanded = props.node?.expanded;

  const handleToggleExpand = (e) => {
    e.stopPropagation();
    props.node?.setExpanded(!isExpanded);
  };

  if (decision === 'DRAFT_PENDING_REVIEW') {
    return (
      <div className="flex items-center space-x-1.5 h-full">
        <button
          onClick={handleToggleExpand}
          className="px-3 py-1 rounded-md bg-[#0079C1] hover:bg-[#00457C] text-white text-xs font-bold shadow-xs transition-colors flex items-center gap-1"
          title="Review and sign merchant rebuttal statement"
        >
          <span>Review &amp; Sign</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-2 h-full">
      <button
        onClick={handleToggleExpand}
        className="px-2.5 py-1 rounded-md bg-slate-100 hover:bg-slate-200 border border-slate-300 text-slate-700 text-xs font-semibold transition-colors flex items-center gap-1"
      >
        <span>{isExpanded ? 'Hide' : 'Details'}</span>
        {isExpanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
      </button>
    </div>
  );
}
