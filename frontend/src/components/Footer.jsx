import React from 'react';
import { Link } from 'react-router-dom';
import { Flame, ShieldCheck, Activity, Github } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="w-full border-t border-white/10 bg-[#1C1D20]/80 backdrop-blur-md mt-20 pt-12 pb-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-12">
          {/* Brand & Description */}
          <div className="md:col-span-2 space-y-3">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 rounded-lg bg-[#FFC928] p-0.5 flex items-center justify-center">
                <div className="w-full h-full bg-[#1C1D20] rounded-[6px] flex items-center justify-center">
                  <Flame className="w-4 h-4 text-[#FFC928]" />
                </div>
              </div>
              <span className="font-extrabold tracking-wider text-lg font-display text-[#F2F4F1]">
                SUPER RR <span className="text-[#FFC928]">CLUTCH IQ</span>
              </span>
            </div>
            <p className="text-[#A6A9A5] text-xs sm:text-sm max-w-md leading-relaxed">
              Beyond Statistics. Discovering players who perform under pressure. 
              Built with Bayesian credibility shrinkage, empirical Bayes baseline regularisation, and unsupervised K-Means archetyping.
            </p>
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-[11px] text-[#A6A9A5]">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>FastAPI Backend v1.0.0 Active • In-Memory Indexed Engine</span>
            </div>
          </div>

          {/* Platform Navigation */}
          <div>
            <h4 className="text-xs uppercase tracking-widest text-[#FFC928] font-bold mb-3 font-display">
              Platform
            </h4>
            <ul className="space-y-2 text-xs sm:text-sm text-[#A6A9A5]">
              <li>
                <Link to="/dashboard" className="hover:text-[#F2F4F1] transition-colors">Dashboard Overview</Link>
              </li>
              <li>
                <Link to="/leaderboards" className="hover:text-[#F2F4F1] transition-colors">Clutch Leaderboards</Link>
              </li>
              <li>
                <Link to="/players" className="hover:text-[#F2F4F1] transition-colors">Player Explorer</Link>
              </li>
              <li>
                <Link to="/compare" className="hover:text-[#F2F4F1] transition-colors">Side-by-Side Comparison</Link>
              </li>
              <li>
                <Link to="/archetypes" className="hover:text-[#F2F4F1] transition-colors">Player Archetypes</Link>
              </li>
            </ul>
          </div>

          {/* Research & Transparency */}
          <div>
            <h4 className="text-xs uppercase tracking-widest text-[#FFC928] font-bold mb-3 font-display">
              Methodology
            </h4>
            <ul className="space-y-2 text-xs sm:text-sm text-[#A6A9A5]">
              <li>
                <Link to="/methodology" className="hover:text-[#F2F4F1] transition-colors">Mathematical Framework</Link>
              </li>
              <li>
                <Link to="/analytics" className="hover:text-[#F2F4F1] transition-colors">Pressure Set Algebra</Link>
              </li>
              <li>
                <a href="http://localhost:8000/docs" target="_blank" rel="noreferrer" className="hover:text-[#F2F4F1] transition-colors flex items-center space-x-1">
                  <span>FastAPI Swagger UI</span>
                </a>
              </li>
              <li>
                <a href="http://localhost:8000/redoc" target="_blank" rel="noreferrer" className="hover:text-[#F2F4F1] transition-colors">
                  API ReDoc Schema
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-6 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between text-[11px] text-[#A6A9A5] gap-4">
          <p>
            Rajasthan Royals Hackathon 2026 • Statistical intelligence product. Empirical analysis across 883 T20 matches.
          </p>
          <div className="flex items-center space-x-4">
            <span className="flex items-center space-x-1">
              <ShieldCheck className="w-3.5 h-3.5 text-[#FFC928]" />
              <span>Zero Outcome Leakage</span>
            </span>
            <span className="flex items-center space-x-1">
              <Activity className="w-3.5 h-3.5 text-emerald-400" />
              <span>ICC Rule 16 Super Over Quarantined</span>
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
}
