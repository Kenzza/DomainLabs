"use client";

import React, { useState, useEffect } from 'react';
import { checkHealth, analyzeTarget, AnalyzeResponse } from '@/lib/api';

interface HistoryItem {
  id: string;
  target: string;
  timestamp: string;
  result: AnalyzeResponse;
  checks: string[];
}

const MAX_HISTORY = 20;
const HISTORY_KEY = 'domainlens_history';

export default function Home() {
  const [target, setTarget] = useState('');
  const [mode, setMode] = useState<'simple' | 'technical'>('simple');
  const [checks, setChecks] = useState<{ [key: string]: boolean }>({
    dns: true,
    ip: true,
    http: true,
    tls: true,
    network: true,
  });

  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  const [statusState, setStatusState] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    checkHealth()
      .then(() => setBackendStatus('online'))
      .catch(() => setBackendStatus('offline'));

    try {
      const stored = localStorage.getItem(HISTORY_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (Array.isArray(parsed)) {
          setHistory(parsed);
        }
      }
    } catch (e) {
      console.error('Gagal memuat history dari localStorage:', e);
    }
  }, []);

  const saveHistoryItem = (targetStr: string, resData: AnalyzeResponse, activeChecks: string[]) => {
    try {
      const newItem: HistoryItem = {
        id: 'dl_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7),
        target: targetStr,
        timestamp: new Date().toISOString(),
        result: resData,
        checks: activeChecks,
      };

      const updated = [newItem, ...history].slice(0, MAX_HISTORY);
      setHistory(updated);
      localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
    } catch (e) {
      console.error('Gagal menyimpan history:', e);
    }
  };

  const deleteHistoryItem = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const updated = history.filter(item => item.id !== id);
      setHistory(updated);
      localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));
    } catch (err) {
      console.error('Gagal menghapus history item:', err);
    }
  };

  const clearAllHistory = () => {
    if (window.confirm('Apakah Anda yakin ingin menghapus seluruh riwayat analisis?')) {
      try {
        setHistory([]);
        localStorage.removeItem(HISTORY_KEY);
      } catch (err) {
        console.error('Gagal menghapus seluruh history:', err);
      }
    }
  };

  const openHistoryItem = (item: HistoryItem) => {
    setTarget(item.target);
    setResult(item.result);
    setStatusState('success');
    setShowHistory(false);
  };

  const handleCheckToggle = (key: string) => {
    setChecks(prev => ({ ...prev, [key]: !prev[key] }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!target.trim()) {
      setErrorMessage('Target domain atau URL tidak boleh kosong.');
      setStatusState('error');
      return;
    }

    setStatusState('loading');
    setErrorMessage(null);
    setResult(null);

    const selectedChecks = Object.keys(checks).filter(k => checks[k]);

    try {
      const data = await analyzeTarget({
        target: target.trim(),
        checks: selectedChecks,
      });
      setResult(data);
      setStatusState('success');
      saveHistoryItem(target.trim(), data, selectedChecks);
    } catch (err: any) {
      setErrorMessage(err.message || 'Terjadi kesalahan saat melakukan analisis.');
      setStatusState('error');
    }
  };

  const exportJSON = () => {
    if (!result) return;
    try {
      const exportData = {
        schema_version: "1.0",
        toolkit: "DomainLens",
        target: result.target,
        started_at: result.started_at,
        completed_at: result.completed_at,
        checks: result.checks,
      };

      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportData, null, 2));
      const downloadAnchor = document.createElement('a');
      downloadAnchor.setAttribute("href", dataStr);
      downloadAnchor.setAttribute("download", `domainlens_${result.target.normalized_host || 'analysis'}_${Date.now()}.json`);
      document.body.appendChild(downloadAnchor);
      downloadAnchor.click();
      downloadAnchor.remove();
    } catch (e) {
      console.error('Gagal mengeksport JSON:', e);
      alert('Gagal mengeksport file JSON.');
    }
  };

  const renderSimpleModuleSummary = (checkKey: string, modResult: any) => {
    if (modResult.status !== 'success' || !modResult.data) {
      return <p className="text-xs text-rose-300">Modul tidak berhasil mengumpulkan data ({modResult.status}).</p>;
    }

    const d = modResult.data;
    switch (checkKey) {
      case 'dns': {
        const aRecord = d.records?.A;
        const aItems = Array.isArray(aRecord) 
          ? aRecord 
          : (aRecord?.items && Array.isArray(aRecord.items) ? aRecord.items.map((i: any) => i.value) : (typeof aRecord === 'string' ? [aRecord] : []));
        return (
          <div className="text-xs space-y-1 text-slate-300">
            <p><span className="text-slate-400">Total Records:</span> {d.summary?.total_records || Object.keys(d.records || {}).length}</p>
            {aItems.length > 0 && (
              <p><span className="text-slate-400">A IPs:</span> {aItems.join(', ')}</p>
            )}
          </div>
        );
      }
      case 'ip':
        return (
          <div className="text-xs space-y-1 text-slate-300">
            <p><span className="text-slate-400">IP Utama:</span> {d.ip || d.query}</p>
            <p><span className="text-slate-400">Negara:</span> {d.country_name || d.country || 'N/A'}</p>
            <p><span className="text-slate-400">ISP / Org:</span> {d.org || d.asn || 'N/A'}</p>
          </div>
        );
      case 'http':
      case 'website':
        return (
          <div className="text-xs space-y-1 text-slate-300">
            <p><span className="text-slate-400">Status HTTP:</span> {d.status_code || 'N/A'}</p>
            <p><span className="text-slate-400">Server:</span> {d.server || d.headers?.server || 'N/A'}</p>
            <p><span className="text-slate-400">Content-Type:</span> {d.content_type || d.headers?.['content-type'] || 'N/A'}</p>
          </div>
        );
      case 'tls':
        return (
          <div className="text-xs space-y-1 text-slate-300">
            <p><span className="text-slate-400">Issuer:</span> {d.issuer?.commonName || d.issuer?.organizationName || 'N/A'}</p>
            <p><span className="text-slate-400">Valid Sampai:</span> {d.not_after || 'N/A'}</p>
            <p><span className="text-slate-400">Versi TLS:</span> {d.version || 'N/A'}</p>
          </div>
        );
      case 'network':
      case 'diagnostics':
        return (
          <div className="text-xs space-y-1 text-slate-300">
            <p><span className="text-slate-400">DNS Resolution:</span> {d.dns_ms ?? 'N/A'} ms</p>
            <p><span className="text-slate-400">TCP Connection:</span> {d.tcp_ms ?? 'N/A'} ms</p>
            <p><span className="text-slate-400">Total Duration:</span> {d.total_ms ?? 'N/A'} ms</p>
          </div>
        );
      default:
        return <p className="text-xs text-slate-300">Data tersedia.</p>;
    }
  };

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-blue-600 text-white font-bold px-3 py-1.5 rounded-lg text-lg tracking-wider">
            DL
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">DomainLens</h1>
            <p className="text-xs text-slate-400">Security & Intelligence Toolkit</p>
          </div>
        </div>

        {/* Right Actions & Health */}
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3 py-1.5 rounded-lg transition border border-slate-700 flex items-center space-x-1.5 cursor-pointer"
          >
            <span>Riwayat ({history.length})</span>
          </button>

          <div className="flex items-center space-x-2 text-xs">
            <span className="text-slate-400 hidden sm:inline">Backend:</span>
            {backendStatus === 'checking' && (
              <span className="bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 px-2.5 py-1 rounded-full flex items-center">
                <span className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse mr-1.5"></span>
                Memeriksa...
              </span>
            )}
            {backendStatus === 'online' && (
              <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-1 rounded-full flex items-center">
                <span className="w-2 h-2 rounded-full bg-emerald-400 mr-1.5"></span>
                Online
              </span>
            )}
            {backendStatus === 'offline' && (
              <span className="bg-rose-500/10 text-rose-400 border border-rose-500/20 px-2.5 py-1 rounded-full flex items-center">
                <span className="w-2 h-2 rounded-full bg-rose-400 mr-1.5"></span>
                Offline
              </span>
            )}
          </div>
        </div>
      </header>

      {/* History Drawer Modal */}
      {showHistory && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex justify-end">
          <div className="w-full max-w-md bg-slate-900 border-l border-slate-800 h-full p-6 flex flex-col shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h3 className="font-bold text-white text-base">Riwayat Analisis (LocalStorage)</h3>
              <button
                onClick={() => setShowHistory(false)}
                className="text-slate-400 hover:text-white text-sm px-2 py-1"
              >
                ✕ Tutup
              </button>
            </div>

            <div className="flex-1 overflow-y-auto py-4 space-y-3">
              {history.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-10">Belum ada riwayat analisis tersimpan.</p>
              ) : (
                history.map(item => (
                  <div
                    key={item.id}
                    onClick={() => openHistoryItem(item)}
                    className="bg-slate-950 border border-slate-800 hover:border-blue-500/50 rounded-lg p-3 cursor-pointer transition space-y-2 group"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-bold text-xs text-blue-400 group-hover:underline truncate max-w-[200px]">
                        {item.target}
                      </span>
                      <button
                        onClick={(e) => deleteHistoryItem(item.id, e)}
                        className="text-slate-500 hover:text-rose-400 text-xs p-1"
                        title="Hapus item ini"
                      >
                        🗑
                      </button>
                    </div>
                    <p className="text-[10px] text-slate-500">
                      {new Date(item.timestamp).toLocaleString('id-ID')}
                    </p>
                  </div>
                ))
              )}
            </div>

            {history.length > 0 && (
              <div className="pt-4 border-t border-slate-800">
                <button
                  onClick={clearAllHistory}
                  className="w-full bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 py-2 rounded-lg text-xs font-medium transition"
                >
                  Hapus Semua Riwayat
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Main Container */}
      <div className="flex-1 max-w-5xl w-full mx-auto px-6 py-10 flex flex-col space-y-8">
        
        {/* Intro / Hero */}
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-extrabold text-white">Analisis Domain & Website Security</h2>
          <p className="text-slate-400 max-w-xl mx-auto text-sm">
            Pemeriksaan komprehensif DNS Intelligence, IP Intelligence, Website Inspector, TLS Certificate, dan Network Diagnostics.
          </p>
        </div>

        {/* Control Card */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl space-y-6">
          <form onSubmit={handleSubmit} className="space-y-6">
            
            {/* Target Input */}
            <div className="space-y-2">
              <label htmlFor="target" className="block text-sm font-medium text-slate-300">
                Target Domain atau URL
              </label>
              <div className="flex space-x-3">
                <input
                  id="target"
                  type="text"
                  placeholder="contoh: example.com atau https://example.com"
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  className="flex-1 bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-white placeholder-slate-600 focus:outline-none focus:border-blue-500 text-sm transition"
                />
                <button
                  type="submit"
                  disabled={statusState === 'loading'}
                  className="bg-blue-600 hover:bg-blue-500 active:bg-blue-700 disabled:opacity-50 text-white font-medium px-6 py-3 rounded-lg text-sm transition shadow-lg shadow-blue-600/20 cursor-pointer"
                >
                  {statusState === 'loading' ? 'Menganalisis...' : 'Mulai Analisis'}
                </button>
              </div>
            </div>

            {/* Mode & Check Selection Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-slate-800">
              
              {/* Mode Toggle */}
              <div className="space-y-3">
                <label className="block text-sm font-medium text-slate-300">Mode Tampilan Dashboard</label>
                <div className="flex bg-slate-950 p-1 rounded-lg border border-slate-800">
                  <button
                    type="button"
                    onClick={() => setMode('simple')}
                    className={`flex-1 py-2 text-xs font-medium rounded-md transition ${
                      mode === 'simple'
                        ? 'bg-blue-600 text-white shadow'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Simple Mode
                  </button>
                  <button
                    type="button"
                    onClick={() => setMode('technical')}
                    className={`flex-1 py-2 text-xs font-medium rounded-md transition ${
                      mode === 'technical'
                        ? 'bg-blue-600 text-white shadow'
                        : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Technical Mode
                  </button>
                </div>
              </div>

              {/* Check Selection */}
              <div className="space-y-3">
                <label className="block text-sm font-medium text-slate-300">Modul Pemeriksaan</label>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { key: 'dns', label: 'DNS Intelligence' },
                    { key: 'ip', label: 'IP Intelligence' },
                    { key: 'http', label: 'Website Inspector' },
                    { key: 'tls', label: 'TLS Certificate' },
                    { key: 'network', label: 'Network Diagnostics' },
                  ].map(item => (
                    <label key={item.key} className="flex items-center space-x-2 text-xs text-slate-300 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={checks[item.key] || false}
                        onChange={() => handleCheckToggle(item.key)}
                        className="rounded border-slate-700 bg-slate-950 text-blue-600 focus:ring-blue-500 w-4 h-4"
                      />
                      <span>{item.label}</span>
                    </label>
                  ))}
                </div>
              </div>

            </div>
          </form>
        </div>

        {/* Status / Results Dashboard Area */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl min-h-[280px] flex flex-col">
          {statusState === 'idle' && (
            <div className="my-auto text-center space-y-2">
              <p className="text-slate-400 text-sm">Belum ada analisis yang dijalankan.</p>
              <p className="text-xs text-slate-600">Masukkan target di atas dan klik "Mulai Analisis", atau buka Riwayat.</p>
            </div>
          )}

          {statusState === 'loading' && (
            <div className="my-auto text-center space-y-3">
              <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
              <p className="text-slate-300 text-sm font-medium">Memulai layanan & menganalisis target...</p>
              <p className="text-xs text-slate-500">Menerapkan policy SSRF dan mengumpulkan intelligence modules.</p>
            </div>
          )}

          {statusState === 'error' && (
            <div className="my-auto text-center space-y-2 max-w-md mx-auto">
              <div className="text-rose-400 font-semibold text-sm">Gagal Melakukan Analisis</div>
              <p className="text-slate-300 text-xs bg-rose-500/10 border border-rose-500/20 p-3 rounded-lg">
                {errorMessage}
              </p>
            </div>
          )}

          {statusState === 'success' && result && (
            <div className="w-full space-y-6">
              {/* Dashboard Header Bar */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between border-b border-slate-800 pb-4 gap-4">
                <div>
                  <h3 className="text-base font-bold text-white flex items-center space-x-2">
                    <span>Hasil Analisis:</span>
                    <span className="text-blue-400">{result.target.normalized_url}</span>
                  </h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Waktu Selesai: {result.completed_at} | Mode: {mode === 'simple' ? 'Simple Mode' : 'Technical Mode'}
                  </p>
                </div>

                <button
                  onClick={exportJSON}
                  className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-4 py-2 rounded-lg text-xs font-medium transition flex items-center space-x-1.5 cursor-pointer shadow"
                >
                  <span>📥 Export JSON (v1.0)</span>
                </button>
              </div>

              {/* Module Results Grid */}
              <div className="grid grid-cols-1 gap-4">
                {Object.entries(result.checks).map(([checkKey, modResult]) => {
                  const statusColors: Record<string, string> = {
                    success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
                    not_found: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
                    failed: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
                    timeout: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
                    unavailable: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
                    rate_limited: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
                  };

                  const badgeClass = statusColors[modResult.status] || 'bg-slate-800 text-slate-300 border-slate-700';

                  return (
                    <div key={checkKey} className="bg-slate-950 border border-slate-800 rounded-lg p-5 space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-sm text-slate-200 uppercase tracking-wider">{checkKey}</span>
                        <span className={`text-xs px-2.5 py-1 rounded-full border uppercase font-medium ${badgeClass}`}>
                          {modResult.status}
                        </span>
                      </div>

                      {modResult.message && (
                        <p className="text-xs text-slate-400 italic">{modResult.message}</p>
                      )}

                      {mode === 'simple' ? (
                        <div className="pt-2 border-t border-slate-900">
                          {renderSimpleModuleSummary(checkKey, modResult)}
                        </div>
                      ) : (
                        <div className="bg-slate-900 p-3 rounded border border-slate-800 font-mono text-xs text-slate-300 overflow-x-auto max-h-72">
                          <pre>{JSON.stringify(modResult.data, null, 2)}</pre>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

      </div>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-4 text-center text-xs text-slate-500 mt-auto">
        DomainLens Security Toolkit — Phase 2C (Result Dashboard & History)
      </footer>
    </main>
  );
}
