import React, { createContext, useContext, useState, useCallback, useMemo, useEffect } from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Info, X } from 'lucide-react';

const TOAST_VARIANTS = {
  success: {
    icon: CheckCircle2,
    border: 'border-emerald-500/40',
    iconColor: 'text-emerald-400',
    barColor: 'bg-emerald-500',
    glow: 'shadow-[0_0_20px_rgba(16,185,129,0.2)]',
  },
  warning: {
    icon: AlertTriangle,
    border: 'border-amber-500/40',
    iconColor: 'text-amber-400',
    barColor: 'bg-amber-500',
    glow: 'shadow-[0_0_20px_rgba(245,158,11,0.2)]',
  },
  error: {
    icon: XCircle,
    border: 'border-rose-500/40',
    iconColor: 'text-rose-400',
    barColor: 'bg-rose-500',
    glow: 'shadow-[0_0_20px_rgba(239,68,68,0.2)]',
  },
  info: {
    icon: Info,
    border: 'border-cyan-500/40',
    iconColor: 'text-paypal-cyan',
    barColor: 'bg-paypal-cyan',
    glow: 'shadow-[0_0_20px_rgba(0,207,222,0.2)]',
  },
};

export function ToastItem({ toast, onDismiss }) {
  const { id, type = 'info', title, message, duration = 5000 } = toast;
  const config = TOAST_VARIANTS[type] || TOAST_VARIANTS.info;
  const Icon = config.icon;
  const [progress, setProgress] = useState(100);

  useEffect(() => {
    const startTime = Date.now();
    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const remaining = Math.max(0, 100 - (elapsed / duration) * 100);
      setProgress(remaining);
      if (remaining <= 0) {
        clearInterval(interval);
        onDismiss(id);
      }
    }, 50);

    return () => clearInterval(interval);
  }, [id, duration, onDismiss]);

  return (
    <div
      className={`relative overflow-hidden pointer-events-auto rounded-xl bg-[#0f172a]/95 backdrop-blur-xl border ${config.border} ${config.glow} p-4 w-80 sm:w-96 animate-slide-in-right transition-all flex items-start gap-3`}
    >
      <div className="flex-shrink-0 mt-0.5">
        <Icon className={`w-5 h-5 ${config.iconColor}`} />
      </div>

      <div className="flex-1 min-w-0 pr-2">
        {title && <h4 className="text-xs font-bold text-white tracking-wide">{title}</h4>}
        {message && <p className="text-[11px] text-slate-300 mt-0.5 leading-relaxed">{message}</p>}
      </div>

      <button
        onClick={() => onDismiss(id)}
        className="flex-shrink-0 p-1 rounded-md text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
        aria-label="Close notification"
      >
        <X className="w-3.5 h-3.5" />
      </button>

      {/* Progress countdown indicator */}
      <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-white/10">
        <div
          className={`h-full ${config.barColor} transition-all duration-75 ease-linear`}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}

export function ToastContainer({ toasts = [], onDismiss }) {
  if (!toasts.length) return null;

  return (
    <div className="fixed top-20 right-6 lg:right-[410px] z-50 flex flex-col space-y-3 pointer-events-none transition-all duration-300">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  );
}

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const dismissToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const addToast = useCallback(({ type = 'info', title, message, duration = 5000 }) => {
    const id = Date.now() + Math.random().toString(36).substring(2, 6);
    const newToast = { id, type, title, message, duration };
    setToasts((prev) => [...prev.slice(-2), newToast]);
  }, []);

  const toast = useMemo(
    () => ({
      success: (title, message, duration) => addToast({ type: 'success', title, message, duration }),
      warning: (title, message, duration) => addToast({ type: 'warning', title, message, duration }),
      error: (title, message, duration) => addToast({ type: 'error', title, message, duration }),
      info: (title, message, duration) => addToast({ type: 'info', title, message, duration }),
    }),
    [addToast]
  );

  const contextValue = useMemo(
    () => ({ addToast, dismissToast, toast }),
    [addToast, dismissToast, toast]
  );

  return (
    <ToastContext.Provider value={contextValue}>
      {children}
      <ToastContainer toasts={toasts} onDismiss={dismissToast} />
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
}
