import React, { useState } from 'react';
import { Search, Sparkles, Loader2, Quote, ExternalLink, Bot, HelpCircle } from 'lucide-react';
import { QueryResponse } from '../types';
import { api } from '../services/api';

interface QueryPanelProps {
  hasItems: boolean;
}

export const QueryPanel: React.FC<QueryPanelProps> = ({ hasItems }) => {
  const [question, setQuestion] = useState('');
  const [topK, setTopK] = useState(4);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAsk = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await api.query(question.trim(), topK);
      setResponse(res);
    } catch (err: any) {
      setError(err.message || 'Failed to complete query. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickQuestion = (sample: string) => {
    setQuestion(sample);
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5 flex flex-col h-full">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded-md bg-indigo-50 flex items-center justify-center text-indigo-600">
            <Bot className="w-4 h-4" />
          </div>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-700">
            Ask Your Knowledge Base
          </h2>
        </div>
        <span className="text-xs text-slate-400">Step 2: RAG Retrieval</span>
      </div>

      {/* Query Input */}
      <form onSubmit={handleAsk} className="mt-4 space-y-3">
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">
            Question
          </label>
          <div className="relative">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="e.g. What are the key architecture decisions? How does vector search work?"
              className="w-full pl-9 pr-24 py-2.5 text-sm rounded-lg border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all placeholder:text-slate-400"
            />
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
            <button
              type="submit"
              disabled={loading || !question.trim()}
              className={`absolute right-1.5 top-1.5 px-3 py-1.5 rounded-md text-xs font-semibold text-white flex items-center gap-1.5 transition-all ${
                loading || !question.trim()
                  ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-700 active:scale-[0.98]'
              }`}
            >
              {loading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Ask AI</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Top-K settings & suggested prompts */}
        <div className="flex items-center justify-between text-xs text-slate-500 pt-1">
          <div className="flex items-center gap-1.5">
            <span>Retrieve Top</span>
            <select
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              className="px-2 py-0.5 text-xs font-semibold bg-slate-100 rounded-md border border-slate-200 text-slate-700 focus:outline-hidden"
            >
              <option value={2}>2 chunks</option>
              <option value={3}>3 chunks</option>
              <option value={4}>4 chunks</option>
              <option value={6}>6 chunks</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] text-slate-400">Quick test:</span>
            <button
              type="button"
              onClick={() => handleQuickQuestion('Summarize everything I have saved')}
              className="text-[11px] text-indigo-600 hover:text-indigo-800 underline decoration-indigo-300 underline-offset-2"
            >
              Summarize all
            </button>
          </div>
        </div>
      </form>

      {/* Error Banner */}
      {error && (
        <div className="mt-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700">
          {error}
        </div>
      )}

      {/* Answer & Sources Display */}
      <div className="mt-5 flex-1 overflow-y-auto space-y-4">
        {loading && (
          <div className="p-6 text-center rounded-xl border border-slate-100 bg-slate-50/50">
            <Loader2 className="w-6 h-6 animate-spin text-indigo-600 mx-auto mb-2" />
            <p className="text-xs font-medium text-slate-600">Retrieving relevant chunks & synthesizing response...</p>
            <p className="text-[11px] text-slate-400 mt-0.5">Computing cosine similarities across vector embeddings</p>
          </div>
        )}

        {!loading && !response && (
          <div className="p-8 text-center rounded-xl border border-dashed border-slate-200 text-slate-400">
            <HelpCircle className="w-8 h-8 mx-auto mb-2 text-slate-300" />
            <p className="text-xs font-medium text-slate-600">Ask any question to search your saved items</p>
            <p className="text-[11px] text-slate-400 mt-1 max-w-sm mx-auto">
              {hasItems
                ? 'Your query will find the most semantically relevant text chunks and synthesize an answer citing exact sources.'
                : 'Save notes or URLs on the left first to build your knowledge base.'}
            </p>
          </div>
        )}

        {!loading && response && (
          <div className="space-y-4 animate-in fade-in duration-300">
            {/* Generated Answer Card */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-800 flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-indigo-600" /> AI Answer
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-200/70 text-slate-700">
                  {response.model_used}
                </span>
              </div>
              <div className="text-xs text-slate-800 leading-relaxed whitespace-pre-wrap font-sans">
                {response.answer}
              </div>
            </div>

            {/* Cited Sources Section */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-600 flex items-center gap-1.5">
                  <Quote className="w-3.5 h-3.5 text-slate-500" /> Cited Sources ({response.sources.length})
                </h3>
                <span className="text-[11px] text-slate-400">Ranked by cosine similarity</span>
              </div>

              {response.sources.length === 0 ? (
                <p className="text-xs text-slate-400 italic">No source chunks retrieved for this query.</p>
              ) : (
                <div className="space-y-2.5">
                  {response.sources.map((src, index) => (
                    <div
                      key={src.chunk_id || index}
                      className="p-3 rounded-lg border border-slate-200 bg-white hover:border-slate-300 transition-all text-xs"
                    >
                      <div className="flex items-center justify-between gap-2 mb-1.5">
                        <div className="flex items-center gap-2">
                          <span className="px-1.5 py-0.5 rounded-md font-mono text-[10px] font-bold bg-indigo-100 text-indigo-800">
                            [{index + 1}]
                          </span>
                          <span className="font-semibold text-slate-800 line-clamp-1">
                            {src.title}
                          </span>
                        </div>
                        <div className="flex items-center gap-1.5 shrink-0">
                          <span className="text-[10px] font-mono text-slate-400">similarity:</span>
                          <span className="px-1.5 py-0.5 rounded-md font-mono text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                            {(src.similarity_score * 100).toFixed(1)}%
                          </span>
                        </div>
                      </div>

                      {src.source_url && (
                        <a
                          href={src.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-[11px] text-indigo-600 hover:underline mb-1.5"
                        >
                          <span className="truncate max-w-[260px]">{src.source_url}</span>
                          <ExternalLink className="w-2.5 h-2.5" />
                        </a>
                      )}

                      <div className="p-2 rounded-md bg-slate-50 text-[11px] text-slate-600 font-mono leading-relaxed border border-slate-100">
                        "{src.snippet}"
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
