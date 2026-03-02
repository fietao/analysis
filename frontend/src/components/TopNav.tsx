"use client";
import React, { useState, useEffect, useRef } from 'react';
import { Search, Bell, UserCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function TopNav() {
    const [query, setQuery] = useState('');
    const [tickers, setTickers] = useState<string[]>([]);
    const [filteredTickers, setFilteredTickers] = useState<string[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const searchRef = useRef<HTMLDivElement>(null);
    const router = useRouter();

    useEffect(() => {
        // Fetch tickers from the backend for autocomplete
        fetch('http://localhost:8000/api/stocks')
            .then(res => res.json())
            .then(data => setTickers(data.tickers || []))
            .catch(err => console.error("Failed to fetch tickers:", err));

        // Handle click outside to close dropdown
        const handleClickOutside = (event: MouseEvent) => {
            if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    useEffect(() => {
        if (query.trim() === '') {
            setFilteredTickers([]);
            setIsOpen(false);
        } else {
            const filtered = tickers.filter(t => t.toLowerCase().includes(query.toLowerCase())).slice(0, 6);
            setFilteredTickers(filtered);
            setIsOpen(true);
        }
    }, [query, tickers]);

    const handleSelect = (ticker: string) => {
        setQuery('');
        setIsOpen(false);
        router.push(`/analytics?ticker=${ticker}`);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && isOpen && filteredTickers.length > 0) {
            handleSelect(filteredTickers[0]);
        } else if (e.key === 'Enter' && query.trim() !== '') {
            handleSelect(query.toUpperCase());
        }
    };

    return (
        <div className="flex items-center justify-between w-full h-20 mb-8 mt-2 sticky top-0 z-40">
            <div className="flex-1 max-w-2xl relative" ref={searchRef}>
                <div className="relative flex flex-col items-center w-full h-14 rounded-2xl focus-within:ring-2 focus-within:ring-primary bg-secondary/40 backdrop-blur-md overflow-hidden border border-border shadow-lg transition-all duration-300">
                    <div className="flex h-14 w-full items-center">
                        <div className="grid place-items-center h-full w-14 text-muted-foreground">
                            <Search size={22} />
                        </div>
                        <input
                            className="h-full w-full outline-none text-base bg-transparent placeholder-muted-foreground pr-4 text-foreground font-medium"
                            type="text"
                            id="search"
                            placeholder="Search NAS100 tickers (e.g., NVDA, MSFT)..."
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={handleKeyDown}
                            onFocus={() => { if (query.length > 0) setIsOpen(true) }}
                            autoComplete="off"
                            spellCheck="false"
                        />
                    </div>
                </div>

                {/* Autocomplete Dropdown */}
                {isOpen && filteredTickers.length > 0 && (
                    <div className="absolute top-16 left-0 w-full bg-card/95 backdrop-blur-lg border border-border rounded-xl shadow-2xl z-50 overflow-hidden glow-shadow animate-in fade-in slide-in-from-top-2 duration-200">
                        <ul className="py-2">
                            {filteredTickers.map((ticker, index) => (
                                <li
                                    key={ticker}
                                    className={`px-5 py-3 hover:bg-secondary cursor-pointer flex items-center justify-between transition-colors ${index === 0 ? "bg-secondary/30" : ""}`}
                                    onClick={() => handleSelect(ticker)}
                                >
                                    <div className="flex items-center space-x-3">
                                        <span className="font-extrabold text-primary">{ticker}</span>
                                        <span className="text-sm font-medium text-muted-foreground bg-secondary/50 px-2 py-0.5 rounded-md">Equities</span>
                                    </div>
                                    <span className="text-xs font-bold text-muted-foreground/80 tracking-widest uppercase">Analyze &rarr;</span>
                                </li>
                            ))}
                        </ul>
                    </div>
                )}
            </div>

            <div className="flex items-center space-x-8 ml-8">
                <button className="text-muted-foreground hover:text-primary transition-colors relative group">
                    <Bell size={24} className="group-hover:animate-pulse" />
                    <span className="absolute -top-1 -right-1 w-3 h-3 bg-rose-500 rounded-full border-2 border-background animate-pulse"></span>
                </button>
                <div className="flex items-center space-x-3 cursor-pointer group hover:bg-secondary/40 p-2 pr-4 rounded-full border border-transparent hover:border-border transition-all duration-300">
                    <UserCircle size={40} className="text-muted-foreground group-hover:text-primary transition-colors" />
                    <div className="text-left hidden md:block">
                        <p className="text-sm font-extrabold text-foreground group-hover:text-primary transition-colors">Elite Analyst</p>
                        <p className="text-xs text-muted-foreground font-medium">Pro Subscription</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
