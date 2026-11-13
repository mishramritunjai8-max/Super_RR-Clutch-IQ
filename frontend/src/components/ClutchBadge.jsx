import React from 'react';
import { Flame, Sparkles } from 'lucide-react';

export default function ClutchBadge({ score, rank, cohort = 'primary', size = 'md', showLabel = true }) {
  if (score === null || score === undefined) {
    return (
      <span className="px-2 py-0.5 rounded-lg bg-white/5 border border-white/10 text-xs text-[#A6A9A5]">
        Unrated
      </span>
    );
  }

  const numScore = typeof score === 'number' ? score : parseFloat(score);
  const formattedScore = !isNaN(numScore) ? numScore.toFixed(2) : score;

  const isElite = numScore >= 70;
  const isSolid = numScore >= 50 && numScore < 70;

  // Size styling
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 space-x-1',
    md: 'text-sm px-3 py-1 space-x-1.5',
    lg: 'text-base px-4 py-1.5 space-x-2',
    xl: 'text-2xl px-5 py-2.5 space-x-3',
  }[size] || 'text-sm px-3 py-1 space-x-1.5';

  return (
    <div className="inline-flex items-center space-x-2">
      {rank && (
        <span className="px-2 py-0.5 rounded-md bg-white/10 text-[#F2F4F1] font-mono text-xs font-bold border border-white/10">
          #{rank}
        </span>
      )}

      <div
        className={`inline-flex items-center rounded-xl font-mono font-bold tracking-tight transition-all ${sizeClasses} ${
          isElite
            ? 'bg-[#FFC928]/20 text-[#FFC928] border border-[#FFC928]/50 shadow-sunshine-sm'
            : isSolid
            ? 'bg-white/10 text-[#F2F4F1] border border-white/20'
            : 'bg-white/5 text-[#A6A9A5] border border-white/10'
        }`}
      >
        <Flame className={`${size === 'xl' ? 'w-6 h-6' : size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5'} text-[#FFC928]`} />
        <span>{formattedScore}</span>
        {showLabel && size !== 'sm' && (
          <span className="text-[10px] font-sans font-medium uppercase tracking-wider text-[#A6A9A5] ml-0.5">
            IQ
          </span>
        )}
      </div>

      {cohort === 'emerging' && (
        <span className="px-2 py-0.5 rounded-md bg-amber-500/15 border border-amber-500/30 text-[10px] uppercase tracking-wider text-amber-300 font-medium">
          Emerging
        </span>
      )}
    </div>
  );
}
