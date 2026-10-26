import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Shield, Lock, Cloud, Activity, Server, Upload, Files, ArrowRight, CheckCircle, AlertCircle } from 'lucide-react';
import { cloudApi } from '../api/cloud';
import type { DashboardStats } from '../types';
import { formatDistanceToNow } from 'date-fns';

function StatCard({ label, value, sub, color }: { label: string; value: string | number; sub?: string; color?: string }) {
  return (
    <div className="card">
      <div className={`text-3xl font-bold mb-1 ${color || 'text-white'}`}>{value}</div>
      <div className="text-slate-400 text-sm">{label}</div>
      {sub && <div className="text-slate-500 text-xs mt-1">{sub}</div>}
    </div>
  );
}

function formatBytes(bytes: number) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    cloudApi.stats()
      .then(r => setStats(r.data))
      .catch(e => setError('Failed to load dashboard data'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="p-8 flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="text-slate-400 mt-1">Your encrypted file storage overview</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-900/20 border border-red-800 rounded-lg text-red-400 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Encrypted Files" value={stats?.total_files ?? 0} color="text-blue-400" />
        <StatCard label="Storage Used" value={formatBytes(stats?.total_original_bytes ?? 0)} sub="Original size" color="text-emerald-400" />
        <StatCard label="Encrypt Operations" value={stats?.encrypt_operations ?? 0} color="text-purple-400" />
        <StatCard
          label="Decryptions"
          value={`${stats?.successful_decryptions ?? 0} / ${stats?.failed_decryptions ?? 0}`}
          sub="Success / Failed"
          color="text-amber-400"
        />
      </div>

      {/* Storage Provider */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
        <div className="card flex items-center gap-4">
          <div className="w-10 h-10 bg-blue-900/50 rounded-lg flex items-center justify-center">
            <Cloud className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <div className="text-sm text-slate-400">Storage Provider</div>
            <div className="text-white font-semibold">{stats?.storage_provider ?? '—'}</div>
          </div>
        </div>
        <div className="card flex items-center gap-4">
          <div className="w-10 h-10 bg-emerald-900/50 rounded-lg flex items-center justify-center">
            <Lock className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <div className="text-sm text-slate-400">Encryption</div>
            <div className="text-white font-semibold">AES-256-GCM</div>
          </div>
        </div>
        <div className="card flex items-center gap-4">
          <div className="w-10 h-10 bg-purple-900/50 rounded-lg flex items-center justify-center">
            <Shield className="w-5 h-5 text-purple-400" />
          </div>
          <div>
            <div className="text-sm text-slate-400">Encrypted Storage</div>
            <div className="text-white font-semibold">{formatBytes(stats?.total_encrypted_bytes ?? 0)}</div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent uploads */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-white">Recent Uploads</h2>
            <Link to="/files" className="text-blue-400 hover:text-blue-300 text-sm">View all →</Link>
          </div>
          {stats?.recent_uploads && stats.recent_uploads.length > 0 ? (
            <div className="space-y-3">
              {stats.recent_uploads.map(f => (
                <div key={f.id} className="flex items-center gap-3 p-3 bg-slate-800 rounded-lg">
                  <div className="w-8 h-8 bg-blue-900/50 rounded flex items-center justify-center flex-shrink-0">
                    <Files className="w-4 h-4 text-blue-400" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-white font-medium truncate">{f.filename}</div>
                    <div className="text-xs text-slate-400">{formatBytes(f.size)} • {formatDistanceToNow(new Date(f.uploaded), { addSuffix: true })}</div>
                  </div>
                  <span className="badge-success"><Lock className="w-3 h-3" />enc</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-500">
              <Files className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No files yet. <Link to="/encrypt" className="text-blue-400">Encrypt your first file</Link></p>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        <div className="card">
          <h2 className="font-semibold text-white mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <Link to="/encrypt" className="flex items-center gap-4 p-4 bg-blue-600/10 hover:bg-blue-600/20 border border-blue-600/30 rounded-lg transition-colors">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center flex-shrink-0">
                <Upload className="w-5 h-5 text-white" />
              </div>
              <div>
                <div className="text-white font-medium">Encrypt a File</div>
                <div className="text-slate-400 text-sm">Upload and encrypt with AES-256-GCM</div>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400 ml-auto" />
            </Link>
            <Link to="/files" className="flex items-center gap-4 p-4 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors">
              <div className="w-10 h-10 bg-emerald-900 rounded-lg flex items-center justify-center flex-shrink-0">
                <Files className="w-5 h-5 text-emerald-400" />
              </div>
              <div>
                <div className="text-white font-medium">My Files</div>
                <div className="text-slate-400 text-sm">View, download, and manage encrypted files</div>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400 ml-auto" />
            </Link>
            <Link to="/audit" className="flex items-center gap-4 p-4 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors">
              <div className="w-10 h-10 bg-purple-900 rounded-lg flex items-center justify-center flex-shrink-0">
                <Activity className="w-5 h-5 text-purple-400" />
              </div>
              <div>
                <div className="text-white font-medium">Audit Log</div>
                <div className="text-slate-400 text-sm">Review security events</div>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400 ml-auto" />
            </Link>
            <Link to="/cloud" className="flex items-center gap-4 p-4 bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors">
              <div className="w-10 h-10 bg-amber-900 rounded-lg flex items-center justify-center flex-shrink-0">
                <Server className="w-5 h-5 text-amber-400" />
              </div>
              <div>
                <div className="text-white font-medium">Cloud Infrastructure</div>
                <div className="text-slate-400 text-sm">Storage status and health</div>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400 ml-auto" />
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
