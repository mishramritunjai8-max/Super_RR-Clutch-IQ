import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

// Pages
import LandingPage from './pages/LandingPage';
import DashboardPage from './pages/DashboardPage';
import LeaderboardsPage from './pages/LeaderboardsPage';
import PlayerExplorerPage from './pages/PlayerExplorerPage';
import PlayerDetailPage from './pages/PlayerDetailPage';
import PlayerComparisonPage from './pages/PlayerComparisonPage';
import ArchetypesPage from './pages/ArchetypesPage';
import PressureAnalyticsPage from './pages/PressureAnalyticsPage';
import MethodologyPage from './pages/MethodologyPage';

// Scroll to top on route change
function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
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

        {/* Main Content Viewport */}
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
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
        </main>

        {/* Global Footer */}
        <Footer />
      </div>
    </Router>
  );
}
