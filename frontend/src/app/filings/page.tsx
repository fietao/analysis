"use client";
import React, { useState } from 'react';
import {
    FileText,
    Upload,
    ShieldAlert,
    Search,
    Sparkles,
    BookOpen,
    ArrowRight
} from 'lucide-react';

export default function FilingsPage() {
    const [selectedFiling, setSelectedFiling] = useState<string | null>(null);

    const mockFilings = [
        { ticker: 'NVDA', type: '10-K', date: '2025-02-26', status: 'Analyzed' },
        { ticker: 'AAPL', type: '10-Q', date: '2025-02-01', status: 'Pending' },
        { ticker: 'TSLA', type: '10-K', date: '2025-01-29', status: 'Analyzed' },
    ];

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-top-4 duration-700">
            <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="space-y-2">
                    <h1 className="text-4xl font-extrabold tracking-tight flex items-center gap-3">
                        <FileText className="text-primary w-10 h-10" />
                        Document Intelligence
                    </h1>
                    <p className="text-muted-foreground text-lg">Elite SEC filing ingestion and automated risk extraction.</p>
                </div>

                <button className="flex items-center space-x-3 px-8 py-3.5 bg-primary text-primary-foreground rounded-2xl font-black shadow-lg shadow-primary/20 hover:scale-[1.02] transition-all">
                    <Upload size={20} />
                    <span>UPLOAD NEW FILING</span>
                </button>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                {/* Sidebar: Filing History */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="glass-card rounded-3xl p-6 glow-shadow border border-white/5">
                        <h3 className="font-black uppercase tracking-widest text-xs text-muted-foreground mb-4">Ingestion History</h3>
                        <div className="space-y-3">
                            {mockFilings.map((filing) => (
                                <div
                                    key={filing.ticker}
                                    onClick={() => setSelectedFiling(filing.ticker)}
                                    className={`p-4 rounded-2xl border transition-all cursor-pointer group ${selectedFiling === filing.ticker ? 'bg-primary/10 border-primary shadow-sm' : 'bg-secondary/40 border-border hover:border-primary/30'}`}
                                >
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="font-black text-lg">{filing.ticker}</span>
                                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${filing.status === 'Analyzed' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-amber-500/10 text-amber-500'}`}>
                                            {filing.status}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center text-xs text-muted-foreground font-medium">
                                        <span>{filing.type}</span>
                                        <span>{filing.date}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="glass-card rounded-3xl p-6 bg-gradient-to-br from-primary/10 to-transparent border border-primary/20">
                        <Sparkles className="text-primary w-6 h-6 mb-3" />
                        <h4 className="text-sm font-black mb-1 uppercase tracking-tight">AI Note Generation</h4>
                        <p className="text-xs text-muted-foreground leading-relaxed">
                            Upload a PDF to automatically generate a high-level risk summary and key management sentiment analysis using the Jarvis processor.
                        </p>
                    </div>
                </div>

                {/* Content Area: Viewer */}
                <div className="lg:col-span-3 space-y-8">
                    {selectedFiling ? (
                        <FilingViewer ticker={selectedFiling} />
                    ) : (
                        <div className="glass-card rounded-[40px] p-12 min-h-[600px] flex flex-col items-center justify-center text-center space-y-6 border-2 border-dashed border-border">
                            <div className="w-24 h-24 bg-secondary rounded-full flex items-center justify-center border border-border shadow-inner">
                                <BookOpen className="w-10 h-10 text-muted-foreground/40" />
                            </div>
                            <div className="space-y-2">
                                <h2 className="text-2xl font-bold opacity-50">Select a Document to Begin</h2>
                                <p className="text-muted-foreground max-w-sm italic">
                                    Choose an SEC filing from the history or upload a new 10-K/10-Q PDF for automated extraction.
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

function FilingViewer({ ticker }: { ticker: string }) {
    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="p-8 glass-card rounded-[40px] glow-shadow space-y-8 border border-white/5">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-border/50">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center font-black text-xl text-primary-foreground shadow-lg">
                            {ticker[0]}
                        </div>
                        <div>
                            <h2 className="text-2xl font-black tracking-tight">{ticker} Business Overview</h2>
                            <p className="text-sm font-medium text-muted-foreground">Form 10-K • Fiscal Year 2024</p>
                        </div>
                    </div>
                    <div className="flex gap-2">
                        <button className="px-4 py-2 bg-secondary rounded-xl text-xs font-black uppercase tracking-widest hover:bg-secondary/70 transition-all border border-border">View Source PDF</button>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="space-y-4">
                        <div className="flex items-center gap-2 text-rose-500">
                            <ShieldAlert size={18} />
                            <h3 className="text-sm font-black uppercase tracking-widest">Risk Factors (Section 1A)</h3>
                        </div>
                        <div className="p-6 bg-secondary/30 rounded-3xl border border-border/50 prose prose-invert max-w-none">
                            <p className="text-sm leading-relaxed text-muted-foreground/90 italic">
                                "We face intense competition in the markets in which we operate, including from both established and emerging competitors. If we are unable to compete effectively, our business, results of operations, and financial condition could be materially and adversely affected..."
                            </p>
                            <div className="mt-4 flex flex-wrap gap-2">
                                <span className="px-2 py-1 bg-rose-500/10 text-rose-500 text-[10px] font-bold rounded-md border border-rose-500/20">Market Competition</span>
                                <span className="px-2 py-1 bg-rose-500/10 text-rose-500 text-[10px] font-bold rounded-md border border-rose-500/20">Operational Risk</span>
                            </div>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div className="flex items-center gap-2 text-emerald-500">
                            <TrendingUp size={18} />
                            <h3 className="text-sm font-black uppercase tracking-widest">Management Discussion (MD&A)</h3>
                        </div>
                        <div className="p-6 bg-secondary/30 rounded-3xl border border-border/50 prose prose-invert max-w-none">
                            <p className="text-sm leading-relaxed text-muted-foreground/90 italic">
                                "Net sales increased 12% year-over-year, primarily driven by strong demand in our Data Center segment. Gross margin improved to 72.1% due to favorable product mix and operational efficiencies in our supply chain management process..."
                            </p>
                            <div className="mt-4 flex flex-wrap gap-2">
                                <span className="px-2 py-1 bg-emerald-500/10 text-emerald-500 text-[10px] font-bold rounded-md border border-emerald-500/20">Revenue Growth</span>
                                <span className="px-2 py-1 bg-emerald-500/10 text-emerald-500 text-[10px] font-bold rounded-md border border-emerald-500/20">Margin Expansion</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="p-6 bg-primary/5 rounded-[32px] border border-primary/20 space-y-4 relative overflow-hidden group">
                    <div className="relative z-10 flex items-start gap-4">
                        <div className="p-3 bg-primary rounded-2xl shadow-lg shadow-primary/20">
                            <Sparkles className="w-6 h-6 text-primary-foreground" />
                        </div>
                        <div className="space-y-1">
                            <h4 className="text-lg font-black tracking-tight uppercase">Jarvis Smart Summary</h4>
                            <p className="text-sm text-foreground/80 leading-relaxed font-medium">
                                The document signals a highly bullish trajectory in core segments despite macroeconomic volatility. Key metrics to watch are the sustained R&D efficiency and potential regulatory headwinds mentioned in Section 1A. Management remains focused on margin preservation through automation.
                            </p>
                        </div>
                    </div>
                    <div className="absolute top-0 right-0 w-32 h-32 bg-primary/10 blur-[60px] rounded-full group-hover:bg-primary/20 transition-all duration-700" />
                </div>
            </div>
        </div>
    );
}
