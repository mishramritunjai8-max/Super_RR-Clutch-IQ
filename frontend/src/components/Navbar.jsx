import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Flame, Trophy, Users, BarChart3, Binary, BookOpen, Menu, X, ArrowUpRight } from 'lucide-react';

export default function Navbar() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navLinks = [
    { name: 'Overview', path: '/' },
    { name: 'Dashboard', path: '/dashboard', icon: BarChart3 },
    { name: 'Leaderboards', path: '/leaderboards', icon: Trophy },
    { name: 'Players', path: '/players', icon: Users },
    { name: 'Archetypes', path: '/archetypes', icon: Binary },
    { name: 'Analytics', path: '/analytics', icon: Flame },
    { name: 'Methodology', path: '/methodology', icon: BookOpen },
  ];

  const isActive = (path) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <header className="sticky top-0 z-50 w-full px-4 sm:px-6 lg:px-8 pt-4 pb-2">
      <nav className="max-w-7xl mx-auto glass-panel rounded-2xl px-4 py-3 sm:px-6 flex items-center justify-between transition-all duration-300">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center space-x-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#FFC928] to-[#E5B422] p-0.5 shadow-sunshine-sm flex items-center justify-center transition-transform group-hover:scale-105">
            <div className="w-full h-full bg-[#1C1D20] rounded-[10px] flex items-center justify-center">
              <Flame className="w-5 h-5 text-[#FFC928]" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <span className="font-extrabold tracking-wider text-base sm:text-lg font-display text-[#F2F4F1]">SUPER RR</span>
              <span className="w-1.5 h-1.5 rounded-full bg-[#FFC928] animate-pulse"></span>
            </div>
            <span className="text-[10px] tracking-widest uppercase font-semibold text-[#FFC928] block -mt-1">CLUTCH IQ</span>
          </div>
        </Link>

        {/* Desktop Navigation Links */}
        <div className="hidden md:flex items-center space-x-1 lg:space-x-2">
          {navLinks.map((link) => {
            const active = isActive(link.path);
            return (
              <Link
                key={link.path}
                to={link.path}
                className={`px-3 py-1.5 rounded-xl text-sm font-medium transition-all duration-200 flex items-center space-x-1.5 ${
                  active
                    ? 'bg-[#FFC928]/15 text-[#FFC928] border border-[#FFC928]/30 shadow-sm'
                    : 'text-[#A6A9A5] hover:text-[#F2F4F1] hover:bg-white/5'
                }`}
              >
                {link.icon && <link.icon className="w-3.5 h-3.5 opacity-80" />}
                <span>{link.name}</span>
              </Link>
            );
          })}
        </div>

        {/* Explore CTA & Compare Link */}
        <div className="hidden lg:flex items-center space-x-3">
          <Link
            to="/compare"
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold uppercase tracking-wider transition-all duration-200 border ${
              location.pathname === '/compare'
                ? 'bg-[#FFC928] text-[#1C1D20] border-[#FFC928]'
                : 'border-white/15 text-[#F2F4F1] hover:border-[#FFC928]/50 hover:bg-white/5'
            }`}
          >
            Compare
          </Link>
          <Link
            to="/dashboard"
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-[#FFC928] to-[#E5B422] text-[#1C1D20] text-xs font-bold uppercase tracking-wider shadow-sunshine-sm hover:shadow-sunshine-md hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center space-x-1"
          >
            <span>Explore Dashboard</span>
            <ArrowUpRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {/* Mobile Hamburger Button */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="md:hidden p-2 rounded-xl text-[#F2F4F1] hover:bg-white/10 transition-colors"
          aria-label="Toggle navigation menu"
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </nav>

      {/* Mobile Menu Dropdown */}
      {mobileMenuOpen && (
        <div className="md:hidden mt-2 max-w-7xl mx-auto glass-panel-elevated rounded-2xl p-4 transition-all">
          <div className="flex flex-col space-y-1">
            {navLinks.map((link) => {
              const active = isActive(link.path);
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`px-4 py-2.5 rounded-xl text-sm font-medium flex items-center space-x-2.5 ${
                    active
                      ? 'bg-[#FFC928]/15 text-[#FFC928] border border-[#FFC928]/30'
                      : 'text-[#A6A9A5] hover:text-[#F2F4F1] hover:bg-white/5'
                  }`}
                >
                  {link.icon && <link.icon className="w-4 h-4 text-[#FFC928]" />}
                  <span>{link.name}</span>
                </Link>
              );
            })}
            <div className="pt-2 flex flex-col space-y-2 border-t border-white/10 mt-2">
              <Link
                to="/compare"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full text-center py-2.5 rounded-xl border border-white/20 text-xs font-semibold uppercase tracking-wider text-[#F2F4F1]"
              >
                Player Comparison
              </Link>
              <Link
                to="/dashboard"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full text-center py-2.5 rounded-xl bg-[#FFC928] text-[#1C1D20] text-xs font-bold uppercase tracking-wider shadow-sunshine-sm"
              >
                Explore Dashboard
              </Link>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
