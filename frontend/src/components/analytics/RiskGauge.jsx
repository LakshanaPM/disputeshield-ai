import React, { useEffect, useState } from 'react';
import axios from 'axios';
import AnimatedCounter from '../common/AnimatedCounter';
import {
  ShieldAlert,
  ShieldCheck,
  TrendingDown,
  TrendingUp,
  Minus,
  AlertTriangle,
  Layers,
} from 'lucide-react';

export default function RiskGauge({ riskData: propRiskData = null, className = '' }) {
  const [riskData, setRiskData] = useState(
    propRiskData || {
      account_health_score: 85.0,
      current_dispute_ratio: 0.88,
      risk_band: 'GREEN',
      trend_direction: 'STABLE',
      disputes_90d: 22,
      transactions_90d: 2500,
      threshold_warning: null,
    }
  );

  useEffect(() => {
    if (propRiskData) {
      setRiskData(propRiskData);
      return;
    }
    async function fetchRisk() {
      try {
        const res = await axios.get('/api/analytics/risk-score');
        if (res.data) setRiskData(res.data);
      } catch (err) {
        // fallback
      }
    }
    fetchRisk();
  }, [propRiskData]);

  const ratio = Number(riskData.current_dispute_ratio) || 0.88;
  const healthScore = Number(riskData.account_health_score) || 85.0;
  const riskBand = riskData.risk_band || 'GREEN';

  // Gauge angles: max ratio on dial is 2.0% (1.5% is the PayPal limitation ceiling)
  const maxDialRatio = 2.0;
  const clampedRatio = Math.min(Math.max(ratio, 0), maxDialRatio);
  const needleRotation = -180 + (clampedRatio / maxDialRatio) * 180;

  const buffer = Math.max(0, 1.5 - ratio).toFixed(2);

  return (
    <div className={`bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div>
          <h3 className="text-sm font-bold text-slate-900 tracking-tight">Account Health Gauge</h3>
          <p className="text-[11px] text-slate-500 font-medium">Standard Settlement Dispute Ceiling</p>
        </div>
        <span className="p-1.5 rounded-lg bg-blue-50 text-[#0079C1] border border-blue-200">
          <ShieldCheck className="w-4 h-4" />
        </span>
      </div>

      {/* Semicircular Speedometer Dial */}
      <div className="flex flex-col items-center pt-3">
        <div className="relative w-64 h-36 flex items-center justify-center overflow-hidden">
          <svg viewBox="0 0 200 115" className="w-full h-full">
            {/* Background Track */}
            <path
              d="M 20 100 A 80 80 0 0 1 180 100"
              fill="none"
              stroke="#F1F5F9"
              strokeWidth="14"
              strokeLinecap="round"
            />

            {/* Safe Zone (0.0% to 1.0%) */}
            <path
              d="M 20 100 A 80 80 0 0 1 100 20"
              fill="none"
              stroke="#0079C1"
              strokeWidth="12"
              strokeLinecap="round"
            />

            {/* Warning Zone (1.0% to 1.5%) */}
            <path
              d="M 100 20 A 80 80 0 0 1 156.6 43.4"
              fill="none"
              stroke="#F59E0B"
              strokeWidth="12"
            />

            {/* Critical Limitation Halt Zone (>1.5%) */}
            <path
              d="M 156.6 43.4 A 80 80 0 0 1 180 100"
              fill="none"
              stroke="#EF4444"
              strokeWidth="12"
              strokeLinecap="round"
            />

            {/* 1.50% PayPal Ceiling Marker Pin */}
            <line
              x1="100"
              y1="100"
              x2="156.6"
              y2="43.4"
              stroke="#EF4444"
              strokeWidth="1.5"
              strokeDasharray="2 2"
            />

            {/* Needle Pivot & Indicator */}
            <g
              transform={`rotate(${needleRotation} 100 100)`}
              className="transition-transform duration-1000 ease-out"
            >
              <line
                x1="100"
                y1="100"
                x2="35"
                y2="100"
                stroke="#00457C"
                strokeWidth="3.5"
                strokeLinecap="round"
              />
              <circle cx="35" cy="100" r="3.5" fill="#0079C1" />
            </g>

            {/* Center Pivot Hub */}
            <circle cx="100" cy="100" r="7" fill="#00457C" stroke="#0079C1" strokeWidth="2.5" />
          </svg>

          {/* Dial Center Numerical Value */}
          <div className="absolute bottom-1 flex flex-col items-center">
            <div className="text-3xl font-extrabold text-slate-900 font-mono tracking-tight">
              <AnimatedCounter value={ratio} decimals={2} suffix="%" duration={1000} />
            </div>
            <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">
              Dispute Velocity
            </span>
          </div>
        </div>

        {/* Dial Scale Tick Labels */}
        <div className="w-full flex justify-between text-[10px] text-slate-500 font-medium px-4 mt-1 border-b border-slate-100 pb-2">
          <span>0.0%</span>
          <span className="text-paypal-marine font-semibold">1.0% Safe</span>
          <span className="text-rose-600 font-bold">1.5% Halt</span>
          <span>2.0%</span>
        </div>

        {/* Safe Zone Buffer Status Pill */}
        <div className="mt-3 flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-xs font-semibold text-[#00457C]">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>Safe Zone ({buffer}% buffer to PayPal freeze)</span>
        </div>
      </div>

      {/* Absorption Runway Card */}
      <div className="mt-4 p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 space-y-1.5">
        <div className="flex items-center gap-1.5 font-bold text-slate-900">
          <Layers className="w-3.5 h-3.5 text-[#0079C1]" />
          <span>Absorption Runway</span>
        </div>
        <p className="text-[11px] text-slate-600 leading-relaxed">
          At current monthly processing of <span className="font-semibold text-slate-900 font-mono">$1,428,890.00</span>, account can absorb <span className="font-bold text-[#0079C1]">28 additional chargebacks</span> before triggering mandatory rolling reserves.
        </p>
      </div>
    </div>
  );
}
