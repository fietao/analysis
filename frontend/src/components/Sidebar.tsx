"use client";
import React from 'react';
import Link from 'next/link';
import {
    LayoutDashboard,
    Search,
    BarChart3,
    FileText,
    Settings,
    ShieldCheck,
    Zap
} from 'lucide-react';

const Sidebar = () => {
    const menuItems = [
        { name: 'Dashboard', icon: LayoutDashboard, href: '/' },
        { name: 'Screener', icon: Search, href: '/screener' },
        { name: 'Analytics', icon: BarChart3, href: '/analytics' },
        { name: 'Filings', icon: FileText, href: '/filings' },
    ];

    return (
        <div className="w-64 bg-card border-r border-border h-screen flex flex-col p-6 space-y-8 sticky top-0">
            <div className="flex items-center space-x-3">
                <div className="bg-primary p-2 rounded-lg">
                    <Zap className="text-white w-6 h-6" />
                </div>
                <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-primary to-emerald-400 bg-clip-text text-transparent">
                    FISCAL AI 2.0
                </span>
            </div>

            <nav className="flex-1">
                <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-4 px-2">
                    General
                </div>
                <ul className="space-y-2">
                    {menuItems.map((item) => (
                        <li key={item.name}>
                            <Link
                                href={item.href}
                                className="flex items-center space-x-3 px-3 py-2.5 rounded-xl hover:bg-secondary transition-all group"
                            >
                                <item.icon className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                                <span className="font-medium">{item.name}</span>
                            </Link>
                        </li>
                    ))}
                </ul>
            </nav>

            <div className="pt-6 border-t border-border">
                <div className="flex items-center space-x-3 px-3 py-2 text-muted-foreground">
                    <ShieldCheck className="w-5 h-5" />
                    <span className="text-sm font-medium">Professional v2.0</span>
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
