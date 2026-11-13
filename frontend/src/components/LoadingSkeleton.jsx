import React from 'react';

export function CardSkeleton({ rows = 3, className = '' }) {
  return (
    <div className={`glass-panel rounded-2xl p-6 animate-pulse space-y-4 ${className}`}>
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-xl bg-white/10"></div>
        <div className="space-y-2 flex-1">
          <div className="h-4 bg-white/15 rounded w-1/3"></div>
          <div className="h-3 bg-white/10 rounded w-1/4"></div>
        </div>
      </div>
      <div className="space-y-2 pt-2">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="h-3 bg-white/10 rounded w-full"></div>
        ))}
      </div>
    </div>
  );
}

export function TableSkeleton({ rows = 8, cols = 6 }) {
  return (
    <div className="glass-panel rounded-2xl overflow-hidden animate-pulse">
      <div className="h-12 bg-white/10 border-b border-white/10 flex items-center px-6">
        <div className="h-4 bg-white/20 rounded w-1/4"></div>
      </div>
      <div className="divide-y divide-white/5 p-4 space-y-3">
        {Array.from({ length: rows }).map((_, r) => (
          <div key={r} className="flex items-center justify-between py-2.5 px-2">
            <div className="h-4 bg-white/15 rounded w-1/5"></div>
            <div className="h-4 bg-white/10 rounded w-1/8"></div>
            <div className="h-4 bg-white/10 rounded w-1/8"></div>
            <div className="h-4 bg-white/10 rounded w-1/8"></div>
            <div className="h-4 bg-white/20 rounded w-1/10"></div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function StatSkeleton() {
  return (
    <div className="glass-panel rounded-2xl p-5 animate-pulse space-y-3">
      <div className="w-8 h-8 rounded-lg bg-white/10"></div>
      <div className="h-7 bg-white/20 rounded w-1/2"></div>
      <div className="h-3 bg-white/10 rounded w-3/4"></div>
    </div>
  );
}

export default CardSkeleton;
