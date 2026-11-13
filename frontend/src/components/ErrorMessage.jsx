import React from 'react';
import { AlertCircle, RefreshCw, WifiOff } from 'lucide-react';

export default function ErrorMessage({
  title = 'Unable to Load Data',
  message = 'An error occurred while connecting to the CLUTCH IQ backend service.',
  onRetry,
}) {
  return (
    <div className="glass-panel rounded-2xl p-8 max-w-xl mx-auto my-8 text-center space-y-4 border-amber-500/20">
      <div className="w-12 h-12 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center mx-auto text-amber-400">
        <WifiOff className="w-6 h-6" />
      </div>
      <div className="space-y-1">
        <h3 className="text-base font-bold text-[#F2F4F1] font-display">{title}</h3>
        <p className="text-xs sm:text-sm text-[#A6A9A5] leading-relaxed max-w-md mx-auto">
          {message}
        </p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-white/10 hover:bg-white/15 text-xs font-semibold text-[#F2F4F1] border border-white/10 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry Request</span>
        </button>
      )}
    </div>
  );
}
