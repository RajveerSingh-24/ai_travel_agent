"use client";

import { useState } from "react";

export default function Home() {
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const checkBackend = async () => {
    setLoading(true);
    setError(null);
    setStatus(null);

    try {
      const response = await fetch("http://localhost:8000/health");
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setStatus(data.status);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to connect to backend"
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col flex-1 items-center justify-center min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <main className="flex flex-col items-center justify-center gap-8 px-4 py-8">
        <h1 className="text-4xl font-bold text-center text-gray-900 dark:text-white mb-2">
          AI Travel Agent
        </h1>
        <p className="text-lg text-gray-600 dark:text-gray-300 text-center mb-8">
          Check backend health status
        </p>

        <button
          onClick={checkBackend}
          disabled={loading}
          className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 text-white font-semibold rounded-lg transition-colors duration-200"
        >
          {loading ? "Checking..." : "Check Backend"}
        </button>

        {status && (
          <div className="mt-6 p-4 bg-green-100 dark:bg-green-900 border border-green-400 dark:border-green-600 rounded-lg">
            <p className="text-green-800 dark:text-green-100">
              <strong>Backend Status:</strong> {status}
            </p>
          </div>
        )}

        {error && (
          <div className="mt-6 p-4 bg-red-100 dark:bg-red-900 border border-red-400 dark:border-red-600 rounded-lg">
            <p className="text-red-800 dark:text-red-100">
              <strong>Error:</strong> {error}
            </p>
          </div>
        )}

        <div className="mt-12 text-center text-sm text-gray-600 dark:text-gray-400">
          <p>Backend runs at: http://localhost:8000</p>
          <p>Frontend runs at: http://localhost:3000</p>
        </div>
      </main>
    </div>
  );
}
