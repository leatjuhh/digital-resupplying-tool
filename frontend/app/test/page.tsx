'use client';

import { useState, useEffect } from 'react';
import { api, Article } from '@/lib/api';

export default function TestPage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    checkConnection();
    loadArticles();
  }, []);

  async function checkConnection() {
    try {
      await api.healthCheck();
      setConnected(true);
    } catch {
      setConnected(false);
    }
  }

  async function loadArticles() {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getArticles();
      setArticles(data);
    } catch (err) {
      setError('Kon artikelen niet laden. Is de backend aan?');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Backend Integratie Test</h1>

      {/* Connection Status */}
      <div className="mb-6 p-4 border rounded">
        <h2 className="text-xl font-semibold mb-2">Backend Status</h2>
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span>{connected ? 'Verbonden' : 'Niet verbonden'}</span>
          <span className="text-sm text-gray-500 ml-2">http://localhost:8000</span>
        </div>
      </div>

      {/* Articles List */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Artikelen van Backend</h2>
          <button
            onClick={loadArticles}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            disabled={loading}
          >
            {loading ? 'Laden...' : 'Ververs'}
          </button>
        </div>

        {loading && <p>Artikelen laden...</p>}

        {error && (
          <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        {!loading && !error && articles.length === 0 && (
          <p className="text-gray-500">Geen artikelen gevonden.</p>
        )}

        {!loading && !error && articles.length > 0 && (
          <div className="space-y-4">
            {articles.map((article) => (
              <div key={article.artikelnummer} className="p-4 border rounded">
                <h3 className="font-bold text-lg">{article.omschrijving}</h3>
                <p className="text-sm text-gray-600 mb-2">SKU: {article.artikelnummer}</p>
                
                <div className="mt-3">
                  <p className="text-sm font-semibold mb-2">Voorraad per winkel:</p>
                  <div className="grid grid-cols-2 gap-2">
                    {Object.entries(article.voorraad_per_winkel).map(([winkel, voorraad]) => (
                      <div key={winkel} className="flex justify-between p-2 bg-gray-50 rounded">
                        <span className="font-medium">{winkel}</span>
                        <span className="text-blue-600">{voorraad} stuks</span>
                      </div>
                    ))}
                  </div>
                  <p className="text-sm text-gray-500 mt-2">
                    Totaal: {Object.values(article.voorraad_per_winkel).reduce((a, b) => a + b, 0)} stuks
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded">
        <h3 className="font-semibold mb-2">📝 Instructies</h3>
        <ol className="list-decimal list-inside space-y-1 text-sm">
          <li>Zorg dat de backend draait op http://localhost:8000</li>
          <li>Deze pagina haalt automatisch data op van /api/articles</li>
          <li>Klik op "Ververs" om data opnieuw op te halen</li>
        </ol>
        <p className="mt-2 text-sm text-gray-600">
          Backend starten: <code className="bg-white px-2 py-1 rounded">cd backend && venv\Scripts\activate && uvicorn main:app --reload</code>
        </p>
      </div>
    </div>
  );
}
