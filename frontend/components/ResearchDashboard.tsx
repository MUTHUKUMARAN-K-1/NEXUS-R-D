'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Search,
  Zap,
  FileSearch,
  TrendingUp,
  Microscope,
  Shield,
  Sparkles,
  CheckCircle2,
  XCircle,
  Loader2,
  ChevronRight,
  Volume2,
  Download,
  ExternalLink,
  Target,
  Clock,
  BarChart3,
  Lightbulb,
  AlertTriangle,
  FileDown,
  AlertCircle,
  TrendingDown,
  Users,
  Moon,
  Sun,
} from 'lucide-react';
import dynamic from 'next/dynamic';
import Image from 'next/image';
import { useTheme } from '@/context/ThemeContext';

// Dynamically import CitationGraph to avoid SSR issues with D3
const CitationGraph = dynamic(() => import('./CitationGraph'), { ssr: false });

interface AgentStatus {
  status: 'idle' | 'running' | 'completed' | 'error';
  task?: string;
  progress: number;
  results: number;
}

interface SessionStatus {
  session_id: string;
  phase: string;
  started_at: string;
  agents: Record<string, AgentStatus>;
  sources_analyzed: number;
  error?: string;
}

interface WhitespaceOpportunity {
  title: string;
  description: string;
  opportunity_type: string;
  confidence_score: number;
  potential_impact: string;
  recommended_actions: string[];
  investment_score?: number;
}

interface Patent {
  patent_id: string;
  title: string;
  abstract: string;
  assignee?: string;
  filing_date?: string;
  url?: string;
  relevance_score?: number;
}

interface CompetitiveThreat {
  company_name: string;
  threat_level: 'high' | 'medium' | 'low';
  patent_count: number;
  market_overlap: number;
  threat_summary: string;
}

interface ResearchReport {
  report_id: string;
  executive_summary: {
    headline: string;
    key_finding: string;
    top_opportunities: string[];
    overall_confidence: number;
  };
  whitespace_opportunities: WhitespaceOpportunity[];
  patent_landscape: {
    total_patents: number;
    top_assignees: Record<string, number>;
    patents?: Patent[];
  };
  market_intelligence: {
    funding_total_usd: number;
    relevant_startups: any[];
  };
  tech_trends: {
    total_papers_analyzed: number;
    trends: any[];
  };
  verification_report: {
    average_confidence: number;
    total_sources_used: number;
  };
  metadata: {
    processing_time_seconds: number;
    total_sources_analyzed: number;
  };
  audio_brief_url?: string;
  competitive_threats?: CompetitiveThreat[];
}

const AGENT_INFO = {
  patent_scout: {
    name: 'Patent Scout',
    icon: FileSearch,
    color: 'cyan',
    description: 'Analyzing patent databases...',
  },
  market_analyst: {
    name: 'Market Analyst',
    icon: TrendingUp,
    color: 'purple',
    description: 'Gathering market intelligence...',
  },
  tech_trend: {
    name: 'Tech Trend',
    icon: Microscope,
    color: 'pink',
    description: 'Analyzing research papers...',
  },
  verifier: {
    name: 'Verifier',
    icon: Shield,
    color: 'green',
    description: 'Validating claims...',
  },
  synthesizer: {
    name: 'Synthesizer',
    icon: Sparkles,
    color: 'orange',
    description: 'Generating report...',
  },
};

// Theme Toggle Component
function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <motion.button
      onClick={toggleTheme}
      className="p-3 rounded-xl border border-[var(--border-color)] bg-[var(--bg-elevated)] hover:border-[var(--primary)] transition-all duration-300"
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

export default function ResearchDashboard({
  sessionId,
  query,
}: {
  sessionId: string;
  query: string;
}) {
  const [status, setStatus] = useState<SessionStatus | null>(null);
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [isComplete, setIsComplete] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'patents' | 'market' | 'trends' | 'verification'>('overview');
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Real backend API connection with polling + websocket
  useEffect(() => {
    let statusInterval: NodeJS.Timeout;
    let ws: WebSocket | null = null;

    const connectWebSocket = () => {
      try {
        // Derive WebSocket URL from API_BASE
        const wsUrl = API_BASE.replace(/^http/, 'ws');
        ws = new WebSocket(`${wsUrl}/ws/${sessionId}`);
        
        ws.onopen = () => {
          console.log('WebSocket connected');
          // Send ping to keep alive
          ws?.send('ping');
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            if (data.type === 'status_update') {
              setStatus(data.data);
            }
          } catch (e) {
            // Ignore ping/pong messages
          }
        };

        ws.onerror = (error) => {
          console.log('WebSocket error, falling back to polling');
        };

        ws.onclose = () => {
          console.log('WebSocket closed');
        };
      } catch (e) {
        console.log('WebSocket not available, using polling');
      }
    };

    const pollStatus = async () => {
      try {
        console.log(`[DEBUG] Polling status for session: ${sessionId}`);
        console.log(`[DEBUG] Fetching: ${API_BASE}/research/${sessionId}/status`);
        
        const response = await fetch(`${API_BASE}/research/${sessionId}/status`);
        console.log(`[DEBUG] Response status: ${response.status}`);
        
        if (response.ok) {
          const data = await response.json();
          console.log('[DEBUG] Status data received:', data);
          setStatus(data);

          // Check if research is complete
          if (data.phase === 'completed' || data.phase === 'failed') {
            clearInterval(statusInterval);
            
            if (data.phase === 'completed') {
              // Fetch the final report
              const reportResponse = await fetch(`${API_BASE}/research/${sessionId}/report`);
              if (reportResponse.ok) {
                const reportData = await reportResponse.json();
                setReport(reportData);
                setIsComplete(true);
              }
            } else if (data.phase === 'failed') {
              setError(data.error || 'Research failed');
            }
          }
        } else {
          console.error(`[DEBUG] Error response: ${response.status} ${response.statusText}`);
        }
      } catch (e) {
        console.error('[DEBUG] Status polling error:', e);
      }
    };

    // Connect WebSocket for real-time updates
    connectWebSocket();

    // Also poll as fallback (every 1 second for faster updates)
    pollStatus(); // Initial fetch
    statusInterval = setInterval(pollStatus, 1000);

    return () => {
      if (statusInterval) clearInterval(statusInterval);
      if (ws) ws.close();
    };
  }, [sessionId]);


  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="glass-card p-8 max-w-md text-center">
          <XCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Research Failed</h2>
          <p className="text-dark-300 mb-6">{error}</p>
          <button 
            onClick={() => window.location.reload()}
            className="btn-primary"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-[var(--border-color)] bg-[var(--bg-secondary)]/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Image 
                src="/logo.jpg" 
                alt="NEXUS-R&D" 
                width={48} 
                height={48} 
                className="rounded-xl"
              />
              <div>
                <h1 className="text-lg font-semibold text-[var(--text-primary)]">NEXUS-R&D</h1>
                <p className="text-sm text-[var(--text-muted)] truncate max-w-[300px]">{query}</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              {/* Theme Toggle */}
              <ThemeToggle />
              
              {isComplete && (
                <>
                  <button 
                    onClick={() => {
                      const link = document.createElement('a');
                      link.href = `http://localhost:8000/research/${sessionId}/export/audio`;
                      link.download = `research_brief.mp3`;
                      document.body.appendChild(link);
                      link.click();
                      document.body.removeChild(link);
                    }}
                    className="btn-secondary flex items-center gap-2"
                  >
                    <Volume2 className="w-4 h-4" />
                    Audio Brief
                  </button>
                  <button 
                    onClick={() => {
                      const link = document.createElement('a');
                      link.href = `http://localhost:8000/research/${sessionId}/export/pdf`;
                      link.download = `research_report.pdf`;
                      document.body.appendChild(link);
                      link.click();
                      document.body.removeChild(link);
                    }}
                    className="btn-primary flex items-center gap-2"
                  >
                    <Download className="w-4 h-4" />
                    Export Report
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <AnimatePresence mode="wait">
          {!isComplete ? (
            <ResearchInProgress status={status} query={query} />
          ) : (
            <ResearchResults report={report} activeTab={activeTab} setActiveTab={setActiveTab} sessionId={sessionId} />
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

function ResearchInProgress({ 
  status, 
  query 
}: { 
  status: SessionStatus | null; 
  query: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="max-w-4xl mx-auto"
    >
      {/* Progress Hero */}
      <div className="text-center mb-12">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
          className="w-24 h-24 mx-auto mb-6 rounded-full bg-gradient-to-br from-primary-500 to-purple-600 p-[3px]"
        >
          <div className="w-full h-full rounded-full bg-dark-900 flex items-center justify-center">
            <Sparkles className="w-10 h-10 text-primary-400" />
          </div>
        </motion.div>
        
        <h2 className="text-3xl font-bold text-white mb-3">Researching...</h2>
        <p className="text-dark-300 text-lg">{query}</p>
        
        {status && (
          <div className="mt-6 inline-flex items-center gap-2 px-4 py-2 bg-primary-500/10 rounded-full">
            <span className="w-2 h-2 bg-primary-400 rounded-full animate-pulse" />
            <span className="text-primary-300 font-medium">
              {status.sources_analyzed} sources analyzed
            </span>
          </div>
        )}
      </div>

      {/* Agent Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(AGENT_INFO).map(([agentId, info], index) => {
          const agentStatus = status?.agents[agentId];
          const Icon = info.icon;
          
          return (
            <motion.div
              key={agentId}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="glass-card p-5"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className={`w-10 h-10 rounded-xl bg-accent-${info.color}/20 flex items-center justify-center`}>
                  <Icon className={`w-5 h-5 text-accent-${info.color}`} />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-white">{info.name}</h3>
                  <p className="text-xs text-dark-400">
                    {agentStatus?.status === 'completed' ? 'Complete' : 
                     agentStatus?.status === 'running' ? (agentStatus.task || info.description) : 
                     agentStatus?.status === 'error' ? 'Error' : 'Waiting...'}
                  </p>
                </div>
                <StatusIndicator status={agentStatus?.status || 'idle'} />
              </div>
              
              <div className="progress-bar">
                <motion.div
                  className="progress-fill"
                  initial={{ width: 0 }}
                  animate={{ width: `${agentStatus?.progress || 0}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
              
              {(agentStatus?.results ?? 0) > 0 && (
                <p className="text-xs text-dark-400 mt-2">
                  {agentStatus?.results} results found
                </p>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Research Phases */}
      <div className="mt-8 glass-card p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Research Phases</h3>
        <div className="flex items-center justify-between">
          {['patent_search', 'market_analysis', 'verification', 'synthesis'].map((phase, index) => {
            const isActive = status?.phase === phase;
            const isComplete = status && ['completed', 'synthesis'].includes(status.phase) && 
              ['patent_search', 'market_analysis', 'tech_trends'].includes(phase);
            
            return (
              <div key={phase} className="flex items-center">
                <div className={`flex items-center gap-2 ${index > 0 ? 'ml-4' : ''}`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    isComplete ? 'bg-green-500/20 text-green-400' :
                    isActive ? 'bg-primary-500/20 text-primary-400' :
                    'bg-dark-700 text-dark-400'
                  }`}>
                    {isComplete ? <CheckCircle2 className="w-4 h-4" /> : 
                     isActive ? <Loader2 className="w-4 h-4 animate-spin" /> :
                     <span className="text-sm">{index + 1}</span>}
                  </div>
                  <span className={`text-sm ${isActive || isComplete ? 'text-white' : 'text-dark-400'}`}>
                    {phase.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                </div>
                {index < 3 && (
                  <ChevronRight className="w-5 h-5 text-dark-600 mx-2" />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}

function ResearchResults({
  report,
  activeTab,
  setActiveTab,
  sessionId,
}: {
  report: ResearchReport | null;
  activeTab: string;
  setActiveTab: (tab: any) => void;
  sessionId: string;
}) {
  if (!report) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-8"
    >
      {/* Executive Summary Hero */}
      <div className="glass-card p-8 bg-gradient-to-br from-primary-500/10 to-purple-500/10">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <p className="text-sm text-primary-400 font-medium">Executive Summary</p>
              <h1 className="text-2xl font-bold text-[var(--text-primary)]">{report.executive_summary.headline}</h1>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm text-[var(--text-muted)]">Confidence Score</p>
            <p className="text-3xl font-bold text-primary-400">
              {(report.executive_summary.overall_confidence * 100).toFixed(0)}%
            </p>
          </div>
        </div>
        
        <p className="text-lg text-[var(--text-secondary)] mb-6">{report.executive_summary.key_finding}</p>

        {report.audio_brief_url && (
            <div className="mb-8 p-4 bg-dark-800/50 rounded-xl border border-primary-500/20 flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-primary-500/20 flex items-center justify-center flex-shrink-0 animate-pulse">
                <Volume2 className="w-5 h-5 text-primary-400" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-medium text-[var(--text-primary)]">AI Audio Briefing</span>
                  <span className="text-xs text-primary-400">Ready to play</span>
                </div>
                <audio controls className="w-full h-8 opacity-80" src={report.audio_brief_url}>
                  Your browser does not support the audio element.
                </audio>
              </div>
            </div>
          )}
        
        {/* Key Stats */}
        <div className="grid grid-cols-4 gap-4">
          <StatCard
            icon={<FileSearch className="w-5 h-5" />}
            label="Patents Analyzed"
            value={report.patent_landscape.total_patents.toString()}
            color="cyan"
          />
          <StatCard
            icon={<BarChart3 className="w-5 h-5" />}
            label="Funding Tracked"
            value={`$${(report.market_intelligence.funding_total_usd / 1000000).toFixed(0)}M`}
            color="purple"
          />
          <StatCard
            icon={<Microscope className="w-5 h-5" />}
            label="Papers Reviewed"
            value={report.tech_trends.total_papers_analyzed.toString()}
            color="pink"
          />
          <StatCard
            icon={<Clock className="w-5 h-5" />}
            label="Processing Time"
            value={`${report.metadata.processing_time_seconds.toFixed(0)}s`}
            color="green"
          />
        </div>
      </div>

      {/* Whitespace Opportunities */}
      <div className="glass-card p-6">
        <div className="flex items-center gap-3 mb-6">
          <Lightbulb className="w-6 h-6 text-accent-orange" />
          <h2 className="text-xl font-bold text-[var(--text-primary)]">Innovation Whitespace</h2>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {report.whitespace_opportunities.slice(0, 4).map((opp, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className="p-5 bg-dark-800/50 rounded-xl border border-dark-700 hover:border-primary-500/40 transition-colors"
            >
              <div className="flex items-start justify-between mb-3">
                <h3 className="font-semibold text-white">{opp.title}</h3>
                <div className="flex items-center gap-2">
                  {opp.investment_score !== undefined && (
                    <span className={`px-2 py-0.5 text-xs font-bold rounded-full ${
                      opp.investment_score >= 70 ? 'bg-green-500/20 text-green-400' :
                      opp.investment_score >= 50 ? 'bg-yellow-500/20 text-yellow-400' :
                      'bg-red-500/20 text-red-400'
                    }`}>
                      🎯 {opp.investment_score.toFixed(0)}
                    </span>
                  )}
                  <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                    opp.potential_impact === 'high' ? 'bg-green-500/20 text-green-400' :
                    opp.potential_impact === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-dark-600 text-dark-300'
                  }`}>
                    {opp.potential_impact} impact
                  </span>
                </div>
              </div>
              <p className="text-sm text-dark-300 mb-3">{opp.description}</p>
              <div className="flex items-center gap-3">
                <div className="flex-1 h-2 bg-dark-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-primary-500 to-purple-500 rounded-full"
                    style={{ width: `${opp.confidence_score * 100}%` }}
                  />
                </div>
                <span className="text-xs text-dark-400">{(opp.confidence_score * 100).toFixed(0)}%</span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Tabbed Content */}
      <div className="glass-card overflow-hidden">
        <div className="border-b border-dark-700 flex items-center justify-between">
          <div className="flex">
            {['overview', 'threats', 'patents', 'market', 'trends', 'verification'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-4 text-sm font-medium transition-colors ${
                  activeTab === tab
                    ? 'text-primary-400 border-b-2 border-primary-400 bg-primary-500/5'
                    : 'text-dark-400 hover:text-white'
                }`}
              >
                {tab === 'threats' ? '🧠 Threats' : tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
          <a
            href={`http://localhost:8000/research/${sessionId}/export/pdf`}
            target="_blank"
            rel="noopener noreferrer"
            className="mr-4 px-4 py-2 bg-gradient-to-r from-primary-500 to-purple-500 text-white text-sm font-medium rounded-lg flex items-center gap-2 hover:opacity-90 transition-opacity"
          >
            <FileDown className="w-4 h-4" />
            Export PDF
          </a>
        </div>
        
        <div className="p-6">
          <TabContent tab={activeTab} report={report} />
        </div>
      </div>
    </motion.div>
  );
}

function TabContent({ tab, report }: { tab: string; report: ResearchReport }) {
  switch (tab) {
    case 'overview':
      return (
        <div className="space-y-6">
          <h3 className="text-lg font-semibold text-white">Top Opportunities</h3>
          <ul className="space-y-3">
            {report.executive_summary.top_opportunities.map((opp, index) => (
              <li key={index} className="flex items-center gap-3 p-4 bg-dark-800/50 rounded-lg">
                <div className="w-8 h-8 rounded-lg bg-primary-500/20 flex items-center justify-center text-primary-400 font-semibold">
                  {index + 1}
                </div>
                <span className="text-dark-200">{opp}</span>
              </li>
            ))}
          </ul>
        </div>
      );
    case 'threats':
      const threats = report.competitive_threats || [];
      const threatColors = {
        high: { bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500/40' },
        medium: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500/40' },
        low: { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500/40' },
      };
      return (
        <div className="space-y-6">
          <div className="flex items-center gap-3 mb-2">
            <AlertCircle className="w-6 h-6 text-red-400" />
            <h3 className="text-lg font-semibold text-white">Competitive Threat Radar</h3>
          </div>
          {threats.length === 0 ? (
            <p className="text-dark-400">No significant competitive threats identified.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {threats.map((threat, index) => {
                const colors = threatColors[threat.threat_level] || threatColors.low;
                return (
                  <div
                    key={index}
                    className={`p-4 rounded-xl border ${colors.border} ${colors.bg}`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-semibold text-white">{threat.company_name}</h4>
                      <span className={`px-2 py-0.5 text-xs font-bold rounded-full ${colors.bg} ${colors.text}`}>
                        {threat.threat_level.toUpperCase()}
                      </span>
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-dark-400">Patents</span>
                        <span className="text-white font-medium">{threat.patent_count}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-dark-400">Market Overlap</span>
                        <span className="text-white font-medium">{(threat.market_overlap * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                    <p className="text-xs text-dark-300 mt-3">{threat.threat_summary}</p>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      );
    case 'patents':
      return (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Patent Landscape</h3>
            <span className="text-dark-400">{report.patent_landscape.total_patents} patents analyzed</span>
          </div>
          
          {/* Citation Network Graph */}
          {report.patent_landscape.patents && report.patent_landscape.patents.length > 0 && (
            <div className="bg-dark-800/50 rounded-xl p-4 border border-dark-700">
              <h4 className="text-sm text-dark-400 mb-3 flex items-center gap-2">
                <span>📊 Citation Network</span>
                <span className="text-xs text-dark-500">(Interactive - drag to rearrange, click to view)</span>
              </h4>
              <CitationGraph patents={report.patent_landscape.patents} />
            </div>
          )}
          
          {/* Top Assignees */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-dark-800/50 rounded-lg">
              <h4 className="text-sm text-dark-400 mb-3">Top Assignees</h4>
              <div className="space-y-2">
                {Object.entries(report.patent_landscape.top_assignees || {}).slice(0, 5).map(([name, count]) => (
                  <div key={name} className="flex items-center justify-between">
                    <span className="text-dark-200 truncate">{name}</span>
                    <span className="text-primary-400 font-semibold">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Patent List with Links */}
          {report.patent_landscape.patents && report.patent_landscape.patents.length > 0 && (
            <div className="mt-6">
              <h4 className="text-sm text-dark-400 mb-3">Patent Details</h4>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {report.patent_landscape.patents.slice(0, 20).map((patent, index) => (
                  <div key={patent.patent_id || index} className="p-4 bg-dark-800/50 rounded-lg border border-dark-700 hover:border-primary-500/40 transition-colors">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs font-mono text-primary-400 bg-primary-500/10 px-2 py-0.5 rounded">
                            {patent.patent_id}
                          </span>
                          {patent.relevance_score && (
                            <span className="text-xs text-dark-400">
                              {(patent.relevance_score * 100).toFixed(0)}% match
                            </span>
                          )}
                        </div>
                        <h5 className="font-medium text-white truncate" title={patent.title}>
                          {patent.title}
                        </h5>
                        {patent.assignee && (
                          <p className="text-xs text-dark-400 mt-1">Assignee: {patent.assignee}</p>
                        )}
                        {patent.abstract && (
                          <p className="text-xs text-dark-300 mt-2 line-clamp-2">{patent.abstract}</p>
                        )}
                      </div>
                      {patent.url && (
                        <a
                          href={patent.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex-shrink-0 px-3 py-1.5 bg-primary-500/10 hover:bg-primary-500/20 text-primary-400 text-xs font-medium rounded-lg flex items-center gap-1 transition-colors"
                        >
                          <ExternalLink className="w-3 h-3" />
                          View Patent
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      );
    case 'market':
      return (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Market Intelligence</h3>
            <span className="text-dark-400">
              ${(report.market_intelligence.funding_total_usd / 1000000).toFixed(1)}M tracked
            </span>
          </div>
          <div className="p-4 bg-dark-800/50 rounded-lg">
            <h4 className="text-sm text-dark-400 mb-3">Relevant Startups</h4>
            <div className="space-y-3">
              {report.market_intelligence.relevant_startups.slice(0, 5).map((startup: any, index: number) => (
                <div key={index} className="flex items-center justify-between p-3 bg-dark-700/50 rounded-lg">
                  <div>
                    <p className="font-medium text-white">{startup.name}</p>
                    <p className="text-xs text-dark-400">{startup.description}</p>
                  </div>
                  {startup.funding_total && (
                    <span className="text-green-400 font-semibold">
                      ${(startup.funding_total / 1000000).toFixed(1)}M
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      );
    case 'trends':
      return (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Technology Trends</h3>
            <span className="text-dark-400">{report.tech_trends.total_papers_analyzed} papers analyzed</span>
          </div>
          <div className="space-y-4">
            {report.tech_trends.trends.slice(0, 4).map((trend: any, index: number) => (
              <div key={index} className="p-4 bg-dark-800/50 rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-medium text-white">{trend.technology_name}</h4>
                  <span className={`px-2 py-0.5 text-xs rounded-full ${
                    trend.maturity_level === 'emerging' ? 'bg-cyan-500/20 text-cyan-400' :
                    trend.maturity_level === 'growing' ? 'bg-green-500/20 text-green-400' :
                    'bg-dark-600 text-dark-300'
                  }`}>
                    {trend.maturity_level}
                  </span>
                </div>
                <p className="text-sm text-dark-300">{trend.description}</p>
                <div className="mt-2 flex items-center gap-4">
                  <span className="text-xs text-dark-400">TRL: {trend.trl_level}/9</span>
                  <span className="text-xs text-dark-400">Momentum: {(trend.research_momentum * 100).toFixed(0)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      );
    case 'verification':
      return (
        <div className="space-y-6">
          <div className="flex items-center gap-4 p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
            <Shield className="w-8 h-8 text-green-400" />
            <div>
              <h3 className="font-semibold text-white">Epistemic Verification Complete</h3>
              <p className="text-sm text-dark-300">
                All claims verified across {report.verification_report.total_sources_used} independent sources
              </p>
            </div>
            <div className="ml-auto text-right">
              <p className="text-2xl font-bold text-green-400">
                {(report.verification_report.average_confidence * 100).toFixed(0)}%
              </p>
              <p className="text-xs text-dark-400">Average Confidence</p>
            </div>
          </div>
        </div>
      );
    default:
      return null;
  }
}

function StatusIndicator({ status }: { status: 'idle' | 'running' | 'completed' | 'error' }) {
  const styles: Record<string, string> = {
    idle: 'bg-dark-500',
    running: 'bg-cyan-400 animate-pulse shadow-lg shadow-cyan-400/50',
    completed: 'bg-green-400 shadow-lg shadow-green-400/50',
    error: 'bg-red-400 shadow-lg shadow-red-400/50',
  };

  return <div className={`w-3 h-3 rounded-full ${styles[status]}`} />;
}

function StatCard({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  color: string;
}) {
  const colorClasses: Record<string, string> = {
    cyan: 'text-cyan-400 bg-cyan-400/10',
    purple: 'text-purple-400 bg-purple-400/10',
    pink: 'text-pink-400 bg-pink-400/10',
    green: 'text-green-400 bg-green-400/10',
  };

  return (
    <div className="p-4 bg-dark-800/50 rounded-xl">
      <div className={`w-10 h-10 rounded-lg ${colorClasses[color]} flex items-center justify-center mb-3`}>
        {icon}
      </div>
      <p className="text-2xl font-bold text-white">{value}</p>
      <p className="text-sm text-dark-400">{label}</p>
    </div>
  );
}

function generateDemoReport(query: string): ResearchReport {
  return {
    report_id: `IOR-${Date.now()}`,
    executive_summary: {
      headline: `Strategic Innovation Opportunities in ${query}`,
      key_finding: `Analysis reveals 5 high-potential whitespace opportunities with strong patent protection potential and growing market demand. The sector shows $2.3B in recent funding with accelerating research momentum.`,
      top_opportunities: [
        'Next-generation materials integration opportunity',
        'AI-enhanced process optimization gap',
        'Sustainability-focused product differentiation',
      ],
      overall_confidence: 0.87,
    },
    whitespace_opportunities: [
      {
        title: 'AI-Integrated Process Control',
        description: 'Gap identified in applying machine learning to real-time process optimization in this domain. Early patent landscape with high commercial potential.',
        opportunity_type: 'technology_gap',
        confidence_score: 0.92,
        potential_impact: 'high',
        recommended_actions: ['File provisional patents', 'Build POC', 'Partner with AI labs'],
      },
      {
        title: 'Sustainable Manufacturing Methods',
        description: 'Growing regulatory pressure and consumer demand creates opportunity for eco-friendly alternatives. Limited IP coverage currently.',
        opportunity_type: 'market_gap',
        confidence_score: 0.85,
        potential_impact: 'high',
        recommended_actions: ['Conduct LCA studies', 'Develop green processes', 'Pursue certifications'],
      },
      {
        title: 'IoT-Enabled Monitoring Solutions',
        description: 'Industry lacking connected device solutions for real-time monitoring and predictive maintenance.',
        opportunity_type: 'technology_gap',
        confidence_score: 0.78,
        potential_impact: 'medium',
        recommended_actions: ['Develop sensor integrations', 'Build data platform', 'Create analytics dashboards'],
      },
      {
        title: 'Advanced Materials Application',
        description: 'Novel materials research shows promising results but limited commercial applications identified.',
        opportunity_type: 'research_commercialization',
        confidence_score: 0.73,
        potential_impact: 'medium',
        recommended_actions: ['Partner with universities', 'Conduct pilot studies', 'Assess manufacturing scalability'],
      },
    ],
    patent_landscape: {
      total_patents: 847,
      top_assignees: {
        'Tech Innovation Corp': 45,
        'Global Research Inc': 38,
        'Advanced Systems Ltd': 32,
        'Future Technologies': 28,
        'Smart Solutions GmbH': 24,
      },
    },
    market_intelligence: {
      funding_total_usd: 2340000000,
      relevant_startups: [
        { name: 'InnovateTech', description: 'AI-powered optimization platform', funding_total: 45000000 },
        { name: 'GreenSolutions', description: 'Sustainable process technologies', funding_total: 32000000 },
        { name: 'DataDriven Labs', description: 'Industrial IoT solutions', funding_total: 28000000 },
        { name: 'NextGen Materials', description: 'Advanced materials R&D', funding_total: 21000000 },
        { name: 'SmartFactory AI', description: 'Manufacturing intelligence', funding_total: 18000000 },
      ],
    },
    tech_trends: {
      total_papers_analyzed: 312,
      trends: [
        { technology_name: 'Machine Learning Integration', description: 'AI/ML being applied to domain processes', maturity_level: 'growing', trl_level: 6, research_momentum: 0.89 },
        { technology_name: 'Sustainable Processes', description: 'Eco-friendly manufacturing methods', maturity_level: 'emerging', trl_level: 4, research_momentum: 0.76 },
        { technology_name: 'IoT Connectivity', description: 'Connected sensors and monitoring', maturity_level: 'growing', trl_level: 7, research_momentum: 0.68 },
        { technology_name: 'Advanced Materials', description: 'Novel material applications', maturity_level: 'emerging', trl_level: 3, research_momentum: 0.82 },
      ],
    },
    verification_report: {
      average_confidence: 0.84,
      total_sources_used: 156,
    },
    metadata: {
      processing_time_seconds: 47.3,
      total_sources_analyzed: 1315,
    },
  };
}
