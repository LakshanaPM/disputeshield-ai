import React from 'react';
import { Zap, Clock, AlertTriangle } from 'lucide-react';

export default function ConfidenceGauge({
  score = 85,
  size = 'md',
  showBreakdown = true,
  breakdown = null,
  className = '',
}) {
  const normalizedScore = Math.max(0, Math.min(100, score <= 1.0 ? Math.round(score * 100) : Math.round(score)));

  const radius = size === 'sm' ? 28 : size === 'lg' ? 48 : 38;
  const strokeWidth = size === 'sm' ? 5 : size === 'lg' ? 8 : 7;
  const viewBoxSize = (radius + strokeWidth) * 2;
  const center = viewBoxSize / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (normalizedScore / 100) * circumference;

  let tier = {
    label: 'AUTO-SUBMIT',
    color: 'text-emerald-400',
    badgeBg: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    gradientId: 'gaugeEmerald',
    startColor: '#10b981',
    endColor: '#00cfde',
    icon: Zap,
    description: 'Score ≥ 80%: Autonomous 1-click submission',
  };

  if (normalizedScore < 60) {
    tier = {
      label: 'ESCALATED',
      color: 'text-rose-400',
      badgeBg: 'bg-rose-500/15 text-rose-400 border-rose-500/30',
      gradientId: 'gaugeRose',
      startColor: '#ef4444',
      endColor: '#f43f5e',
      icon: AlertTriangle,
      description: 'Score < 60%: High risk, full human analysis needed',
    };
  } else if (normalizedScore < 80) {
    tier = {
      label: 'NEEDS REVIEW',
      color: 'text-amber-400',
      badgeBg: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
      gradientId: 'gaugeAmber',
      startColor: '#f59e0b',
      endColor: '#f97316',
      icon: Clock,
      description: 'Score 60-79%: Draft prepared, merchant approval required',
    };
  }

  const TierIcon = tier.icon;

  const metrics = breakdown || {
    evidenceWeight: Math.min(100, Math.round(normalizedScore * 0.95)),
    precedentRate: Math.min(100, Math.round(normalizedScore * 1.02)),
    merchantSafety: Math.min(100, Math.round(normalizedScore * 0.98)),
  };

  return (
    <div className={`flex flex-col items-center ${className}`}>
      {/* Circular Gauge Graphic */}
      <div className="relative flex items-center justify-center">
        <svg
          width={viewBoxSize}
          height={viewBoxSize}
          viewBox={`0 0 ${viewBoxSize} ${viewBoxSize}`}
          className="transform -rotate-90"
        >
          <defs>
            <linearGradient id={tier.gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor={tier.startColor} />
              <stop offset="100%" stopColor={tier.endColor} />
            </linearGradient>
          </defs>

          <circle
            cx={center}
            cy={center}
            r={radius}
            className="text-white/10"
            strokeWidth={strokeWidth}
            stroke="currentColor"
            fill="transparent"
          />

          <circle
            cx={center}
            cy={center}
            r={radius}
            className="transition-all duration-1000 ease-out"
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            stroke={`url(#${tier.gradientId})`}
            fill="transparent"
          />
        </svg>

        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className={`font-mono font-extrabold ${size === 'sm' ? 'text-sm' : size === 'lg' ? 'text-2xl' : 'text-xl'} ${tier.color}`}>
            {normalizedScore}%
          </span>
          {size !== 'sm' && (
            <span className="text-[9px] uppercase tracking-wider text-slate-400 font-semibold mt-0.5">
              Confidence
            </span>
          )}
        </div>
      </div>

      {/* Decision Gate Badge */}
      <div className="mt-2.5">
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-xs font-semibold tracking-wide ${tier.badgeBg}`}
          title={tier.description}
        >
          <TierIcon className="w-3.5 h-3.5" />
          <span>{tier.label}</span>
        </span>
      </div>

      {/* Scoring Weight Breakdown */}
      {showBreakdown && (
        <div className="w-full mt-4 space-y-2 text-xs pt-3 border-t border-white/10">
          <div>
            <div className="flex justify-between text-[11px] mb-1">
              <span className="text-slate-400">Evidence Weight (40%)</span>
              <span className="font-mono text-slate-200 font-semibold">{metrics.evidenceWeight}%</span>
            </div>
            <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-paypal-blue h-full rounded-full transition-all duration-500"
                style={{ width: `${metrics.evidenceWeight}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-[11px] mb-1">
              <span className="text-slate-400">Precedent Win Rate (35%)</span>
              <span className="font-mono text-cyan-400 font-semibold">{metrics.precedentRate}%</span>
            </div>
            <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-paypal-cyan h-full rounded-full transition-all duration-500"
                style={{ width: `${metrics.precedentRate}%` }}
              />
            </div>
          </div>

          <div>
            <div className="flex justify-between text-[11px] mb-1">
              <span className="text-slate-400">Merchant Safety Ratio (25%)</span>
              <span className="font-mono text-emerald-400 font-semibold">{metrics.merchantSafety}%</span>
            </div>
            <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
              <div
                className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                style={{ width: `${metrics.merchantSafety}%` }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
