import React, { useState, useEffect } from 'react';
import axios from 'axios';
import RiskGauge from './RiskGauge';
import TrendChart from './TrendChart';
import AlertPanel from './AlertPanel';
import {
  ShieldAlert,
  ShieldCheck,
  CheckCircle2,
  Calendar,
  Layers,
  Sparkles,
} from 'lucide-react';

export default function RiskDashboardView({ lastMessage }) {
  const [timeframe, setTimeframe] = useState('30d');
  const [riskData, setRiskData] = useState({
    account_health_score: 85.0,
    current_dispute_ratio: 0.88,
    risk_band: 'GREEN',
    transactions_90d: 2500,
  });
  const [summaryData, setSummaryData] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [riskRes, sumRes] = await Promise.allSettled([
          axios.get('/api/analytics/risk-score'),
          axios.get('/api/analytics/summary'),
        ]);
        if (riskRes.status === 'fulfilled' && riskRes.value?.data) {
          setRiskData(riskRes.value.data);
        }
        if (sumRes.status === 'fulfilled' && sumRes.value?.data) {
          setSummaryData(sumRes.value.data);
        }
      } catch (err) {
        // fallback
      }
    }
    loadData();
  }, [lastMessage]);

  const ratio = Number(riskData.current_dispute_ratio) || 0.88;
  const buffer = Math.max(0, 1.5 - ratio).toFixed(2);
  const totalClaims = summaryData?.total ?? 47;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* 1. Subheader with Timeframe Pills */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-1 border-b border-slate-200 gap-3">
        <div className="flex items-center space-x-2">
          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-blue-50 text-[#0079C1] border border-blue-200">
            PAYPAL API V2 SYNC
          </span>
          <span className="text-xs text-slate-500 font-medium">
            Continuous threshold telemetry &amp; predictive account limitation prevention
          </span>
        </div>

        {/* Timeframe Filter Buttons */}
        <div className="flex items-center space-x-1 p-1 bg-slate-100 rounded-lg border border-slate-200 self-start sm:self-auto text-xs">
          {[
            { id: '7d', label: 'Last 7 Days' },
            { id: '30d', label: 'Last 30 Days (Active)' },
            { id: '90d', label: 'Last 90 Days' },
            { id: 'custom', label: 'Custom' },
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setTimeframe(t.id)}
              className={`px-3 py-1 rounded-md font-semibold transition-all ${
                timeframe === t.id
                  ? 'bg-white text-[#00457C] shadow-xs'
                  : 'text-slate-500 hover:text-slate-900'
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      {/* 2. Top 4 Risk & Velocity KPI Ribbon */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Current Dispute Ratio */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              Current Dispute Ratio
            </span>
            <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-blue-50 text-[#0079C1] border border-blue-200">
              Safe Harbor
            </span>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-slate-900 font-mono tracking-tight">
            {ratio.toFixed(2)}%
          </div>
          <div className="mt-1 text-[11px] text-slate-500 font-medium">
            Target &lt; 1.00% (PayPal Limit: 1.50%)
          </div>
        </div>

        {/* Card 2: Rolling Reserve Risk */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              Rolling Reserve Risk
            </span>
            <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
              0% Required
            </span>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-slate-900 font-mono tracking-tight">
            Zero Hold
          </div>
          <div className="mt-1 text-[11px] text-slate-500 font-medium">
            Next Reserve Evaluation: 18d
          </div>
        </div>

        {/* Card 3: PayPal Standing */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              PayPal Standing
            </span>
            <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-blue-50 text-[#00457C] border border-blue-200">
              Verified T1
            </span>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-[#00457C] font-mono tracking-tight flex items-center gap-1.5">
            <span>Normal Standing</span>
            <CheckCircle2 className="w-5 h-5 text-paypal-marine" />
          </div>
          <div className="mt-1 text-[11px] text-slate-500 font-medium">
            No account flags recorded
          </div>
        </div>

        {/* Card 4: Safe Intake Capacity */}
        <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-xs">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              Safe Intake Capacity
            </span>
            <span className="p-1 rounded bg-blue-50 text-[#0079C1]">
              <ShieldCheck className="w-3.5 h-3.5" />
            </span>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-slate-900 font-mono tracking-tight">
            +28 Claims
          </div>
          <div className="mt-1 text-[11px] text-slate-500 font-medium">
            {buffer}% cushion before freeze ($1.4M GMV)
          </div>
        </div>
      </div>

      {/* 3. Middle Row: Account Health Speedometer Gauge + 30-Day Trajectory Area Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <RiskGauge className="lg:col-span-1" riskData={riskData} />
        <TrendChart className="lg:col-span-2" />
      </div>

      {/* 4. Bottom Row: Dispute Reason Breakdown + Predictive Risk Guardrails */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Dispute Reason Breakdown Card */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h3 className="text-sm font-bold text-slate-900 tracking-tight">
                Dispute Reason Breakdown
              </h3>
              <p className="text-[11px] text-slate-500 font-medium">
                Active {totalClaims} total disputes across primary categories
              </p>
            </div>
            <span className="text-[10px] font-mono text-slate-400 bg-slate-50 border border-slate-200 px-2 py-0.5 rounded">
              Aggregated 90d
            </span>
          </div>

          {/* Breakdown Bars */}
          <div className="space-y-4 text-xs">
            {/* INR Category */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <span className="font-bold text-slate-800 flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-sm bg-[#0079C1]" />
                  <span>INR (Item Not Received)</span>
                </span>
                <span className="font-mono text-slate-600 font-semibold">54% (25 claims)</span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div className="bg-[#0079C1] h-full rounded-full" style={{ width: '54%' }} />
              </div>
              <div className="flex justify-between text-[11px] text-slate-500">
                <span className="text-emerald-700 font-semibold">Win Rate: 91.2%</span>
                <span>Avg Res: 18h (Auto-Carrier)</span>
              </div>
            </div>

            {/* SNAD Category */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <span className="font-bold text-slate-800 flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-sm bg-[#00457C]" />
                  <span>SNAD (Not As Described)</span>
                </span>
                <span className="font-mono text-slate-600 font-semibold">32% (15 claims)</span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div className="bg-[#00457C] h-full rounded-full" style={{ width: '32%' }} />
              </div>
              <div className="flex justify-between text-[11px] text-slate-500">
                <span className="text-emerald-700 font-semibold">Win Rate: 73.5%</span>
                <span>Avg Res: 34h (RAG Match)</span>
              </div>
            </div>

            {/* Unauthorized Category */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <span className="font-bold text-slate-800 flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-sm bg-rose-500" />
                  <span>Unauthorized Transaction</span>
                </span>
                <span className="font-mono text-slate-600 font-semibold">14% (7 claims)</span>
              </div>
              <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                <div className="bg-rose-500 h-full rounded-full" style={{ width: '14%' }} />
              </div>
              <div className="flex justify-between text-[11px] text-slate-500">
                <span className="text-emerald-700 font-semibold">Win Rate: 85.7%</span>
                <span>Avg Res: 12h (IP/Device Match)</span>
              </div>
            </div>
          </div>

          {/* Footer Metric */}
          <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
            <span className="text-slate-500 font-medium">Blended Merchant Defense Win Rate</span>
            <span className="font-mono font-bold text-emerald-700 text-sm">84.8% Won</span>
          </div>
        </div>

        {/* Predictive AI Guardrails Component */}
        <AlertPanel />
      </div>
    </div>
  );
}

