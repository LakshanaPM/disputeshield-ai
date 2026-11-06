import React from 'react';
import clsx from 'clsx';
import {
  Zap,
  Clock,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  ShieldCheck,
  ShieldAlert,
  Edit3,
} from 'lucide-react';

const STATUS_CONFIGS = {
  AUTO_SUBMITTED: {
    label: 'Auto-Submitted',
    variant: 'success',
    icon: Zap,
  },
  DRAFT_PENDING_REVIEW: {
    label: 'Draft (Pending Review)',
    variant: 'warning',
    icon: Clock,
  },
  ESCALATED: {
    label: 'Escalated to Human',
    variant: 'danger',
    icon: AlertTriangle,
  },
  OVERRIDDEN: {
    label: 'Merchant Overridden',
    variant: 'purple',
    icon: Edit3,
  },
  APPROVED: {
    label: 'Merchant Approved',
    variant: 'info',
    icon: CheckCircle2,
  },
  WON: {
    label: 'Won',
    variant: 'success',
    icon: ShieldCheck,
  },
  LOST: {
    label: 'Lost',
    variant: 'danger',
    icon: XCircle,
  },
  UNDER_REVIEW: {
    label: 'Under Review',
    variant: 'info',
    icon: Clock,
  },
  WAITING_FOR_SELLER_RESPONSE: {
    label: 'Action Required',
    variant: 'warning',
    icon: AlertTriangle,
  },
  OPEN: {
    label: 'Open',
    variant: 'warning',
    icon: AlertTriangle,
  },
};

const VARIANT_STYLES = {
  success: 'bg-emerald-50 text-emerald-800 border-emerald-200 font-semibold',
  warning: 'bg-amber-50 text-amber-800 border-amber-200 font-semibold',
  danger: 'bg-rose-50 text-rose-800 border-rose-200 font-semibold',
  info: 'bg-sky-50 text-sky-800 border-sky-200 font-semibold',
  purple: 'bg-purple-50 text-purple-800 border-purple-200 font-semibold',
  neutral: 'bg-slate-100 text-slate-800 border-slate-200 font-medium',
};

const SIZES = {
  sm: 'text-[11px] px-2 py-0.5 gap-1',
  md: 'text-xs px-2.5 py-1 gap-1.5',
  lg: 'text-sm px-3 py-1.5 gap-2',
};

export default function Badge({
  status,
  variant,
  size = 'md',
  icon: CustomIcon,
  children,
  className,
  dot = false,
}) {
  const config = status ? STATUS_CONFIGS[status] : null;
  const activeVariant = variant || (config ? config.variant : 'neutral');
  const IconComponent = CustomIcon || (config ? config.icon : null);
  const displayText = children || (config ? config.label : status);

  return (
    <span
      className={clsx(
        'inline-flex items-center font-medium rounded-full border transition-colors select-none',
        VARIANT_STYLES[activeVariant] || VARIANT_STYLES.neutral,
        SIZES[size] || SIZES.md,
        className
      )}
    >
      {dot && (
        <span
          className={clsx(
            'w-1.5 h-1.5 rounded-full',
            activeVariant === 'success' && 'bg-emerald-500',
            activeVariant === 'warning' && 'bg-amber-500',
            activeVariant === 'danger' && 'bg-rose-500',
            activeVariant === 'info' && 'bg-sky-500',
            activeVariant === 'purple' && 'bg-purple-500',
            activeVariant === 'neutral' && 'bg-slate-500'
          )}
        />
      )}
      {IconComponent && <IconComponent className={size === 'sm' ? 'w-3 h-3' : 'w-3.5 h-3.5'} />}
      <span>{displayText}</span>
    </span>
  );
}
