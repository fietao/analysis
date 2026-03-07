"use client";
import React, { useEffect, useState } from 'react';
import {
    TrendingUp,
    ArrowUpRight,
    ArrowDownRight,
    Search,
    Download,
    Filter,
    Activity,
    BarChart3,
    RefreshCw
} from 'lucide-react';
import Link from 'next/link';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface StockMetric {
    ticker: string;
    "1Y Return": number;
    "Volatility": number;
    "Max Drawdown": number;
    market_cap?: number;
    forward_pe?: number;
    dividend_yield?: number;
    profit_margins?: number;
    revenue_growth?: number;
    "Market Cap (B)"?: number;
    "Forward PE"?: number;
    "Div Yield"?: number;
    "Profit Margin"?: number;
    "Rev Growth"?: number;
}

export default function ScreenerPage() {
    const [data, setData] = useState<StockMetric[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [sortConfig, setSortConfig] = useState<{ key: keyof StockMetric; direction: 'asc' | 'desc' }>({
        key: '1Y Return',
        direction: 'desc'
    });
    const [searchQuery, setSearchQuery] = useState('');
    const [refreshing, setRefreshing] = useState(false);

    useEffect(() => {
        fetchScreenerData();
    }, []);

    const fetchScreenerData = async () => {
        try {
            setError(null);
            const response = await fetch(`${API_BASE}/api/screening`);
            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.detail || 'Failed to fetch screening data');
            }
            const result = await response.json();
            setData(result.results || []);
        } catch (err: any) {
            setError(err.message);
            setData([]);
        } finally {
            setLoading(false);
        }
    };

    const refreshWithLiveData = async () => {
        setRefreshing(true);
        setError(null);
        try {
            const response = await fetch(`${API_BASE}/api/screening/refresh`, { method: 'POST' });
            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.detail || 'Refresh failed');
            }
            const result = await response.json();
            setData(result.results || []);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setRefreshing(false);
        }
    };

    const handleSort = (key: keyof StockMetric) => {
        let direction: 'asc' | 'desc' = 'desc';
        if (sortConfig.key === key && sortConfig.direction === 'desc') {
            direction = 'asc';
        }
        setSortConfig({ key, direction });
    };

    const sortedData = [...data].sort((a, b) => {
        const valA = a[sortConfig.key] ?? 0;
        const valB = b[sortConfig.key] ?? 0;
        if (valA < valB) return sortConfig.direction === 'asc' ? -1 : 1;
        if (valA > valB) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
    }).filter(item =>
        item.ticker.toLowerCase().includes(searchQuery.toLowerCase())
    );

    if (loading && data.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
                <Activity className="w-12 h-12 text-primary animate-spin" />
                <p className="text-lg font-bold tracking-widest text-primary animate-pulse">LOADING...</p>
                <p className="text-sm text-muted-foreground">No screening data yet? Click &quot;Refresh with live data&quot; on the Screener to fetch.</p>
            </div>
        );
    }

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <header className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                <div>
                    <h1 className="text-4xl font-extrabold tracking-tight">Market Screener</h1>
                    <p className="text-muted-foreground text-lg">Batch performance discovery across NAS100.</p>
                </div>

                <div className="flex flex-wrap items-center gap-4">
                    <button
                        onClick={refreshWithLiveData}
                        disabled={refreshing}
                        className="flex items-center space-x-2 px-4 py-2.5 bg-emerald-600 text-white rounded-xl font-bold hover:bg-emerald-500 disabled:opacity-50 transition-all"
                    >
                        <RefreshCw size={18} className={refreshing ? 'animate-spin' : ''} />
                        <span>{refreshing ? 'Fetching live data…' : 'Refresh with live data'}</span>
                    </button>
                    <div className="relative group">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                        <input
                            type="text"
                            placeholder="Filter by ticker..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="pl-10 pr-4 py-2.5 bg-secondary/50 border border-border rounded-xl focus:outline-none focus:ring-2 focus:ring-primary/50 w-full sm:w-64 transition-all"
                        />
                    </div>
                    <button className="flex items-center space-x-2 px-4 py-2.5 bg-secondary border border-border rounded-xl font-bold hover:bg-secondary/80 transition-all">
                        <Filter size={18} />
                        <span>Advanced Filters</span>
                    </button>
                    <button className="flex items-center space-x-2 px-4 py-2.5 bg-primary text-primary-foreground rounded-xl font-bold hover:shadow-lg hover:shadow-primary/20 transition-all">
                        <Download size={18} />
                        <span>Export CSV</span>
                    </button>
                </div>
            </header>

            {error && (
                <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-700 dark:text-amber-400 text-sm flex flex-wrap items-center justify-between gap-4">
                    <span>{error}</span>
                    <button
                        onClick={refreshWithLiveData}
                        disabled={refreshing}
                        className="flex items-center space-x-2 px-4 py-2 bg-emerald-600 text-white rounded-lg font-bold hover:bg-emerald-500 disabled:opacity-50"
                    >
                        <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
                        {refreshing ? 'Fetching…' : 'Refresh with live data'}
                    </button>
                </div>
            )}

            {/* Top Performers Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {data.sort((a, b) => ((b["1Y Return"] ?? 0) - (a["1Y Return"] ?? 0))).slice(0, 3).map((stock, i) => (
                    <Link key={stock.ticker} href={`/analytics?ticker=${stock.ticker}`}>
                        <div className={`glass-card p-6 rounded-3xl border-l-4 ${i === 0 ? 'border-emerald-500' : 'border-primary/50'} hover:scale-[1.02] transition-all cursor-pointer group`}>
                            <div className="flex justify-between items-center mb-4">
                                <span className="px-3 py-1 bg-secondary rounded-lg font-black text-sm">{stock.ticker}</span>
                                <span className="text-emerald-500 flex items-center text-sm font-bold">
                                    <ArrowUpRight size={14} className="mr-1" />
                                    Top Performer
                                </span>
                            </div>
                            <h4 className="text-3xl font-black">{(stock["1Y Return"] * 100).toFixed(1)}%</h4>
                            <p className="text-xs font-bold text-muted-foreground uppercase tracking-widest mt-1">1-Year Return</p>
                        </div>
                    </Link>
                ))}
            </div>

            {/* Main Table */}
            <div className="glass-card rounded-3xl overflow-hidden border border-border/50 shadow-2xl">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-secondary/30 border-b border-border">
                                <th className="p-5 font-black uppercase tracking-widest text-xs text-muted-foreground">Ticker</th>
                                <SortableHeader label="1Y Return" field="1Y Return" currentSort={sortConfig} onSort={handleSort} />
                                <SortableHeader label="Volatility" field="Volatility" currentSort={sortConfig} onSort={handleSort} />
                                <SortableHeader label="Drawdown" field="Max Drawdown" currentSort={sortConfig} onSort={handleSort} />
                                <th className="p-5 font-black uppercase tracking-widest text-xs text-muted-foreground text-right">Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {sortedData.map((stock) => (
                                <tr key={stock.ticker} className="border-b border-border/50 hover:bg-secondary/20 transition-colors group">
                                    <td className="p-5">
                                        <div className="flex items-center space-x-3">
                                            <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center font-black text-primary text-xs">
                                                {stock.ticker[0]}
                                            </div>
                                            <span className="font-bold">{stock.ticker}</span>
                                        </div>
                                    </td>
                                    <td className="p-5">
                                        <span className={`font-mono font-bold ${stock["1Y Return"] >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
                                            {stock["1Y Return"] >= 0 ? '+' : ''}{(stock["1Y Return"] * 100).toFixed(2)}%
                                        </span>
                                    </td>
                                    <td className="p-5 font-mono text-muted-foreground">
                                        {(stock["Volatility"] * 100).toFixed(2)}%
                                    </td>
                                    <td className="p-5 font-mono text-rose-500/80">
                                        {(stock["Max Drawdown"] * 100).toFixed(2)}%
                                    </td>
                                    <td className="p-5 text-right">
                                        <Link href={`/analytics?ticker=${stock.ticker}`}>
                                            <button className="px-4 py-1.5 bg-secondary group-hover:bg-primary group-hover:text-primary-foreground rounded-lg text-xs font-black uppercase tracking-wider transition-all">
                                                Analyze
                                            </button>
                                        </Link>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

function SortableHeader({ label, field, currentSort, onSort }: any) {
    const isActive = currentSort.key === field;
    return (
        <th
            className="p-5 cursor-pointer hover:text-primary transition-colors group"
            onClick={() => onSort(field)}
        >
            <div className="flex items-center space-x-2">
                <span className={`font-black uppercase tracking-widest text-xs ${isActive ? 'text-primary' : 'text-muted-foreground'}`}>
                    {label}
                </span>
                <div className={`flex flex-col transition-opacity ${isActive ? 'opacity-100' : 'opacity-0 group-hover:opacity-40'}`}>
                    <TrendingUp size={10} className={`${isActive && currentSort.direction === 'asc' ? 'text-primary' : ''}`} />
                </div>
            </div>
        </th>
    );
}
