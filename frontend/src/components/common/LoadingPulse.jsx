import React from 'react';
import clsx from 'clsx';

export default function LoadingPulse({
  lines = 1,
  height = 'h-4',
  className = '',
  circle = false,
  width = 'w-full',
}) {
  if (circle) {
    return (
      <div
        className={clsx(
          'rounded-full bg-slate-200 animate-pulse border border-slate-300',
          height,
          width,
          className
        )}
      />
    );
  }

  return (
    <div className={clsx('space-y-2.5 w-full', className)}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className={clsx(
            'bg-gradient-to-r from-slate-200 via-slate-100 to-slate-200 rounded-md animate-pulse border border-slate-200/80',
            height,
            i === lines - 1 && lines > 1 ? 'w-4/5' : width
          )}
        />
      ))}
    </div>
  );
}
