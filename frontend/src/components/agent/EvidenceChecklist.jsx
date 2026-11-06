import React from 'react';
import { CheckCircle2, Clock, AlertTriangle, Shield, AlertCircle } from 'lucide-react';

const DEFAULT_ITEMS = [
  {
    name: 'Proof of Delivery',
    evidence_type: 'CARRIER_TRACKING',
    status: 'AVAILABLE',
    score: 95,
    details: 'UPS 1Z9999999999999999 — Delivered to buyer postal code with timestamp',
  },
  {
    name: 'Customer Invoice & Order Match',
    evidence_type: 'ORDER_INVOICE',
    status: 'AVAILABLE',
    score: 90,
    details: 'Matched billing address and item description in transaction telemetry',
  },
  {
    name: 'RAG Precedent Case Match',
    evidence_type: 'HISTORICAL_PRECEDENT',
    status: 'AVAILABLE',
    score: 85,
    details: '5 matching INR cases in Elasticsearch with 78% empirical win rate',
  },
  {
    name: 'Signature Confirmation',
    evidence_type: 'SIGNATURE_RECEIPT',
    status: 'INCOMPLETE',
    score: 50,
    details: 'Optional carrier signature not requested by buyer (order < $750)',
  },
];

export default function EvidenceChecklist({
  items = DEFAULT_ITEMS,
  overallScore = 88,
  identifiedGaps = [],
  className = '',
}) {
  const displayItems = items && items.length > 0 ? items : DEFAULT_ITEMS;

  const getStatusConfig = (status) => {
    switch (status) {
      case 'AVAILABLE':
        return {
          icon: CheckCircle2,
          color: 'text-emerald-400',
          bg: 'bg-emerald-500/10 border-emerald-500/20',
          label: 'Available',
        };
      case 'INCOMPLETE':
        return {
          icon: Clock,
          color: 'text-amber-400',
          bg: 'bg-amber-500/10 border-amber-500/20',
          label: 'Incomplete',
        };
      case 'MISSING':
      default:
        return {
          icon: AlertTriangle,
          color: 'text-rose-400',
          bg: 'bg-rose-500/10 border-rose-500/20',
          label: 'Missing',
        };
    }
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header with Strength Progress Bar */}
      <div>
        <div className="flex items-center justify-between mb-1.5">
          <span className="text-xs font-semibold text-slate-200 flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5 text-paypal-cyan" />
            Evidence Strength Score
          </span>
          <span className="text-xs font-bold font-mono text-emerald-400">
            {overallScore}%
          </span>
        </div>
        <div className="w-full bg-white/10 h-2 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-paypal-blue via-paypal-cyan to-emerald-400 transition-all duration-700"
            style={{ width: `${Math.min(100, Math.max(0, overallScore))}%` }}
          />
        </div>
      </div>

      {/* Checklist Items */}
      <div className="space-y-2">
        {displayItems.map((item, idx) => {
          const config = getStatusConfig(item.status);
          const Icon = config.icon;
          return (
            <div
              key={idx}
              className="p-2.5 rounded-xl bg-white/5 border border-white/5 hover:border-white/15 transition-all text-xs"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start gap-2">
                  <Icon className={`w-4 h-4 mt-0.5 flex-shrink-0 ${config.color}`} />
                  <div>
                    <h5 className="font-semibold text-slate-200">{item.name}</h5>
                    <p className="text-[11px] text-slate-400 mt-0.5 leading-relaxed">
                      {item.details}
                    </p>
                  </div>
                </div>

                <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-medium border flex-shrink-0 ${config.bg} ${config.color}`}>
                  {config.label}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Defense Gaps Section */}
      {identifiedGaps && identifiedGaps.length > 0 && (
        <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-xs">
          <div className="flex items-center gap-1.5 text-rose-400 font-semibold mb-1.5">
            <AlertCircle className="w-3.5 h-3.5" />
            <span>Identified Defense Gaps</span>
          </div>
          <ul className="space-y-1 list-disc list-inside text-[11px] text-slate-300">
            {identifiedGaps.map((gap, idx) => (
              <li key={idx}>{gap}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
