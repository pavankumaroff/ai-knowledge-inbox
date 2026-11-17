import React from 'react';
import { KnowledgeItem } from '../types';
import { FileText, Globe, Trash2, ExternalLink, Clock, Layers } from 'lucide-react';
import { api } from '../services/api';

interface ItemsListProps {
  items: KnowledgeItem[];
  loading: boolean;
  onItemDeleted: () => void;
}

export const ItemsList: React.FC<ItemsListProps> = ({ items, loading, onItemDeleted }) => {
  const handleDelete = async (id: string, title: string) => {
    if (!window.confirm(`Delete "${title}" and all its chunk embeddings?`)) {
      return;
    }
    try {
      await api.deleteItem(id);
      onItemDeleted();
    } catch (err: any) {
      alert(`Failed to delete item: ${err.message}`);
    }
  };

  const formatDate = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-xs p-5">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-700">
            Inbox Items
          </h2>
          <span className="px-2 py-0.5 rounded-full text-[11px] font-bold bg-slate-100 text-slate-600">
            {items.length}
          </span>
        </div>
        <span className="text-xs text-slate-400">Indexed Knowledge</span>
      </div>

      <div className="mt-4 space-y-3 max-h-[520px] overflow-y-auto pr-1">
        {loading && items.length === 0 ? (
          <div className="py-8 text-center text-xs text-slate-400">Loading saved items...</div>
        ) : items.length === 0 ? (
          <div className="py-10 text-center px-4">
            <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400 mb-2">
              <Layers className="w-5 h-5" />
            </div>
            <p className="text-xs font-semibold text-slate-600">Your inbox is empty</p>
            <p className="text-[11px] text-slate-400 mt-1 max-w-[220px] mx-auto">
              Save your first note or URL using the form above to start querying your knowledge base.
            </p>
          </div>
        ) : (
          items.map((item) => (
            <div
              key={item.id}
              className="p-3.5 rounded-lg border border-slate-100 bg-slate-50/60 hover:bg-slate-50 transition-colors group"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2 flex-wrap">
                  {item.type === 'note' ? (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200/60">
                      <FileText className="w-3 h-3" /> Note
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200/60">
                      <Globe className="w-3 h-3" /> URL
                    </span>
                  )}
                  <h3 className="text-xs font-semibold text-slate-800 line-clamp-1">
                    {item.title}
                  </h3>
                </div>

                <button
                  type="button"
                  onClick={() => handleDelete(item.id, item.title)}
                  title="Delete item"
                  className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-rose-600 transition-all p-1"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>

              {item.source_url && (
                <a
                  href={item.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-[11px] text-indigo-600 hover:text-indigo-800 hover:underline mt-1 line-clamp-1"
                >
                  <span className="truncate max-w-[240px]">{item.source_url}</span>
                  <ExternalLink className="w-2.5 h-2.5 shrink-0" />
                </a>
              )}

              <p className="text-[11px] text-slate-500 mt-1.5 line-clamp-2 leading-relaxed">
                {item.preview}
              </p>

              <div className="flex items-center justify-between text-[10px] text-slate-400 mt-2.5 pt-2 border-t border-slate-200/40">
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {formatDate(item.created_at)}
                </span>
                <span className="flex items-center gap-1 font-medium text-slate-500">
                  <Layers className="w-3 h-3" />
                  {item.chunk_count} {item.chunk_count === 1 ? 'chunk' : 'chunks'} ({item.char_count} chars)
                </span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
