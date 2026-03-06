"use client";
import React, { useEffect, useState, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import {
    TrendingUp,
    Activity,
    ShieldCheck,
    AlertTriangle,
    ChevronLeft,
    RefreshCcw,
    Zap,
    BarChart3
} from 'lucide-react';

interface StockData {
    ticker: string;
    info: {
        name: string;
        sector?: string;
        industry?: string;
        market_cap?: number;
        forward_pe?: number;
        dividend_yield?: number;
        profit_margins?: number;
        revenue_growth?: number;
    };
    metrics: {
        "1Y Return": number;
        "Volatility": number;
        "Max Drawdown": number;
        "MA50": number;
        "MA200": number;
        insights: string[];
        [key: string]: any;
    };
}

function AnalyticsContent() {
    const searchParams = useSearchParams();
    const ticker = searchParams.get('ticker');
    const router = useRouter();

    const [data, setData] = useState<StockData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (ticker) {
            fetchData(ticker);
        }
    }, [ticker]);

    const fetchData = async (symbol: string) => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`http://localhost:8000/api/analysis/${symbol}`);
            if (!response.ok) {
                throw new Error(`Failed to fetch analysis for ${symbol}`);
            }
            const result = await response.json();
            setData(result);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    if (!ticker) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-6 animate-in fade-in duration-700">
                <div className="w-20 h-20 bg-secondary/50 rounded-3xl flex items-center justify-center">
                    <Activity className="w-10 h-10 text-muted-foreground animate-pulse" />
                </div>
                <div className="space-y-2">
                    <h2 className="text-3xl font-bold tracking-tight">No Ticker Selected</h2>
                    <p className="text-muted-foreground max-w-sm mx-auto">
                        Search for a NASDAQ 100 stock ticker in the top navigation bar to begin deep-dive intelligence analysis.
                    </p>
                </div>
                <button
                    onClick={() => router.push('/')}
                    className="px-6 py-2.5 bg-primary text-primary-foreground font-bold rounded-xl shadow-lg hover:shadow-primary/20 transition-all active:scale-95"
                >
                    Back to Home
                </button>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
                <div className="relative">
                    <div className="w-16 h-16 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
                    <Zap className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-6 h-6 text-primary animate-pulse" />
                </div>
                <p className="text-lg font-bold animate-pulse text-primary tracking-widest uppercase">Initializing Jarvis Engine...</p>
            </div>
        );
    }

    if (error || !data) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] text-center space-y-4">
                <div className="w-16 h-16 bg-rose-500/10 rounded-2xl flex items-center justify-center">
                    <AlertTriangle className="w-8 h-8 text-rose-500" />
                </div>
                <div>
                    <h2 className="text-2xl font-bold text-rose-500">Analysis Failed</h2>
                    <p className="text-muted-foreground">{error || "Could not retrieve data for this ticker."}</p>
                </div>
                <button
                    onClick={() => fetchData(ticker)}
                    className="flex items-center space-x-2 px-6 py-2 bg-secondary rounded-xl font-bold hover:bg-secondary/80 transition-all"
                >
                    <RefreshCcw size={18} />
                    <span>Retry Analysis</span>
                </button>
            </div>
        );
    }

    const { info, metrics } = data;

    return (
        <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            {/* Header Section */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div className="space-y-2">
                    <button
                        onClick={() => router.push('/')}
                        className="flex items-center space-x-2 text-sm font-bold text-muted-foreground hover:text-primary transition-colors mb-2"
                    >
                        <ChevronLeft size={16} />
                        <span>Dashboard</span>
                    </button>
                    <div className="flex items-center space-x-4">
                        <div className="w-14 h-14 bg-primary text-primary-foreground flex items-center justify-center rounded-2xl text-2xl font-black shadow-lg">
                            {data.ticker[0]}
                        </div>
                        <div>
                            <h1 className="text-4xl font-extrabold tracking-tight flex items-center gap-3">
                                {info.name}
                                <span className="text-xl font-medium text-muted-foreground bg-secondary/50 px-3 py-1 rounded-lg border border-border/50">
                                    {data.ticker}
                                </span>
                            </h1>
                            <p className="text-muted-foreground font-medium flex items-center gap-2 mt-1">
                                {info.sector} • {info.industry}
                            </p>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-3 bg-card p-2 rounded-2xl border border-border shadow-sm">
                    <div className="px-4 py-2 text-center">
                        <p className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold font-mono">Market Cap</p>
                        <p className="text-lg font-black">${((info.market_cap || 0) / 1e9).toFixed(2)}B</p>
                    </div>
                    <div className="w-px h-8 bg-border" />
                    <div className="px-4 py-2 text-center">
                        <p className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold font-mono">Forward PE</p>
                        <p className="text-lg font-black">{info.forward_pe?.toFixed(2) || 'N/A'}</p>
                    </div>
                </div>
            </div>

            {/* Metric Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <MetricCard
                    label="1Y Total Return"
                    value={(metrics["1Y Return"] * 100).toFixed(2) + "%"}
                    icon={TrendingUp}
                    description="Stock performance over last 12 months"
                    trend={metrics["1Y Return"] > 0 ? "bullish" : "bearish"}
                />
                <MetricCard
                    label="Annualized Volatility"
                    value={(metrics["Volatility"] * 100).toFixed(2) + "%"}
                    icon={Activity}
                    description="Risk measurement based on historical volatility"
                    variant="risk"
                />
                <MetricCard
                    label="Max Drawdown"
                    value={(metrics["Max Drawdown"] * 100).toFixed(2) + "%"}
                    icon={ShieldCheck}
                    description="Peak-to-trough decline over the period"
                    variant="risk"
                />
                <MetricCard
                    label="Profit Margin"
                    value={(info.profit_margins ? (info.profit_margins * 100).toFixed(2) + "%" : "N/A")}
                    icon={BarChart3}
                    description="The percentage of revenue that is profit"
                    variant="finance"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Placeholder for Charts */}
                <div className="lg:col-span-2 glass-card rounded-3xl p-8 border-2 border-dashed border-border/50 flex flex-col justify-center items-center text-center space-y-4 min-h-[450px]">
                    <div className="w-20 h-20 bg-secondary rounded-full flex items-center justify-center">
                        <Activity className="w-10 h-10 text-muted-foreground/30" />
                    </div>
                    <h3 className="text-2xl font-bold opacity-40 uppercase tracking-widest">Recharts Analysis Hub</h3>
                    <p className="text-muted-foreground max-w-sm italic">
                        Interactive technical analysis and benchmarking modules will be initialized in Phase 10.
                    </p>
                </div>

                {/* Analyst Notes Section */}
                <div className="glass-card rounded-3xl p-8 space-y-8 flex flex-col glow-shadow border border-white/5">
                    <div className="flex items-center space-x-3 pb-4 border-b border-border/50">
                        <div className="p-2 bg-primary/10 rounded-lg">
                            <BarChart3 className="w-6 h-6 text-primary" />
                        </div>
                        <h3 className="text-xl font-extrabold tracking-tight uppercase">Analyst Insights</h3>
                    </div>

                    <div className="space-y-6 flex-1">
                        {metrics.insights.map((insight, idx) => (
                            <div key={idx} className="flex gap-4 group p-1 transition-all">
                                <div className="mt-1.5 min-w-[20px] h-5 w-5 bg-primary/20 rounded-full flex items-center justify-center group-hover:bg-primary transition-colors">
                                    <div className="w-1.5 h-1.5 bg-primary group-hover:bg-primary-foreground rounded-full" />
                                </div>
                                <p className="text-sm font-medium leading-relaxed text-foreground/90 group-hover:text-foreground transition-colors">
                                    {insight}
                                </p>
                            </div>
                        ))}
                    </div>

                    <div className="mt-auto p-5 rounded-2xl bg-secondary/30 border border-border/50">
                        <div className="flex items-center gap-2 mb-2 text-xs font-black uppercase tracking-widest text-muted-foreground">
                            <ShieldCheck size={14} className="text-emerald-500" />
                            Technical Sentiment
                        </div>
                        <div className="flex justify-between items-end">
                            <div>
                                <p className="text-sm font-bold">50-Day MA: <span className="font-mono ml-2">${metrics.MA50.toFixed(2)}</span></p>
                                <p className="text-sm font-bold">200-Day MA: <span className="font-mono ml-2">${metrics.MA200.toFixed(2)}</span></p>
                            </div>
                            <div className={`px-3 py-1 rounded-md text-[10px] font-black uppercase tracking-widest ${metrics.MA50 > metrics.MA200 ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>
                                {metrics.MA50 > metrics.MA200 ? 'Golden Cross' : 'Bearish Trend'}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function MetricCard({ label, value, icon: Icon, description, trend, variant }: any) {
    let accentClass = "bg-primary/10 text-primary";
    if (variant === 'risk') accentClass = "bg-rose-500/10 text-rose-500";
    if (variant === 'finance') accentClass = "bg-emerald-500/10 text-emerald-500";
    if (trend === 'bullish') accentClass = "bg-emerald-500/10 text-emerald-500";
    if (trend === 'bearish') accentClass = "bg-rose-500/10 text-rose-500";

    return (
        <div className="glass-card p-6 rounded-3xl glow-shadow space-y-4 hover:border-primary/20 transition-all group">
            <div className="flex justify-between items-start">
                <div className={`p-3 rounded-2xl ${accentClass} transition-all group-hover:scale-110 shadow-sm`}>
                    <Icon className="w-6 h-6" />
                </div>
                {trend && (
                    <div className={`px-2 py-1 rounded-lg text-[10px] font-black uppercase tracking-wider ${trend === 'bullish' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>
                        {trend}
                    </div>
                )}
            </div>
            <div>
                <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground">{label}</p>
                <h3 className="text-3xl font-black mt-1 tracking-tight">{value}</h3>
                <p className="text-xs font-medium text-muted-foreground/70 mt-3 italic line-clamp-1">{description}</p>
            </div>
        </div>
    );
}

export default function AnalyticsPage() {
    return (
        <Suspense fallback={
            <div className="flex items-center justify-center min-h-[60vh]">
                <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
            </div>
        }>
            <AnalyticsContent />
        </Suspense>
    );
}
