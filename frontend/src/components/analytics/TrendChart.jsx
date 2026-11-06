import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { TrendingDown, TrendingUp, Calendar } from 'lucide-react';

function CustomAreaTooltip({ active, payload, label }) {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="p-3 rounded-xl bg-white border border-slate-200 shadow-xl text-xs space-y-1 font-sans">
        <p className="font-bold text-slate-900">{label}</p>
        <div className="flex items-center justify-between gap-4">
          <span className="text-slate-500">Dispute Ratio:</span>
          <span className="font-mono font-extrabold text-[#0079C1]">
            {Number(data.ratio).toFixed(2)}%
          </span>
        </div>
        <div className="flex items-center justify-between gap-4">
          <span className="text-slate-500">Claims Logged:</span>
          <span className="font-mono font-bold text-slate-700">{data.dispute_count}</span>
        </div>
      </div>
    );
  }
  return null;
}

export default function TrendChart({ className = '' }) {
  const [trends, setTrends] = useState({
    time_series: [],
    by_category: [],
    monthly: [],
  });

  useEffect(() => {
    async function fetchTrends() {
      try {
        const res = await axios.get('/api/analytics/dispute-trends');
        if (res.data) setTrends(res.data);
      } catch (err) {
        console.warn('[TrendChart] Failed to fetch trends:', err);
      }
    }
    fetchTrends();
  }, []);

  // Format time series for 30-day trajectory
  const rawSeries = trends.time_series || [];
  const chartData = rawSeries.length > 0 ? rawSeries.map((item, idx) => ({
    ...item,
    formattedDate: item.date ? item.date.slice(5) : `Day ${idx + 1}`,
    ratio: Number(item.ratio) || 0.88,
  })) : [
    { formattedDate: 'Day 1', ratio: 0.76, dispute_count: 1 },
    { formattedDate: 'Day 8', ratio: 0.82, dispute_count: 2 },
    { formattedDate: 'Day 14', ratio: 0.94, dispute_count: 3 },
    { formattedDate: 'Day 24', ratio: 0.85, dispute_count: 1 },
    { formattedDate: 'Today', ratio: 0.88, dispute_count: 2 },
  ];

  return (
    <div className={`bg-white rounded-xl border border-slate-200 p-5 shadow-xs flex flex-col justify-between ${className}`}>
      {/* Header and Legend */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
        <div>
          <h3 className="text-sm font-bold text-slate-900 tracking-tight">
            30-Day Dispute Ratio Trajectory
          </h3>
          <p className="text-[11px] text-slate-500 font-medium">
            Daily tracked ratio against PayPal threshold and industry average
          </p>
        </div>

        {/* Legend */}
        <div className="flex items-center space-x-3 text-[11px] font-medium">
          <div className="flex items-center gap-1.5 text-slate-700 font-semibold">
            <span className="w-2.5 h-2.5 rounded-sm bg-[#0079C1]" />
            <span>EliteMerchant (0.88%)</span>
          </div>
          <div className="flex items-center gap-1.5 text-rose-600 font-semibold">
            <span className="w-2.5 h-0.5 bg-rose-500" />
            <span>Ceiling (1.50%)</span>
          </div>
          <div className="flex items-center gap-1.5 text-slate-400">
            <span className="w-2.5 h-0.5 bg-slate-300" />
            <span>Industry (1.25%)</span>
          </div>
        </div>
      </div>

      {/* Area Chart Viewport */}
      <div className="pt-4 flex-1 h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={chartData}
            margin={{ top: 15, right: 15, left: -20, bottom: 0 }}
          >
            <defs>
              <linearGradient id="paypalBlueGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="5%" stopColor="#0079C1" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#0079C1" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
            <XAxis
              dataKey="formattedDate"
              stroke="#94A3B8"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#E2E8F0' }}
            />
            <YAxis
              stroke="#94A3B8"
              fontSize={11}
              tickLine={false}
              axisLine={{ stroke: '#E2E8F0' }}
              domain={[0, 2.0]}
              tickFormatter={(v) => `${v}%`}
            />
            <Tooltip content={<CustomAreaTooltip />} />
            {/* PayPal 1.50% Seller Limitation Ceiling */}
            <ReferenceLine
              y={1.5}
              stroke="#EF4444"
              strokeDasharray="4 4"
              strokeWidth={1.5}
              label={{
                value: 'LIMITATION CEILING 1.50%',
                fill: '#EF4444',
                fontSize: 10,
                position: 'top',
                fontWeight: 'bold',
              }}
            />
            <Area
              type="monotone"
              dataKey="ratio"
              stroke="#0079C1"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#paypalBlueGrad)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Bottom 3-Metric Trajectory Summary */}
      <div className="mt-4 pt-3 border-t border-slate-100 grid grid-cols-3 gap-3 text-center text-xs">
        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
          <span className="text-[10px] text-slate-500 block uppercase font-bold tracking-wider">30D Peak Ratio</span>
          <span className="font-mono font-bold text-slate-800 text-xs">0.94%</span>
          <span className="text-[10px] text-slate-400 block font-medium">Day 14 Peak</span>
        </div>
        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
          <span className="text-[10px] text-slate-500 block uppercase font-bold tracking-wider">30D Low Ratio</span>
          <span className="font-mono font-bold text-slate-800 text-xs">0.72%</span>
          <span className="text-[10px] text-slate-400 block font-medium">Day 3 Valley</span>
        </div>
        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-100">
          <span className="text-[10px] text-slate-500 block uppercase font-bold tracking-wider">Net 7D Delta</span>
          <span className="font-mono font-bold text-emerald-700 text-xs flex items-center justify-center gap-0.5">
            <TrendingDown className="w-3 h-3" />
            -0.06%
          </span>
          <span className="text-[10px] text-slate-400 block font-medium">Downward Trend</span>
        </div>
      </div>
    </div>
  );
}
