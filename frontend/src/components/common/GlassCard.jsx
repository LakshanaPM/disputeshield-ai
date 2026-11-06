import React from 'react';
import clsx from 'clsx';

/**
 * Reusable GlassCard component with backdrop blur, subtle inner border glow,
 * and optional header, title, subtitle, and action slots.
 */
export default function GlassCard({
  title,
  subtitle,
  action,
  children,
  footer,
  className,
  headerClassName,
  hoverGlow = true,
  ...props
}) {
  return (
    <div
      className={clsx(
        'glass-card p-5 relative overflow-hidden',
        hoverGlow && 'hover:border-paypal-blue/40 hover:shadow-[0_0_25px_rgba(0,112,186,0.15)]',
        className
      )}
      {...props}
    >
      {(title || subtitle || action) && (
        <div className={clsx('flex items-center justify-between pb-3 mb-4 border-b border-slate-100', headerClassName)}>
          <div>
            {title && <h3 className="text-base font-bold text-slate-900 tracking-tight">{title}</h3>}
            {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
          </div>
          {action && <div className="flex items-center space-x-2">{action}</div>}
        </div>
      )}

      <div>{children}</div>

      {footer && (
        <div className="pt-3 mt-4 border-t border-slate-100 text-xs text-slate-500">
          {footer}
        </div>
      )}
    </div>
  );
}
