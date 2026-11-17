import React, { useState } from 'react';
import { FileText, Globe, Plus, Loader2, CheckCircle2, AlertCircle } from 'lucide-react';
import { ItemType } from '../types';
import { api } from '../services/api';

interface IngestFormProps {
  onIngestSuccess: () => void;
}

export const IngestForm: React.FC<IngestFormProps> = ({ onIngestSuccess }) => {
  const [type, setType] = useState<ItemType>('note');
  const [content, setContent] = useState('');
  const [title, setTitle] = useState('');
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) {
      setErrorMessage(type === 'note' ? 'Please enter note content.' : 'Please enter a valid URL.');
      return;
    }

    setLoading(true);
    setErrorMessage(null);
    setSuccessMessage(null);

    try {
      const res = await api.ingest({
        type,
        content: content.trim(),
        title: title.trim() || undefined,
      });

      setSuccessMessage(`Saved "${res.title}" (${res.chunk_count} semantic chunks generated)`);
      setContent('');
      setTitle('');
      onIngestSuccess();
      
      // Auto-clear success message after 4s
      setTimeout(() => setSuccessMessage(null), 4000);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to ingest item. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-700">
          Capture Knowledge
        </h2>
        <span className="text-xs text-slate-400">Step 1: Ingest</span>
      </div>

      {/* Tabs */}
      <div className="grid grid-cols-2 gap-2 mt-4 p-1 bg-slate-100 rounded-lg">
        <button
          type="button"
          onClick={() => {
            setType('note');
            setErrorMessage(null);
          }}
          className={`flex items-center justify-center gap-2 py-2 text-xs font-semibold rounded-md transition-all ${
            type === 'note'
              ? 'bg-white text-indigo-700 shadow-xs'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          Text Note
        </button>
        <button
          type="button"
          onClick={() => {
            setType('url');
            setErrorMessage(null);
          }}
          className={`flex items-center justify-center gap-2 py-2 text-xs font-semibold rounded-md transition-all ${
            type === 'url'
              ? 'bg-white text-emerald-700 shadow-xs'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <Globe className="w-3.5 h-3.5" />
          Web URL
        </button>
      </div>

      <form onSubmit={handleSubmit} className="mt-4 space-y-3">
        {/* Optional Title */}
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">
            Title <span className="text-slate-400 font-normal">(Optional)</span>
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder={type === 'note' ? 'e.g. Architecture Decisions' : 'e.g. React 19 Documentation'}
            className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all placeholder:text-slate-400"
          />
        </div>

        {/* Content Input */}
        <div>
          <label className="block text-xs font-medium text-slate-600 mb-1">
            {type === 'note' ? 'Note Content *' : 'Web Page URL *'}
          </label>
          {type === 'note' ? (
            <textarea
              rows={4}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Paste plain text, documentation snippet, meeting notes..."
              className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all placeholder:text-slate-400 font-mono text-xs leading-relaxed"
            />
          ) : (
            <input
              type="url"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="https://example.com/article"
              className="w-full px-3 py-2 text-sm rounded-lg border border-slate-200 focus:outline-hidden focus:ring-2 focus:ring-emerald-500/20 focus:border-emerald-500 transition-all placeholder:text-slate-400 font-mono text-xs"
            />
          )}
          {type === 'url' && (
            <p className="text-[11px] text-slate-400 mt-1">
              Content is fetched and parsed server-side with clutter stripped out.
            </p>
          )}
        </div>

        {/* Status Alerts */}
        {errorMessage && (
          <div className="flex items-start gap-2 p-3 text-xs rounded-lg bg-rose-50 border border-rose-200 text-rose-700">
            <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
            <p className="leading-snug">{errorMessage}</p>
          </div>
        )}

        {successMessage && (
          <div className="flex items-start gap-2 p-3 text-xs rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800">
            <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
            <p className="leading-snug">{successMessage}</p>
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading || !content.trim()}
          className={`w-full py-2.5 px-4 rounded-lg text-xs font-semibold text-white flex items-center justify-center gap-2 shadow-xs transition-all ${
            loading || !content.trim()
              ? 'bg-slate-300 cursor-not-allowed text-slate-500'
              : type === 'note'
              ? 'bg-indigo-600 hover:bg-indigo-700 active:scale-[0.99]'
              : 'bg-emerald-600 hover:bg-emerald-700 active:scale-[0.99]'
          }`}
        >
          {loading ? (
            <>
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              <span>{type === 'url' ? 'Scraping & Indexing...' : 'Chunking & Indexing...'}</span>
            </>
          ) : (
            <>
              <Plus className="w-3.5 h-3.5" />
              <span>Save & Index {type === 'note' ? 'Note' : 'URL'}</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};
