"use client";
import React, { useEffect, useState } from 'react';
import { TrendingUp, ArrowUpRight, ArrowDownRight, Activity, RefreshCw, Zap } from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface DashboardStats {
  ticker_count: number;
  screening_available: boolean;
  screening_ticker_count: number;
  avg_1y_return_pct: number | null;
  last_updated: string | null;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/dashboard`);
        if (!res.ok) throw new Error('Failed to load dashboard');
        const data = await res.json();
        setStats(data);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const statCards = stats
    ? [
        { label: 'NASDAQ 100 Coverage', value: `${stats.ticker_count} Stocks`, icon: Activity },
        {
          label: 'Avg. 1Y Return (screened)',
          value: stats.avg_1y_return_pct != null ? `${stats.avg_1y_return_pct}%` : '—',
          icon: TrendingUp,
          trend: stats.avg_1y_return_pct != null ? (stats.avg_1y_return_pct >= 0 ? 'Live' : 'Live') : 'Run screener',
          trendUp: stats.avg_1y_return_pct != null && stats.avg_1y_return_pct >= 0,
        },
        {
          label: 'Screening (live)',
          value: stats.screening_available ? `${stats.screening_ticker_count} tickers` : 'Not run',
          icon: Zap,
          trend: stats.last_updated ? 'Updated' : '',
        },
      ]
    : [
        { label: 'NASDAQ 100 Coverage', value: '—', icon: Activity },
        { label: 'Avg. 1Y Return', value: '—', icon: TrendingUp },
        { label: 'Screening', value: '—', icon: Zap },
      ];

  return (
    <div className="space-y-10 animate-in fade-in duration-500">
      <header className="flex flex-col space-y-2">
        <h1 className="text-4xl font-extrabold tracking-tight">Market Dashboard</h1>
        <p className="text-muted-foreground text-lg flex items-center gap-2">
          Live data from your Jarvis engine.
          {stats?.last_updated && (
            <span className="text-xs font-medium text-muted-foreground/80 flex items-center gap-1">
              <RefreshCw className="w-3 h-3" /> Last refresh: {new Date(stats.last_updated).toLocaleString()}
            </span>
          )}
        </p>
      </header>

      {error && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-600 text-sm">
          Cannot reach API: {error}. Start the backend with <code className="bg-black/20 px-1 rounded">python api.py</code>.
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, i) => (
          <div key={i} className="glass-card p-6 rounded-2xl glow-shadow space-y-4">
            <div className="flex justify-between items-start">
              <div className="p-3 bg-secondary rounded-xl">
                <stat.icon className="w-6 h-6 text-primary" />
              </div>
              {stat.trend !== undefined && stat.trend && (
                <div className={`flex items-center text-xs font-bold px-2 py-1 rounded-full ${stat.trendUp ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>
                  {stat.trendUp === true ? <ArrowUpRight className="w-3 h-3 mr-1" /> : stat.trendUp === false ? <ArrowDownRight className="w-3 h-3 mr-1" /> : null}
                  {stat.trend}
                </div>
              )}
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
              <h3 className="text-3xl font-bold mt-1">{loading ? '…' : stat.value}</h3>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 glass-card rounded-3xl p-8 min-h-[400px] flex flex-col justify-center items-center text-center space-y-4">
          <div className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center">
            <Activity className="w-8 h-8 text-muted-foreground animate-pulse" />
          </div>
          <h2 className="text-2xl font-bold">Interactive Charts (Phase 10)</h2>
          <p className="text-muted-foreground max-w-md italic">Recharts integration is coming in the next phase to bring your stock data to life.</p>
        </div>

        <div className="glass-card rounded-3xl p-8 space-y-6">
          <h2 className="text-xl font-bold">Quick Insights</h2>
          <div className="space-y-4">
            {[1, 2, 3].map((_, i) => (
              <div key={i} className="flex space-x-4 p-4 rounded-xl bg-secondary/50 border border-border/50">
                <div className="w-2 h-2 rounded-full bg-primary mt-2" />
                <div className="space-y-1">
                  <div className="h-4 w-32 bg-muted rounded-md animate-pulse" />
                  <div className="h-3 w-48 bg-muted/50 rounded-md animate-pulse" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
