import React, { useEffect, Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Eager load LandingPage for immediate, ultra-fast initial render
import LandingPage from './pages/LandingPage';

// Lazy load other views for modular resilience and clean chunking
const DashboardPage = lazy(() => import('./pages/DashboardPage'));
const LeaderboardsPage = lazy(() => import('./pages/LeaderboardsPage'));
const PlayerExplorerPage = lazy(() => import('./pages/PlayerExplorerPage'));
const PlayerDetailPage = lazy(() => import('./pages/PlayerDetailPage'));
const PlayerComparisonPage = lazy(() => import('./pages/PlayerComparisonPage'));
const ArchetypesPage = lazy(() => import('./pages/ArchetypesPage'));
const PressureAnalyticsPage = lazy(() => import('./pages/PressureAnalyticsPage'));
const MethodologyPage = lazy(() => import('./pages/MethodologyPage'));

// Scroll to top on route change
function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}

// Clean loading state indicator
function PageFallback() {
  return (
    <div className="min-h-[50vh] flex flex-col items-center justify-center space-y-4">
      <div className="w-10 h-10 border-2 border-[#FFC928]/30 border-t-[#FFC928] rounded-full animate-spin" />
      <span className="text-xs text-[#A6A9A5] uppercase tracking-widest font-sans">
        Loading View...
      </span>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <ScrollToTop />
      <div className="min-h-screen bg-graphite-950 text-cloud-100 flex flex-col font-sans selection:bg-sunshine-500 selection:text-graphite-950 relative overflow-x-hidden">
        {/* Subtle Ambient Radial Lighting */}
        <div className="fixed top-0 left-1/4 w-[600px] h-[600px] bg-sunshine-500/5 rounded-full blur-[140px] pointer-events-none -z-10" />
        <div className="fixed bottom-1/4 right-1/4 w-[500px] h-[500px] bg-sunshine-400/3 rounded-full blur-[160px] pointer-events-none -z-10" />

        {/* Global Navigation */}
        <Navbar />

        {/* Main Content Viewport with Suspense Protection */}
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
          <Suspense fallback={<PageFallback />}>
            <Routes>
              <Route path="/" element={<LandingPage />} />
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/leaderboards" element={<LeaderboardsPage />} />
              <Route path="/players" element={<PlayerExplorerPage />} />
              <Route path="/players/:id" element={<PlayerDetailPage />} />
              <Route path="/compare" element={<PlayerComparisonPage />} />
              <Route path="/archetypes" element={<ArchetypesPage />} />
              <Route path="/analytics" element={<PressureAnalyticsPage />} />
              <Route path="/methodology" element={<MethodologyPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </Suspense>
        </main>

        {/* Global Footer */}
        <Footer />
      </div>
    </Router>
  );
}
