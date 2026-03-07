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
    BarChart3,
    Calendar,
    Target,
    Scale,
    DollarSign
} from 'lucide-react';
import {
    ResponsiveContainer,
    AreaChart,
    Area,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    Legend,
    CartesianGrid,
    ComposedChart,
    Line,
    Cell,
} from 'recharts';

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
        "1Y_total_return": number;
        "volatility": number;
        "max_drawdown": number;
        "MA50": number;
        "MA200": number;
        insights: string[];
        [key: string]: any;
    };
}

interface ChartPoint {
    Date: string;
    Close: number;
}

interface FinancialTrend {
    year: string;
    revenue: number;
    net_income: number;
    roic?: number;
    wacc?: number;
}

function AnalyticsContent() {
    const searchParams = useSearchParams();
    const ticker = searchParams.get('ticker');
    const router = useRouter();

    const [data, setData] = useState<StockData | null>(null);
    const [chartData, setChartData] = useState<ChartPoint[]>([]);
    const [financialTrends, setFinancialTrends] = useState<FinancialTrend[]>([]);
    const [financialRedFlags, setFinancialRedFlags] = useState<any[]>([]);
    const [valuation, setValuation] = useState<any | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    useEffect(() => {
        if (ticker) {
            fetchData(ticker, false);
            fetchChartData(ticker, false);
            fetchFinancials(ticker);
        }
    }, [ticker]);

    const fetchData = async (symbol: string, forceRefresh = false) => {
        setLoading(true);
        setError(null);
        try {
            const url = `${API_BASE}/api/analysis/${symbol}${forceRefresh ? '?refresh=true' : ''}`;
            const response = await fetch(url);
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

    const fetchChartData = async (symbol: string, forceRefresh = false) => {
        try {
            const url = `${API_BASE}/api/historical/${symbol}${forceRefresh ? '?refresh=true' : ''}`;
            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to fetch chart data');
            const result = await response.json();
            setChartData(result.data);
        } catch (err) {
            console.error("Chart fetch error:", err);
        }
    };

    const fetchFinancials = async (symbol: string) => {
        try {
            const response = await fetch(`${API_BASE}/api/financials/${symbol}`);
            if (!response.ok) throw new Error('Failed to fetch financials');
            const result = await response.json();
            setFinancialTrends(result.trends);
            setFinancialRedFlags(result.red_flags || []);
            setValuation(result.valuation || null);
        } catch (err) {
            console.error("Financials fetch error:", err);
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
                    onClick={() => { fetchData(ticker, true); fetchChartData(ticker, true); }}
                    className="flex items-center space-x-2 px-6 py-2 bg-secondary rounded-xl font-bold hover:bg-secondary/80 transition-all"
                >
                    <RefreshCcw size={18} />
                    <span>Retry with live data</span>
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
                    <div className="flex items-center gap-2 mb-2">
                        <button
                            onClick={() => router.push('/')}
                            className="flex items-center space-x-2 text-sm font-bold text-muted-foreground hover:text-primary transition-colors"
                        >
                            <ChevronLeft size={16} />
                            <span>Dashboard</span>
                        </button>
                        <button
                            onClick={() => { fetchData(ticker!, true); fetchChartData(ticker!, true); }}
                            className="flex items-center space-x-2 text-sm font-bold text-muted-foreground hover:text-primary transition-colors px-2 py-1 rounded-lg hover:bg-secondary/50"
                            title="Fetch latest prices"
                        >
                            <RefreshCcw size={14} />
                            <span>Live data</span>
                        </button>
                    </div>
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
                    value={(metrics["1Y_total_return"] * 100).toFixed(2) + "%"}
                    icon={TrendingUp}
                    description="Stock performance over last 12 months"
                    trend={metrics["1Y_total_return"] > 0 ? "bullish" : "bearish"}
                />
                <MetricCard
                    label="Annualized Volatility"
                    value={(metrics["volatility"] * 100).toFixed(2) + "%"}
                    icon={Activity}
                    description="Risk measurement based on historical volatility"
                    variant="risk"
                />
                <MetricCard
                    label="Max Drawdown"
                    value={(metrics["max_drawdown"] * 100).toFixed(2) + "%"}
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
                <div className="lg:col-span-2 space-y-8">
                    {/* Interactive Price Chart */}
                    <div className="glass-card rounded-3xl p-8 glow-shadow h-[450px] flex flex-col space-y-6">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="p-2 bg-primary/10 rounded-lg">
                                    <TrendingUp className="w-5 h-5 text-primary" />
                                </div>
                                <h3 className="text-xl font-extrabold uppercase tracking-tight">Price Movement</h3>
                            </div>
                            <div className="flex items-center space-x-2 text-xs font-bold text-muted-foreground bg-secondary/50 px-3 py-1.5 rounded-full border border-border/50">
                                <Calendar size={14} />
                                <span>Last 200 Trading Days</span>
                            </div>
                        </div>

                        <div className="flex-1 w-full h-[300px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={chartData}>
                                    <defs>
                                        <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                                    <XAxis
                                        dataKey="Date"
                                        hide={true}
                                    />
                                    <YAxis
                                        domain={['auto', 'auto']}
                                        stroke="#a1a1aa"
                                        fontSize={12}
                                        fontWeight="bold"
                                        axisLine={false}
                                        tickLine={false}
                                        tickFormatter={(value) => `$${value}`}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            backgroundColor: '#18181b',
                                            border: '1px solid #27272a',
                                            borderRadius: '12px',
                                            boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)'
                                        }}
                                        itemStyle={{ color: '#10b981', fontWeight: '800' }}
                                        labelClassName="hidden"
                                        formatter={(value: any) => [`$${parseFloat(value).toFixed(2)}`, 'Closing Price']}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="Close"
                                        stroke="#10b981"
                                        strokeWidth={3}
                                        fillOpacity={1}
                                        fill="url(#colorPrice)"
                                        animationDuration={1500}
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Financial Growth Chart */}
                    <div className="glass-card rounded-3xl p-8 glow-shadow h-[450px] flex flex-col space-y-6 border border-white/5">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                                <div className="p-2 bg-emerald-500/10 rounded-lg">
                                    <BarChart3 className="w-5 h-5 text-emerald-500" />
                                </div>
                                <h3 className="text-xl font-extrabold uppercase tracking-tight">Growth Trajectory</h3>
                            </div>
                            <div className="text-xs font-bold text-muted-foreground bg-secondary/50 px-3 py-1.5 rounded-full border border-border/50 uppercase">
                                Annual Financials (SEC)
                            </div>
                        </div>

                        <div className="flex-1 w-full h-[300px]">
                            {financialTrends.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={financialTrends} margin={{ top: 20, right: 30, left: 10, bottom: 5 }}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                                        <XAxis dataKey="year" stroke="#a1a1aa" fontSize={12} fontWeight="bold" axisLine={false} tickLine={false} />
                                        <YAxis
                                            stroke="#a1a1aa"
                                            fontSize={10}
                                            fontWeight="bold"
                                            axisLine={false}
                                            tickLine={false}
                                            tickFormatter={(value) => `$${(value / 1e9).toFixed(0)}B`}
                                        />
                                        <Tooltip
                                            cursor={{ fill: '#27272a', opacity: 0.4 }}
                                            contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '12px' }}
                                            formatter={(value: any) => [`$${(value / 1e9).toFixed(2)}B`, '']}
                                        />
                                        <Legend wrapperStyle={{ paddingTop: '20px', fontWeight: 'bold', fontSize: '10px', textTransform: 'uppercase' }} />
                                        <Bar dataKey="revenue" name="Revenue" fill="#10b981" radius={[4, 4, 0, 0]} barSize={40} />
                                        <Bar dataKey="net_income" name="Net Income" fill="#3b82f6" radius={[4, 4, 0, 0]} barSize={40} />
                                    </BarChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="flex items-center justify-center h-full bg-secondary/20 rounded-2xl border border-dashed border-border/50">
                                    <span className="text-sm font-bold text-muted-foreground italic">No historical SEC data found for this ticker</span>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Value Creation (ROIC vs WACC) Chart */}
                <div className="glass-card rounded-3xl p-8 glow-shadow h-[450px] flex flex-col space-y-6 border border-white/5">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                            <div className="p-2 bg-blue-500/10 rounded-lg">
                                <Activity className="w-5 h-5 text-blue-500" />
                            </div>
                            <h3 className="text-xl font-extrabold uppercase tracking-tight">Value Creation (ROIC vs WACC)</h3>
                        </div>
                        <div className="text-xs font-bold text-muted-foreground bg-secondary/50 px-3 py-1.5 rounded-full border border-border/50 uppercase">
                            Profitability Spread
                        </div>
                    </div>

                    <div className="flex-1 w-full h-[300px]">
                        {financialTrends.length > 0 && financialTrends.some(t => typeof t.roic === 'number' && t.roic > 0) ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <ComposedChart data={financialTrends} margin={{ top: 20, right: 30, left: 10, bottom: 5 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                                    <XAxis dataKey="year" stroke="#a1a1aa" fontSize={12} fontWeight="bold" axisLine={false} tickLine={false} />
                                    <YAxis
                                        stroke="#a1a1aa"
                                        fontSize={10}
                                        fontWeight="bold"
                                        axisLine={false}
                                        tickLine={false}
                                        tickFormatter={(value) => `${value.toFixed(0)}%`}
                                    />
                                    <Tooltip
                                        cursor={{ fill: '#27272a', opacity: 0.4 }}
                                        contentStyle={{ backgroundColor: '#18181b', border: '1px solid #27272a', borderRadius: '12px' }}
                                        formatter={(value: any, name: string) => {
                                            return [`${parseFloat(value).toFixed(2)}%`, name.toUpperCase()];
                                        }}
                                    />
                                    <Legend wrapperStyle={{ paddingTop: '20px', fontWeight: 'bold', fontSize: '10px', textTransform: 'uppercase' }} />

                                    <Bar dataKey="roic" name="ROIC" radius={[4, 4, 0, 0]} barSize={40}>
                                        {
                                            financialTrends.map((entry, index) => {
                                                const isValueCreator = (entry.roic ?? 0) >= (entry.wacc ?? 0);
                                                return <Cell key={`cell-${index}`} fill={isValueCreator ? '#10b981' : '#f43f5e'} />;
                                            })
                                        }
                                    </Bar>
                                    <Line type="monotone" dataKey="wacc" name="Cost of Capital (WACC)" stroke="#fbbf24" strokeWidth={3} dot={{ r: 4, strokeWidth: 2 }} />
                                </ComposedChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="flex items-center justify-center h-full bg-secondary/20 rounded-2xl border border-dashed border-border/50">
                                <span className="text-sm font-bold text-muted-foreground italic">Insufficient balance sheet data to calculate ROIC</span>
                            </div>
                        )}
                    </div>
                </div>
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
                    {metrics.insights.map((insight: string, idx: number) => (
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

            {/* Advanced Valuation Section */}
            {valuation && (
                <div className="glass-card rounded-3xl p-8 glow-shadow space-y-6 border border-emerald-500/20">
                    <div className="flex items-center space-x-3 pb-4 border-b border-border/50">
                        <div className="p-2 bg-emerald-500/10 rounded-lg">
                            <Scale className="w-6 h-6 text-emerald-500" />
                        </div>
                        <div>
                            <h3 className="text-xl font-extrabold tracking-tight uppercase text-emerald-500">Intrinsic Value Analysis</h3>
                            <p className="text-xs font-bold text-muted-foreground mt-1 tracking-widest uppercase">Discounted Cash Flow (DCF) Model</p>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        <div className="p-5 rounded-2xl bg-secondary/30 border border-border/50 text-center">
                            <p className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold mb-1">Current Price</p>
                            <p className="text-2xl font-black">${valuation.current_price?.toFixed(2)}</p>
                        </div>
                        <div className="p-5 rounded-2xl bg-primary/10 border border-primary/20 text-center relative overflow-hidden group">
                            <div className="absolute inset-0 bg-primary/5 group-hover:bg-primary/10 transition-colors" />
                            <p className="text-[10px] uppercase tracking-widest text-primary font-bold mb-1 relative z-10">Intrinsic Value</p>
                            <p className="text-3xl font-black text-primary relative z-10">${valuation.intrinsic_value?.toFixed(2)}</p>
                        </div>
                        <div className={`p-5 rounded-2xl border text-center ${valuation.margin_of_safety > 0 ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500' : 'bg-rose-500/10 border-rose-500/20 text-rose-500'}`}>
                            <p className="text-[10px] uppercase tracking-widest font-bold mb-1">Margin of Safety</p>
                            <p className="text-2xl font-black">{(valuation.margin_of_safety * 100).toFixed(2)}%</p>
                            <p className="text-[9px] uppercase font-bold mt-1 opacity-80">{valuation.margin_of_safety > 0 ? 'Undervalued' : 'Overvalued'}</p>
                        </div>
                        <div className="p-5 rounded-2xl bg-secondary/30 border border-border/50 text-center text-left flex flex-col justify-center space-y-2">
                            <div className="flex justify-between items-center">
                                <span className="text-[10px] tracking-widest text-muted-foreground font-bold uppercase">WACC</span>
                                <span className="font-mono text-sm font-bold">{(valuation.wacc * 100).toFixed(2)}%</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-[10px] tracking-widest text-muted-foreground font-bold uppercase">Proj. Growth</span>
                                <span className="font-mono text-sm font-bold">{(valuation.projected_growth_rate * 100).toFixed(2)}%</span>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-[10px] tracking-widest text-muted-foreground font-bold uppercase">Term Growth</span>
                                <span className="font-mono text-sm font-bold">{(valuation.terminal_growth_rate * 100).toFixed(2)}%</span>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Red Flags Section */}
            <div className="lg:col-span-3 glass-card rounded-3xl p-8 glow-shadow border border-rose-500/20">
                <div className="flex items-center space-x-3 pb-6 border-b border-border/50">
                    <div className="p-2 bg-rose-500/10 rounded-lg">
                        <AlertTriangle className="w-6 h-6 text-rose-500" />
                    </div>
                    <div>
                        <h3 className="text-xl font-extrabold tracking-tight uppercase text-rose-500">Fundamental Red Flags</h3>
                        <p className="text-xs font-bold text-muted-foreground mt-1 tracking-widest uppercase">Automated SEC Detection</p>
                    </div>
                </div>
                <div className="pt-6 space-y-4">
                    {financialRedFlags.length > 0 ? (
                        financialRedFlags.map((flag, idx) => (
                            <div key={idx} className="flex gap-4 p-4 rounded-2xl bg-rose-500/5 hover:bg-rose-500/10 transition-colors border border-rose-500/10">
                                <div className={`mt-1 min-w-[32px] h-8 w-8 rounded-full flex items-center justify-center font-bold text-xs ${flag.severity === 'High' ? 'bg-rose-500 text-white shadow-[0_0_15px_rgba(244,63,94,0.5)]' : 'bg-orange-500/20 text-orange-500'}`}>
                                    !
                                </div>
                                <div>
                                    <h4 className="font-bold text-foreground">{flag.type}</h4>
                                    <p className="text-sm text-foreground/80 mt-1 leading-relaxed">{flag.description}</p>
                                </div>
                            </div>
                        ))
                    ) : (
                        <div className="flex flex-col items-center justify-center py-10 space-y-3 bg-emerald-500/5 rounded-2xl border border-dashed border-emerald-500/20">
                            <ShieldCheck className="w-10 h-10 text-emerald-500 opacity-50" />
                            <span className="text-sm font-bold text-emerald-500/80 uppercase tracking-widest">No Fundamental Anomalies Detected</span>
                        </div>
                    )}
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
