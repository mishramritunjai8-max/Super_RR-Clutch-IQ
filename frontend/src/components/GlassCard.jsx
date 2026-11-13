import React from 'react';

export default function GlassCard({
  children,
  className = '',
  elevated = false,
  hover = true,
  glow = false,
  onClick,
  ...props
}) {
  return (
    <div
      onClick={onClick}
      className={`rounded-2xl transition-all duration-200 ${
        elevated ? 'glass-panel-elevated' : 'glass-panel'
      } ${hover ? 'glass-panel-hover' : ''} ${
        glow ? 'border-[#FFC928]/40 shadow-sunshine-sm' : ''
      } ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
