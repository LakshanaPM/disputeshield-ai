import React from 'react';
import {
  ChevronRight,
  ChevronLeft,
  Bot,
  Sparkles,
  X,
} from 'lucide-react';
import AgentLog from '../agent/AgentLog';

export default function Sidebar({
  isExpanded = false,
  onToggle,
  lastMessage,
}) {
  return (
    <>
      {/* Backdrop overlay when drawer is open */}
      {isExpanded && (
        <div
          onClick={onToggle}
          className="fixed inset-0 bg-slate-900/30 backdrop-blur-xs z-40 transition-opacity"
          aria-hidden="true"
        />
      )}

      {/* Slide-over Drawer Panel */}
      <aside
        role="complementary"
        aria-label="Autonomous AI Agent Telemetry Drawer"
        className={`fixed inset-y-0 right-0 z-50 bg-white border-l border-slate-200 shadow-2xl flex flex-col transition-all duration-300 ease-in-out font-sans ${
          isExpanded
            ? 'w-full sm:w-[420px] translate-x-0'
            : 'w-0 translate-x-full overflow-hidden pointer-events-none'
        }`}
      >
        {isExpanded && (
          <div className="flex flex-col h-full overflow-hidden">
            {/* Drawer Header */}
            <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <div className="flex items-center space-x-2.5">
                <div className="p-1.5 rounded-lg bg-[#00457C] text-white shadow-xs">
                  <Bot className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-slate-900 flex items-center space-x-1.5">
                    <span>AI Agent Stream</span>
                    <Sparkles className="w-3.5 h-3.5 text-[#0079C1]" />
                  </h3>
                  <p className="text-[11px] text-slate-500 font-medium">
                    Live telemetry &amp; webhook reasoning
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-1">
                <span className="px-2 py-0.5 rounded-full text-[10px] font-mono font-bold bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  Active
                </span>
                <button
                  onClick={onToggle}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200 transition-colors"
                  aria-label="Close Drawer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Stream Body */}
            <div className="flex-1 overflow-hidden p-4">
              <AgentLog lastMessage={lastMessage} isFullView={false} />
            </div>

            {/* Drawer Footer */}
            <div className="p-3 border-t border-slate-200 bg-slate-50 flex items-center justify-between text-xs text-slate-500 font-medium">
              <span className="text-[11px] flex items-center gap-1.5 text-slate-600">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Connected to PayPal Event Bus
              </span>
              <span className="text-[10px] font-mono text-[#0079C1] font-bold">
                DisputeShield v1.0
              </span>
            </div>
          </div>
        )}
      </aside>
    </>
  );
}
