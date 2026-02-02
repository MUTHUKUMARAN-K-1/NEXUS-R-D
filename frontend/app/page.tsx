'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Search, 
  Sparkles, 
  Gem,
  ArrowRight, 
  Zap, 
  Shield, 
  Globe ,
  Lightbulb,
  TrendingUp,
  FileSearch,
  Microscope,
  Moon,
  Sun,
} from 'lucide-react';
import Image from 'next/image';
import ResearchDashboard from '@/components/ResearchDashboard';
import { useTheme } from '@/context/ThemeContext';

// Theme Toggle Component for Home Page
function HomeThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <motion.button
      onClick={toggleTheme}
      className="p-2 rounded-lg border border-[var(--border-color)] bg-[var(--bg-elevated)] hover:border-[var(--primary)] transition-all duration-300"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
    >
      <AnimatePresence mode="wait" initial={false}>
        {theme === 'dark' ? (
          <motion.div
            key="moon"
            initial={{ rotate: -90, opacity: 0 }}
            animate={{ rotate: 0, opacity: 1 }}
            exit={{ rotate: 90, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <Moon className="w-5 h-5 text-[var(--primary)]" />
          </motion.div>
        ) : (
          <motion.div
            key="sun"
            initial={{ rotate: 90, opacity: 0 }}
            animate={{ rotate: 0, opacity: 1 }}
            exit={{ rotate: -90, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <Sun className="w-5 h-5 text-[var(--primary)]" />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.button>
  );
}

export default function Home() {
  const [isResearching, setIsResearching] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [query, setQuery] = useState('');

  const handleStartResearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    try {
      // Call backend directly
      const response = await fetch('http://localhost:8000/research', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          domain: null,
          geographic_scope: ['US', 'EU', 'CN', 'JP'],
          time_range_years: 5,
          max_recursion_depth: 4,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        setIsResearching(true);
      } else {
        console.error('Backend error:', response.status);
        // Show error instead of demo mode
        alert('Failed to start research. Please check that backend is running on http://localhost:8000');
      }
    } catch (error) {
      console.error('Failed to start research:', error);
      alert('Cannot connect to backend. Please start the backend server: python main.py');
    }
  };

  if (isResearching && sessionId) {
    return <ResearchDashboard sessionId={sessionId} query={query} />;
  }

  return (
    <main className="min-h-screen relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[var(--primary)]/20 rounded-full blur-[128px] animate-pulse-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-[128px] animate-pulse-slow" style={{ animationDelay: '1s' }} />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[var(--accent-cyan)]/10 rounded-full blur-[150px]" />
      </div>

      {/* Hero Section */}
      <div className="container mx-auto px-6 py-12 lg:py-20">
        {/* Header */}
        <motion.header 
          className="flex items-center justify-between mb-20"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex items-center gap-3">
            <Image 
              src="/logo.jpg" 
              alt="NEXUS-R&D" 
              width={48} 
              height={48} 
              className="rounded-xl"
            />
            <span className="text-2xl font-bold gradient-text">NEXUS-R&D</span>
          </div>
          <nav className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">Features</a>
            <a href="#how-it-works" className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">How It Works</a>
            <HomeThemeToggle />
            <a 
              href="https://github.com/MUTHUKUMARAN-K-1/NEXUS-R-D" 
              target="_blank" 
              rel="noopener noreferrer"
              className="btn-secondary text-sm"
            >
              Documentation
            </a>
          </nav>
        </motion.header>

        {/* Main Hero */}
        <div className="text-center max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/10 border border-primary-500/20 mb-8">
              <Gem className="w-4 h-4 text-primary-400" />
              <span className="text-sm text-primary-300">Powered by Gemini Deep Research Pro</span>
            </div>
          </motion.div>

          <motion.h1
            className="text-5xl md:text-7xl font-bold mb-6 leading-tight"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <span className="text-[var(--text-primary)]">From Patents to Profits:</span>
            <br />
            <span className="gradient-text">Autonomous Discovery</span>
            <br />
            <span className="text-[var(--text-primary)]">of Tomorrow's Innovations</span>
          </motion.h1>

          <motion.p
            className="text-xl text-[var(--text-secondary)] mb-12 max-w-3xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            NEXUS-R&D is an autonomous multi-agent system that discovers innovation 
            whitespace through recursive research across patents, markets, and technology trends.
          </motion.p>

          {/* Search Form */}
          <motion.form
            onSubmit={handleStartResearch}
            className="relative max-w-3xl mx-auto mb-16"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
          >
            <div className="relative glass-card p-2">
              <div className="flex items-center gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-dark-400" />
                  <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Explore innovation opportunities in any domain..."
                    className="w-full pl-12 pr-4 py-4 bg-transparent border-none focus:outline-none text-lg text-white placeholder:text-dark-400"
                  />
                </div>
                <button 
                  type="submit"
                  className="btn-primary flex items-center gap-2 text-lg px-8 py-4"
                >
                  <span>Discover</span>
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Quick Suggestions */}
            <div className="flex flex-wrap items-center justify-center gap-3 mt-6">
              <span className="text-dark-400 text-sm">Try:</span>
              {[
                'Solid-state battery technology',
                'AI drug discovery',
                'Quantum computing applications',
                'Carbon capture methods',
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => setQuery(suggestion)}
                  className="px-3 py-1.5 text-sm text-[var(--text-secondary)] bg-[var(--bg-elevated)] rounded-lg border border-[var(--border-color)] hover:border-[var(--primary)] hover:text-[var(--primary)] transition-all"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </motion.form>

          {/* Feature Cards - How It Works */}
          <motion.div
            id="how-it-works"
            className="grid grid-cols-1 md:grid-cols-3 gap-6"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.6 }}
          >
            <FeatureCard
              icon={<FileSearch className="w-6 h-6" />}
              title="Patent Landscape"
              description="Deep analysis of global patent databases with AI-powered claim extraction"
              color="cyan"
            />
            <FeatureCard
              icon={<TrendingUp className="w-6 h-6" />}
              title="Market Intelligence"
              description="Real-time startup funding, M&A activity, and market sizing analysis"
              color="purple"
            />
            <FeatureCard
              icon={<Microscope className="w-6 h-6" />}
              title="Tech Trends"
              description="Research paper analysis with technology maturity predictions"
              color="pink"
            />
          </motion.div>
        </div>

        {/* Unique Features Section */}
        <motion.section
          id="features"
          className="mt-32"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.8 }}
        >
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-[var(--text-primary)] mb-4">
              International-Level Innovation
            </h2>
            <p className="text-[var(--text-secondary)] text-lg max-w-2xl mx-auto">
              Features that set NEXUS-R&D apart from any existing solution
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <InnovationCard
              icon={<Shield className="w-8 h-8" />}
              title="Epistemic Verification Protocol"
              description="Multi-agent adversarial verification system. An AI skeptic challenges every claim, actively searching for contradicting evidence before finalizing insights."
              badge="Novel"
            />
            <InnovationCard
              icon={<Lightbulb className="w-8 h-8" />}
              title="Innovation Whitespace Mapping"
              description="Identifies gaps where patent coverage is thin, market demand exists, and technology is maturing—the sweet spots for innovation investment."
              badge="First of its kind"
            />
            <InnovationCard
              icon={<Globe className="w-8 h-8" />}
              title="Recursive Knowledge Spirals"
              description="Each discovery triggers new targeted searches. A single query can spawn 100+ focused sub-investigations, building deep domain understanding."
              badge="Deep Research"
            />
            <InnovationCard
              icon={<Zap className="w-8 h-8" />}
              title="Temporal Innovation Forecasting"
              description="Predicts technology maturation timelines, optimal patent filing windows, and competitive threat emergence using pattern analysis."
              badge="Predictive"
            />
          </div>
        </motion.section>
      </div>

      {/* Footer */}
      <footer className="border-t border-dark-700 mt-32 py-8">
        <div className="container mx-auto px-6 text-center text-dark-400">
          <p>Built for VETROX AGENTIC 3.0 Hackathon | Powered by Gemini 3</p>
        </div>
      </footer>
    </main>
  );
}

function FeatureCard({ 
  icon, 
  title, 
  description, 
  color 
}: { 
  icon: React.ReactNode; 
  title: string; 
  description: string; 
  color: 'cyan' | 'purple' | 'pink';
}) {
  const colorClasses = {
    cyan: 'from-cyan-500/20 to-cyan-500/5 border-cyan-500/30 group-hover:border-cyan-400/50',
    purple: 'from-purple-500/20 to-purple-500/5 border-purple-500/30 group-hover:border-purple-400/50',
    pink: 'from-pink-500/20 to-pink-500/5 border-pink-500/30 group-hover:border-pink-400/50',
  };

  const iconColors = {
    cyan: 'text-cyan-400',
    purple: 'text-purple-400',
    pink: 'text-pink-400',
  };

  return (
    <div className={`group glass-card p-6 bg-gradient-to-b ${colorClasses[color]} transition-all duration-300 hover:-translate-y-1`}>
      <div className={`w-12 h-12 rounded-xl bg-[var(--bg-elevated)] flex items-center justify-center mb-4 ${iconColors[color]}`}>
        {icon}
      </div>
      <h3 className="text-xl font-semibold text-[var(--text-primary)] mb-2">{title}</h3>
      <p className="text-[var(--text-secondary)]">{description}</p>
    </div>
  );
}

function InnovationCard({
  icon,
  title,
  description,
  badge,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  badge: string;
}) {
  return (
    <div className="innovation-card glass-card p-8 transition-all duration-300 hover:border-primary-400/40">
      <div className="flex items-start gap-4">
        <div className="innovation-icon w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-500/20 to-purple-500/20 flex items-center justify-center flex-shrink-0">
          {icon}
        </div>
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h3 className="text-xl font-semibold text-[var(--text-primary)]">{title}</h3>
            <span className="innovation-badge px-2 py-0.5 text-xs font-medium rounded-full">
              {badge}
            </span>
          </div>
          <p className="text-[var(--text-secondary)] leading-relaxed">{description}</p>
        </div>
      </div>
    </div>
  );
}
