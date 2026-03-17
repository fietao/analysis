"use client";
import React, { useEffect, useState } from 'react';
import { TrendingUp, ArrowUpRight, ArrowDownRight, Activity, RefreshCw, Zap } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import Link from 'next/link';

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

  const [spyData, setSpyData] = useState<any[]>([]);
  const [topScreened, setTopScreened] = useState<any[]>([]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/dashboard`);
        if (!res.ok) throw new Error('Failed to load dashboard');
        const data = await res.json();
        setStats(data);

        // Fetch SPY Chart data sequentially to not block initial render excessively
        try {
          const resSpy = await fetch(`${API_BASE}/api/historical/SPY`);
          if (resSpy.ok) {
            const spyDataInfo = await resSpy.json();
            const formatted = spyDataInfo.data.map((d: any) => ({
              ...d,
              DateStr: new Date(d.Date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
            }));
            setSpyData(formatted);
          }
        } catch (e) {
          console.error("SPY data fetch error", e);
        }

        // Fetch Screening Data for top insights
        if (data.screening_available) {
          try {
            const resScreen = await fetch(`${API_BASE}/api/screening`);
            if (resScreen.ok) {
              const screenDataInfo = await resScreen.json();
              if (screenDataInfo.results && screenDataInfo.results.length > 0) {
                // Sort by 1Y Return descending
                const sorted = [...screenDataInfo.results].sort((a: any, b: any) => (b["1Y Return"] || 0) - (a["1Y Return"] || 0));
                setTopScreened(sorted.slice(0, 5));
              }
            }
          } catch (e) {
            console.error("Screening data fetch error", e);
          }
        }
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
        <div className="lg:col-span-2 glass-card rounded-3xl p-8 min-h-[400px] flex flex-col space-y-4 relative">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <Activity className="w-6 h-6 text-primary" />
              Market Benchmark (SPY)
            </h2>
            <div className="text-sm text-muted-foreground mr-4">Last 200 Days • Close Price</div>
          </div>

          {spyData.length > 0 ? (
            <div className="flex-1 w-full h-full min-h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={spyData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorSpy" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis
                    dataKey="DateStr"
                    stroke="#888888"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    minTickGap={30}
                  />
                  <YAxis
                    domain={['auto', 'auto']}
                    stroke="#888888"
                    fontSize={12}
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `$${value}`}
                  />
                  <Tooltip
                    contentStyle={{ backgroundColor: 'rgba(17, 24, 39, 0.8)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                    itemStyle={{ color: '#10b981' }}
                    labelStyle={{ color: '#9ca3af' }}
                    formatter={(value: any) => [`$${Number(value).toFixed(2)}`, 'Close']}
                  />
                  <Area type="monotone" dataKey="Close" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorSpy)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex-1 flex flex-col justify-center items-center text-center space-y-4">
              <div className="w-16 h-16 bg-secondary rounded-full flex items-center justify-center">
                <Activity className="w-8 h-8 text-muted-foreground animate-pulse" />
              </div>
              <p className="text-muted-foreground max-w-md italic">Loading market data...</p>
            </div>
          )}
        </div>

        <div className="glass-card rounded-3xl p-8 space-y-6 max-h-[450px] overflow-y-auto">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-bold">Top Performers</h2>
            <Link href="/screener" className="text-primary text-sm font-medium hover:underline">View All</Link>
          </div>
          <div className="space-y-4">
            {topScreened.length > 0 ? (
              topScreened.map((stock, i) => (
                <div key={i} className="flex space-x-4 p-4 rounded-xl bg-secondary/50 border border-border/50 hover:bg-secondary transition-colors group">
                  <div className="flex-1 flex justify-between items-center">
                    <div>
                      <Link href={`/analytics?ticker=${stock.ticker}`} className="text-lg font-bold group-hover:text-primary transition-colors">
                        {stock.ticker}
                      </Link>
                      <p className="text-sm text-muted-foreground truncate w-32">
                        {stock["1Y Return"] ? `${(stock["1Y Return"] * 100).toFixed(2)}% Return` : 'No Return Data'}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium">Vol: {stock["Volatility"] ? `${(stock["Volatility"] * 100).toFixed(1)}%` : '—'}</div>
                      <div className="text-xs text-muted-foreground mt-1 text-emerald-500 font-semibold">
                        Score: {stock.Score ? stock.Score.toFixed(1) : '—'}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              [1, 2, 3].map((_, i) => (
                <div key={i} className="flex space-x-4 p-4 rounded-xl bg-secondary/50 border border-border/50">
                  <div className="w-2 h-2 rounded-full bg-primary mt-2 flex-shrink-0" />
                  <div className="space-y-2 w-full">
                    <div className="h-4 w-1/2 bg-muted rounded-md animate-pulse" />
                    <div className="h-3 w-3/4 bg-muted/50 rounded-md animate-pulse" />
                  </div>
                </div>
              ))
            )}

            {!loading && topScreened.length === 0 && (
              <div className="text-center p-4">
                <p className="text-sm text-muted-foreground">Run the screener to see top performers here.</p>
                <Link href="/screener" className="mt-2 inline-block px-4 py-2 bg-primary/20 text-primary rounded-lg text-sm hover:bg-primary/30 transition-colors">
                  Go to Screener
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
