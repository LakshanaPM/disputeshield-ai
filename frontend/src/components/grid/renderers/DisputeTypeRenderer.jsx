import React from 'react';
import { Package, FileText, ShieldAlert, HelpCircle } from 'lucide-react';

const REASON_CONFIG = {
  MERCHANDISE_OR_SERVICE_NOT_RECEIVED: {
    label: 'INR (Not Received)',
    shortLabel: 'INR (Item Not Received)',
    color: 'text-amber-800 bg-amber-50 border-amber-200',
    dotColor: 'bg-amber-500',
    icon: Package,
  },
  MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED: {
    label: 'SNAD (Significantly Not as Described)',
    shortLabel: 'SNAD (Not as Described)',
    color: 'text-[#00457C] bg-blue-50 border-blue-200',
    dotColor: 'bg-[#0079C1]',
    icon: FileText,
  },
  UNAUTHORIZED: {
    label: 'Unauthorized Charge',
    shortLabel: 'Unauthorized Transaction',
    color: 'text-rose-800 bg-rose-50 border-rose-200',
    dotColor: 'bg-rose-500',
    icon: ShieldAlert,
  },
};

export default function DisputeTypeRenderer(props) {
  const reason = props.value || '';
  const config = REASON_CONFIG[reason] || {
    label: reason || 'Other',
    shortLabel: reason ? reason.replace(/_/g, ' ') : 'Other',
    color: 'text-slate-800 bg-slate-100 border-slate-200',
    dotColor: 'bg-slate-400',
    icon: HelpCircle,
  };

  const Icon = config.icon;

  return (
    <div className="flex items-center h-full">
      <span
        className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-xs font-semibold tracking-tight ${config.color}`}
        title={config.label}
      >
        <span className={`w-1.5 h-1.5 rounded-full ${config.dotColor}`} />
        <span className="truncate">{config.shortLabel}</span>
      </span>
    </div>
  );
}
