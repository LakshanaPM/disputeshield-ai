import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Activity,
  Bell,
  CheckCircle2,
  ChevronDown,
  Sparkles,
  Zap,
  Loader2,
  Menu,
  SlidersHorizontal,
  Bot,
  Layers,
  TrendingUp,
} from 'lucide-react';
import logoImg from '../../assets/logo.png';
import shieldImg from '../../assets/shield.png';
import { useToast } from '../common/Toast';

export default function TopNav({
  currentView = 'queue',
  onSelectView,
  isWsConnected = true,
  lastMessage = null,
  onToggleSidebar,
  isSidebarExpanded = false,
}) {
  const [riskData, setRiskData] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const toastContext = useToast();

  // Load initial notifications from real disputes
  useEffect(() => {
    async function loadNotifications() {
      try {
        const res = await axios.get('/api/disputes', {
          params: { start_row: 0, end_row: 4, sort_col: 'created_at', sort_dir: 'desc' },
        });
        const rows = res.data?.rows || [];
        const notifs = rows.map((d) => ({
          id: d.paypal_dispute_id,
          title: `Dispute ${d.paypal_dispute_id}`,
          reason: d.reason?.replace(/_/g, ' ') || 'Dispute Ingested',
          status: d.agent_decision || d.status || 'UNDER_REVIEW',
          amount: Number(d.dispute_amount || 0).toFixed(2),
          currency: d.dispute_currency || 'USD',
          time: 'Active',
        }));
        setNotifications(notifs);
      } catch (e) {
        // Fallback gracefully
      }
    }
    loadNotifications();
  }, []);

  // Prepend live WebSocket events to activity feed
  useEffect(() => {
    if (!lastMessage) return;
    if (['new_dispute', 'agent_decision', 'evidence_submitted'].includes(lastMessage.type)) {
      const isAuto = lastMessage.decision === 'AUTO_SUBMITTED' || lastMessage.type === 'evidence_submitted';
      const newNotif = {
        id: lastMessage.dispute_id || `PP-D-${Date.now().toString().slice(-4)}`,
        title: `Dispute ${lastMessage.dispute_id || 'Alert'}`,
        reason: isAuto
          ? 'Rebuttal dispatched to PayPal Resolution API'
          : (lastMessage.reason?.replace(/_/g, ' ') || 'Incoming Dispute Ingested'),
        status: lastMessage.decision || (isAuto ? 'AUTO_SUBMITTED' : 'UNDER_REVIEW'),
        amount: lastMessage.amount ? Number(lastMessage.amount).toFixed(2) : undefined,
        currency: lastMessage.currency || 'USD',
        time: 'Just now',
      };
      setNotifications((prev) => [newNotif, ...prev.filter((n) => n.id !== newNotif.id).slice(0, 4)]);
    }
  }, [lastMessage]);

  useEffect(() => {
    async function fetchRiskScore() {
      try {
        const res = await axios.get('/api/analytics/risk-score');
        setRiskData(res.data);
      } catch (err) {
        // Fallback demo data if backend is starting
        setRiskData({
          account_health_score: 85.0,
          current_dispute_ratio: 0.88,
          risk_band: 'GREEN',
          disputes_90d: 22,
          transactions_90d: 2500,
        });
      }
    }
    fetchRiskScore();
  }, []);

  const handleSimulateWebhook = async () => {
    try {
      setIsSimulating(true);
      const res = await axios.post('/api/webhooks/paypal/simulate', {});
      const desc = res.data?.description || `Scenario: ${res.data?.scenario || 'Dispute'}`;
      toastContext?.toast?.info(
        'Webhook Ingested',
        `Dispute ${res.data?.dispute_id || 'PP-D-SIM'} ingested. ${desc}`
      );
    } catch (err) {
      toastContext?.toast?.error('Simulation Failed', err.response?.data?.detail || err.message);
    } finally {
      setIsSimulating(false);
    }
  };

  const riskBand = riskData?.risk_band || 'GREEN';
  const healthScore = riskData?.account_health_score ? Number(riskData.account_health_score).toFixed(0) : '85';
  const disputeRatio = riskData?.current_dispute_ratio ? Number(riskData.current_dispute_ratio).toFixed(2) : '0.88';

  const navTabs = [
    { id: 'queue', label: 'Dispute Queue', icon: Layers },
    { id: 'analytics', label: 'Risk & Limitation Analytics', icon: TrendingUp },
    { id: 'agent', label: 'Autonomous Agent Stream', icon: Bot },
  ];

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-xs">
      {/* Primary Brand & Metric Bar */}
      <div className="h-16 sm:h-[72px] px-4 sm:px-6 flex items-center justify-between border-b border-slate-100">
        {/* Left: Brand Identity & Subtitle */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 py-1">
            {/* Full Logo: Shield + Text for screens sm and up */}
            <img
              src={logoImg}
              alt="DisputeShield AI"
              className="h-10 sm:h-11 md:h-12 w-auto max-h-[50px] object-contain cursor-pointer transition-transform hover:scale-[1.02] hidden sm:block"
              onClick={() => onSelectView && onSelectView('queue')}
            />
            {/* Shield Only Logo for mobile / compact views */}
            <img
              src={shieldImg}
              alt="DisputeShield AI"
              className="h-9 w-9 object-contain cursor-pointer transition-transform hover:scale-[1.05] block sm:hidden"
              onClick={() => onSelectView && onSelectView('queue')}
            />
          </div>
          <span className="hidden xl:inline-block text-[11px] text-slate-400 font-medium border-l border-slate-200 pl-3">
            Autonomous PayPal Defense
          </span>
        </div>

        {/* Center: Live Telemetry Badges */}
        <div className="hidden lg:flex items-center space-x-3">
          {/* Live Agent Stream Status Indicator */}
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-50 border border-slate-200 shadow-inner">
            <span className="relative flex h-2 w-2">
              {isWsConnected && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-500 opacity-75" />
              )}
              <span
                className={`relative inline-flex rounded-full h-2 w-2 ${
                  isWsConnected ? 'bg-emerald-500' : 'bg-slate-400'
                }`}
              />
            </span>
            <span className="text-[11px] font-bold text-slate-700 uppercase tracking-wider">
              {isWsConnected ? 'Agent Live' : 'Standby'}
            </span>
          </div>

          {/* Account Health & Ratio Badge */}
          <div className="flex items-center space-x-3 px-3 py-1 rounded-full bg-slate-50 border border-slate-200 shadow-inner">
            <div className="flex items-center space-x-1.5">
              <span className="text-[11px] text-slate-500 font-medium">Health Score:</span>
              <span className="text-xs font-bold text-slate-900 font-mono">{healthScore}/100</span>
            </div>
            <div className="h-3 w-px bg-slate-200" />
            <div className="flex items-center space-x-1.5">
              <span className="text-xs font-bold text-slate-900 font-mono">{disputeRatio}%</span>
              <span className="text-[11px] text-slate-500 font-medium">Dispute Ratio</span>
            </div>
            <div className="h-3 w-px bg-slate-200" />
            <span className="px-2 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wide bg-blue-50 text-paypal-marine border border-blue-200">
              {riskBand === 'GREEN' ? 'SAFE HARBOR' : riskBand}
            </span>
          </div>
        </div>

        {/* Right Actions: Simulate Webhook, Notifications, Merchant, Drawer Toggle */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Simulate Webhook Button */}
          <button
            onClick={handleSimulateWebhook}
            disabled={isSimulating}
            className="px-3.5 py-1.5 rounded-lg bg-[#0079C1] hover:bg-[#00457C] text-white font-semibold text-xs transition-colors flex items-center gap-1.5 shadow-sm disabled:opacity-50 focus-ring"
            aria-label="Simulate PayPal Webhook"
          >
            {isSimulating ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Zap className="w-3.5 h-3.5 fill-current" />
            )}
            <span className="hidden sm:inline font-bold">Simulate Webhook</span>
          </button>

          {/* Notification Center */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 rounded-lg bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-600 hover:text-slate-900 transition-colors relative focus-ring"
              aria-label="Notifications"
            >
              <Bell className="w-4 h-4" />
              {notifications.length > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-[#0079C1] ring-2 ring-white" />
              )}
            </button>

            {showNotifications && (
              <div className="absolute right-0 mt-2 w-84 bg-white rounded-xl shadow-xl p-3.5 z-50 animate-fade-in border border-slate-200 text-xs">
                <div className="font-bold text-slate-900 pb-2.5 border-b border-slate-100 flex justify-between items-center">
                  <span>Autonomous Activity Feed</span>
                  <span className="text-[10px] text-slate-500 font-medium">
                    {notifications.length} recent
                  </span>
                </div>
                <div className="py-2 space-y-2 max-h-72 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="py-6 text-center text-slate-400 text-xs">
                      No recent notifications
                    </div>
                  ) : (
                    notifications.map((n) => (
                      <div
                        key={n.id}
                        className="p-2.5 rounded-lg bg-slate-50 hover:bg-slate-100/80 border border-slate-100 transition-colors"
                      >
                        <div className="flex items-center justify-between gap-2">
                          <p className="font-bold text-slate-800 text-[11px] truncate">{n.title}</p>
                          <span
                            className={`px-1.5 py-0.5 rounded text-[9px] font-bold uppercase shrink-0 ${
                              n.status === 'AUTO_SUBMITTED'
                                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                : n.status === 'DRAFT_PENDING_REVIEW' || n.status === 'PENDING'
                                ? 'bg-amber-50 text-amber-700 border border-amber-200'
                                : 'bg-blue-50 text-[#0079C1] border border-blue-200'
                            }`}
                          >
                            {n.status === 'AUTO_SUBMITTED'
                              ? 'Auto-Submitted'
                              : n.status === 'DRAFT_PENDING_REVIEW'
                              ? 'Pending Review'
                              : n.status}
                          </span>
                        </div>
                        <p className="text-slate-600 text-[11px] mt-0.5 line-clamp-1">{n.reason}</p>
                        <div className="flex items-center justify-between text-[10px] text-slate-400 mt-1 pt-1 border-t border-slate-200/50">
                          <span>{n.amount ? `$${n.amount} ${n.currency}` : 'PayPal Claim'}</span>
                          <span>{n.time}</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Merchant Profile Pill */}
          <div className="flex items-center space-x-2.5 px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 hidden sm:flex">
            <div className="w-7 h-7 rounded-full bg-[#00457C] text-white flex items-center justify-center font-bold text-xs">
              EM
            </div>
            <div className="text-left">
              <div className="text-xs font-bold text-slate-800 leading-tight flex items-center gap-1">
                <span>EliteMerchant LLC</span>
                <CheckCircle2 className="w-3 h-3 text-paypal-marine" />
              </div>
              <div className="text-[10px] text-slate-400 font-medium">Business Verified</div>
            </div>
          </div>
          {/* Slide-over Agent Stream Trigger */}
          <button
            onClick={onToggleSidebar}
            aria-label="Toggle AI Stream Drawer"
            className={`p-2 rounded-lg border transition-colors focus-ring flex items-center gap-1 text-xs font-semibold ${
              isSidebarExpanded
                ? 'bg-blue-50 border-blue-200 text-paypal-marine'
                : 'bg-slate-100 hover:bg-slate-200 border-slate-200 text-slate-600'
            }`}
          >
            <Bot className="w-4 h-4" />
            <span className="hidden md:inline">AI Stream</span>
          </button>
        </div>
      </div>

      {/* Secondary View Switcher Tabs Bar (Stitch Layout Navigation) */}
      <div className="px-4 sm:px-6 flex items-center space-x-4 sm:space-x-6 h-11 bg-white text-xs border-t border-slate-100">
        <div className="flex items-center gap-2 pr-3 border-r border-slate-200 h-6">
          <img
            src={shieldImg}
            alt="DisputeShield Emblem"
            className="w-4 h-4 object-contain"
          />
          <span className="font-extrabold text-slate-800 text-[11px] tracking-tight hidden md:inline">
            Active Shield
          </span>
        </div>
        {navTabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = currentView === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => onSelectView && onSelectView(tab.id)}
              className={`h-full flex items-center space-x-2 font-bold transition-all relative border-b-2 focus-ring ${
                isActive
                  ? 'border-[#0079C1] text-[#00457C]'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-[#0079C1]' : 'text-slate-400'}`} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
}
