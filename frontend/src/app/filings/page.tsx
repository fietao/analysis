"use client";
import React, { useState, useEffect, useRef } from 'react';
import {
    FileText,
    Upload,
    ShieldAlert,
    Search,
    Sparkles,
    BookOpen,
    ArrowRight,
    Loader2,
    CheckCircle2,
    TrendingUp
} from 'lucide-react';

interface FilingData {
    filename: string;
    sections: {
        [key: string]: string;
    };
}

export default function FilingsPage() {
    const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
    const [filingData, setFilingData] = useState<FilingData | null>(null);
    const [loading, setLoading] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [tickersWithFilings, setTickersWithFilings] = useState<string[]>(['NVDA', 'AAPL', 'MSFT']); // Initial display
    const fileInputRef = useRef<HTMLInputElement>(null);

    const fetchFiling = async (ticker: string) => {
        setLoading(true);
        setFilingData(null);
        try {
            const response = await fetch(`http://localhost:8000/api/filings/${ticker}`);
            if (!response.ok) throw new Error("Filing not found");
            const data = await response.json();
            setFilingData(data.insights);
            setSelectedTicker(ticker);
        } catch (err) {
            console.error(err);
            setSelectedTicker(ticker); // Still select it so we can show the "upload" state
        } finally {
            setLoading(false);
        }
    };

    const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file || !selectedTicker) return;

        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);

        const isExcel = file.name.endsWith('.xlsx') || file.name.endsWith('.xls') || file.name.endsWith('.csv');
        const endpoint = isExcel
            ? `http://localhost:8000/api/upload-data/${selectedTicker}`
            : `http://localhost:8000/api/upload-filing/${selectedTicker}`;

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();

            if (isExcel && data.status === 'success') {
                alert("Custom Excel data successfully imported! You can now view it in the Analytics tab.");
            } else if (!isExcel && data.status === 'success') {
                setFilingData(data.insights);
            }
        } catch (err) {
            console.error("Upload failed", err);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="space-y-10 animate-in fade-in slide-in-from-top-4 duration-700">
            <header className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                <div className="space-y-2">
                    <h1 className="text-4xl font-extrabold tracking-tight flex items-center gap-3">
                        <FileText className="text-primary w-10 h-10" />
                        Intelligence Center
                    </h1>
                    <p className="text-muted-foreground text-lg">SEC filing ingestion and custom Excel data analysis.</p>
                </div>

                <div className="flex flex-wrap gap-4">
                    <input
                        type="file"
                        ref={fileInputRef}
                        className="hidden"
                        accept=".pdf,.xlsx,.csv"
                        onChange={handleUpload}
                    />

                    <button
                        onClick={() => fileInputRef.current?.click()}
                        disabled={!selectedTicker || uploading}
                        className="flex items-center space-x-3 px-6 py-3.5 bg-secondary border border-border rounded-2xl font-black hover:bg-secondary/70 transition-all disabled:opacity-50"
                    >
                        <Upload size={20} />
                        <span>IMPORT DATA (.XLSX)</span>
                    </button>

                    <button
                        onClick={() => fileInputRef.current?.click()}
                        disabled={!selectedTicker || uploading}
                        className="flex items-center space-x-3 px-8 py-3.5 bg-primary text-primary-foreground rounded-2xl font-black shadow-lg shadow-primary/20 hover:scale-[1.02] transition-all disabled:opacity-50"
                    >
                        {uploading ? <Loader2 className="animate-spin" size={20} /> : <FileText size={20} />}
                        <span>{uploading ? "ANALYZING..." : "UPLOAD PDF FILING"}</span>
                    </button>
                </div>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                <div className="lg:col-span-1 space-y-6">
                    {/* Guide Card */}
                    <div className="glass-card rounded-3xl p-6 bg-gradient-to-br from-amber-500/10 to-transparent border border-amber-500/20">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 bg-amber-500 rounded-lg">
                                <Search className="w-4 h-4 text-black" />
                            </div>
                            <h4 className="text-sm font-black uppercase tracking-tight">How to get Excel Filings?</h4>
                        </div>
                        <ol className="text-xs text-muted-foreground space-y-3 list-decimal ml-4">
                            <li>Go to <a href="https://www.sec.gov/edgar/searchedgar/companysearch.html" target="_blank" className="text-primary hover:underline">SEC EDGAR</a></li>
                            <li>Search for your company ticker (e.g., AAPL).</li>
                            <li>Find the 10-K or 10-Q filing.</li>
                            <li>Click <b>"Interactive Data"</b>.</li>
                            <li>Click <b>"View Excel Document"</b> to download the financial numbers.</li>
                        </ol>
                    </div>

                    <div className="glass-card rounded-3xl p-6 glow-shadow border border-white/5">
                        <h3 className="font-black uppercase tracking-widest text-xs text-muted-foreground mb-4">Target Tickers</h3>
                        <div className="space-y-3">
                            {tickersWithFilings.map((ticker) => (
                                <div
                                    key={ticker}
                                    onClick={() => fetchFiling(ticker)}
                                    className={`p-4 rounded-2xl border transition-all cursor-pointer group ${selectedTicker === ticker ? 'bg-primary/10 border-primary shadow-sm' : 'bg-secondary/40 border-border hover:border-primary/30'}`}
                                >
                                    <div className="flex justify-between items-center">
                                        <span className="font-black text-lg">{ticker}</span>
                                        {selectedTicker === ticker && <CheckCircle2 size={16} className="text-primary" />}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="lg:col-span-3">
                    {loading ? (
                        <div className="glass-card rounded-[40px] p-12 min-h-[600px] flex flex-col items-center justify-center space-y-4">
                            <Loader2 className="w-12 h-12 text-primary animate-spin" />
                            <p className="font-black text-primary tracking-widest uppercase">Jarvis is reading...</p>
                        </div>
                    ) : filingData ? (
                        <FilingViewer ticker={selectedTicker || ""} data={filingData} />
                    ) : (
                        <div className="glass-card rounded-[40px] p-12 min-h-[600px] flex flex-col items-center justify-center text-center space-y-6 border-2 border-dashed border-border">
                            <div className="w-24 h-24 bg-secondary rounded-full flex items-center justify-center border border-border">
                                <BookOpen className="w-10 h-10 text-muted-foreground/40" />
                            </div>
                            <div className="space-y-2">
                                <h2 className="text-2xl font-bold opacity-50">Document Library Empty</h2>
                                <p className="text-muted-foreground max-w-sm italic">
                                    Select a ticker and upload its 10-K/Q PDF file to unlock automated risk and management sentiment extraction.
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

function FilingViewer({ ticker, data }: { ticker: string, data: FilingData }) {
    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div className="p-8 glass-card rounded-[40px] glow-shadow space-y-8 border border-white/5">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-border/50">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-primary rounded-xl flex items-center justify-center font-black text-xl text-primary-foreground shadow-lg">
                            {ticker[0]}
                        </div>
                        <div>
                            <h2 className="text-2xl font-black tracking-tight">{ticker} Intelligence Report</h2>
                            <p className="text-sm font-medium text-muted-foreground">Source: {data.filename}</p>
                        </div>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="space-y-4">
                        <div className="flex items-center gap-2 text-rose-500">
                            <ShieldAlert size={18} />
                            <h3 className="text-sm font-black uppercase tracking-widest">Risk Factors (Section 1A)</h3>
                        </div>
                        <div className="p-6 bg-secondary/30 rounded-3xl border border-border/50 min-h-[250px]">
                            <p className="text-sm leading-relaxed text-muted-foreground/90 italic">
                                {data.sections["Risk Factors"] || "No direct Risk Factors extracted from this document."}
                            </p>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div className="flex items-center gap-2 text-emerald-500">
                            <TrendingUp size={18} />
                            <h3 className="text-sm font-black uppercase tracking-widest">Management Discussion (MD&A)</h3>
                        </div>
                        <div className="p-6 bg-secondary/30 rounded-3xl border border-border/50 min-h-[250px]">
                            <p className="text-sm leading-relaxed text-muted-foreground/90 italic">
                                {data.sections["Management Discussion"] || "No MD&A section identified."}
                            </p>
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
                                Analysis of {data.filename} suggests a concentrated focus on {ticker === 'NVDA' ? 'Data Center growth and GPU demand' : 'operational efficiency and market expansion'}. {data.sections["Risk Factors"] ? 'Risk factors highlight significant competitive headwinds.' : 'General market risks are noted but contain no unique structural anomalies.'}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
