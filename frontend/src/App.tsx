import { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import { IngestForm } from './components/IngestForm';
import { ItemsList } from './components/ItemsList';
import { QueryPanel } from './components/QueryPanel';
import { KnowledgeItem } from './types';
import { api } from './services/api';

export function App() {
  const [items, setItems] = useState<KnowledgeItem[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchItems = useCallback(async () => {
    try {
      setLoading(true);
      const data = await api.getItems();
      setItems(data);
    } catch (err) {
      console.error('Failed to load items:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900">
      <Header totalItems={items.length} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Capture & Inbox List */}
          <div className="lg:col-span-5 space-y-6">
            <IngestForm onIngestSuccess={fetchItems} />
            <ItemsList
              items={items}
              loading={loading}
              onItemDeleted={fetchItems}
            />
          </div>

          {/* Right Column: Q&A / Semantic Search / Answer with Citations */}
          <div className="lg:col-span-7">
            <QueryPanel hasItems={items.length > 0} />
          </div>
        </div>
      </main>

      <footer className="border-t border-slate-200 bg-white py-3 text-center text-xs text-slate-400">
        AI Knowledge Inbox • FastAPI + SQLite Vector Store + React
      </footer>
    </div>
  );
}

export default App;
