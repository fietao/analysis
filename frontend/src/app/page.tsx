import React from 'react';
import { TrendingUp, ArrowUpRight, ArrowDownRight, Activity } from 'lucide-react';

export default function Dashboard() {
  const stats = [
    { label: 'NASDAQ 100 Coverage', value: '100 Stocks', icon: Activity, trend: '+5% this month' },
    { label: 'Avg. Profit Margin', value: '18.4%', icon: TrendingUp, trend: '+1.2%', trendUp: true },
  ];

  return (
    <div className="space-y-10 animate-in fade-in duration-500">
      <header className="flex flex-col space-y-2">
        <h1 className="text-4xl font-extrabold tracking-tight">Market Dashboard</h1>
        <p className="text-muted-foreground text-lg">Real-time analysis from your premium Jarvis engine.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, i) => (
          <div key={i} className="glass-card p-6 rounded-2xl glow-shadow space-y-4">
            <div className="flex justify-between items-start">
              <div className="p-3 bg-secondary rounded-xl">
                <stat.icon className="w-6 h-6 text-primary" />
              </div>
              {stat.trendUp !== undefined && (
                <div className={`flex items-center text-xs font-bold px-2 py-1 rounded-full ${stat.trendUp ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>
                  {stat.trendUp ? <ArrowUpRight className="w-3 h-3 mr-1" /> : <ArrowDownRight className="w-3 h-3 mr-1" />}
                  {stat.trend}
                </div>
              )}
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">{stat.label}</p>
              <h3 className="text-3xl font-bold mt-1">{stat.value}</h3>
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
