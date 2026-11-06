import React from 'react';
import AgentLog from './AgentLog';
import {
  Clock,
  Sparkles,
  Zap,
  Code2,
  Bot,
  Activity,
  Layers,
  CheckCircle2,
} from 'lucide-react';

export default function AgentStreamView({ lastMessage }) {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* 1. Top Operational Telemetry Ribbon (Stitch Geometry) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1: Avg Response Time */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:border-[#0079C1] transition-all">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              Avg Response Time
            </span>
            <div className="p-1.5 rounded-lg bg-blue-50 text-[#0079C1]">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-slate-900 font-mono tracking-tight flex items-baseline gap-1.5">
            <span>4.2</span>
            <span className="text-xs font-semibold text-slate-500">minutes</span>
          </div>
          <div className="mt-2 pt-2 border-t border-slate-100 text-[11px] text-slate-500 font-medium">
            PayPal webhook ingestion to defense submission
          </div>
        </div>

        {/* Metric 2: Precedent Match */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:border-[#0079C1] transition-all">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              Precedent Match
            </span>
            <span className="text-[10px] font-mono font-bold text-[#0079C1] bg-blue-50 px-2 py-0.5 rounded-full border border-blue-200">
              cosine &gt; 0.85
            </span>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-slate-900 font-mono tracking-tight">
            98.4%
          </div>
          <div className="mt-2 pt-2 border-t border-slate-100 text-[11px] text-slate-500 font-medium">
            Elasticsearch vector similarity over settled claims
          </div>
        </div>

        {/* Metric 3: Autonomous Actions */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:border-[#0079C1] transition-all">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              Autonomous Actions
            </span>
            <span className="text-[10px] font-bold uppercase text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
              Zero-Touch
            </span>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-emerald-700 font-mono tracking-tight">
            89.2%
          </div>
          <div className="mt-2 pt-2 border-t border-slate-100 text-[11px] text-slate-500 font-medium">
            Processed end-to-end without merchant friction
          </div>
        </div>

        {/* Metric 4: Daily MCP Tool Invocations */}
        <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-xs hover:border-[#0079C1] transition-all">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">
              Daily Tool Invocations
            </span>
            <div className="p-1.5 rounded-lg bg-blue-50 text-[#0079C1]">
              <Code2 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-slate-900 font-mono tracking-tight flex items-baseline gap-1.5">
            <span>412</span>
            <span className="text-xs font-semibold text-slate-500">calls / 24h</span>
          </div>
          <div className="mt-2 pt-2 border-t border-slate-100 text-[11px] text-slate-500 font-medium">
            100% compliance with PayPal Dispute API v1/v2 schema
          </div>
        </div>
      </div>

      {/* 2. Full Page Agent Stream Container */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-xs min-h-[600px]">
        <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-4">
          <div className="flex items-center space-x-2.5">
            <div className="p-1.5 rounded-lg bg-[#00457C] text-white">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-900 tracking-tight">
                Live Telemetry &amp; Step Execution Chain
              </h2>
              <p className="text-[11px] text-slate-500 font-medium">
                Real-time multi-agent triage loop connected to PayPal Sandbox
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3 text-xs font-medium text-slate-500">
            <span className="flex items-center gap-1.5 text-emerald-700 font-semibold text-[11px]">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              Agent Loop Running
            </span>
            <span className="text-slate-300">|</span>
            <span className="font-mono text-[11px] text-slate-400">4 Worker Threads</span>
            <span className="text-slate-300">|</span>
            <span className="font-mono text-[11px] text-paypal-marine font-bold">(•) WS Connected</span>
          </div>
        </div>

        <AgentLog lastMessage={lastMessage} isFullView={true} />
      </div>
    </div>
  );
}

