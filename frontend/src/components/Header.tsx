import React from 'react';
import { Database, Sparkles, Inbox } from 'lucide-react';

interface HeaderProps {
  totalItems: number;
}

export const Header: React.FC<HeaderProps> = ({ totalItems }) => {
  return (
    <header className="border-b border-slate-200 bg-white shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-100">
            <Inbox className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold text-slate-900 tracking-tight">AI Knowledge Inbox</h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200">
                FastAPI + RAG
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">
              Personal second brain with recursive chunking & semantic search
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-xs font-medium text-slate-600">
            <Database className="w-3.5 h-3.5 text-slate-500" />
            <span>SQLite Vector Index</span>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-50 border border-indigo-100 text-xs font-semibold text-indigo-700">
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            <span>{totalItems} {totalItems === 1 ? 'Item' : 'Items'} Ingested</span>
          </div>
        </div>
      </div>
    </header>
  );
};
