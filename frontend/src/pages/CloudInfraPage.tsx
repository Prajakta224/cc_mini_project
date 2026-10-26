import React, { useEffect, useState } from 'react';
import { cloudApi } from '../api/cloud';
import type { CloudStatus } from '../types';
import { Cloud, Server, Database, CheckCircle, XCircle, RefreshCw, AlertTriangle, Activity } from 'lucide-react';

interface Health {
  status: string; api: boolean; database: boolean; database_message: string; timestamp: string; environment: string;
}

export default function CloudInfraPage() {
  const [health, setHealth] = useState<Health | null>(null);
  const [cloudStatus, setCloudStatus] = useState<CloudStatus | null>(null);
  const [testResult, setTestResult] = useState<{ test_passed: boolean; errors: string[]; timestamp: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [h, s] = await Promise.all([cloudApi.health(), cloudApi.status()]);
      setHealth(h.data);
      setCloudStatus(s.data);
    } catch {
    } finally {
      setLoading(false);
    }
  };

  const runTest = async () => {
    setTesting(true);
    try {
      const res = await cloudApi.test();
      setTestResult(res.data);
    } catch {
    } finally {
      setTesting(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  const StatusIcon = ({ ok }: { ok: boolean }) =>
    ok ? <CheckCircle className="w-5 h-5 text-emerald-400" /> : <XCircle className="w-5 h-5 text-red-400" />;

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Cloud Infrastructure</h1>
          <p className="text-slate-400 mt-1">System health and storage provider status</p>
        </div>
        <button onClick={loadData} className="btn-secondary flex items-center gap-2">
          <RefreshCw className="w-4 h-4" /> Refresh
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <div className="space-y-6">
          {/* System Health */}
          <div className="card">
            <h2 className="font-semibold text-white mb-4 flex items-center gap-2">
              <Activity className="w-4 h-4 text-blue-400" /> System Health
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <StatusCard icon={<Server className="w-5 h-5 text-blue-400" />} label="API Server" ok={health?.api ?? false}
                sub={health?.environment} />
              <StatusCard icon={<Database className="w-5 h-5 text-purple-400" />} label="Database" ok={health?.database ?? false}
                sub={health?.database_message} />
              <StatusCard icon={<Cloud className="w-5 h-5 text-emerald-400" />} label="Storage" ok={cloudStatus?.connected ?? false}
                sub={cloudStatus?.provider} />
            </div>
          </div>

          {/* Storage Details */}
          {cloudStatus && (
            <div className="card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold text-white flex items-center gap-2">
                  <Cloud className="w-4 h-4 text-blue-400" /> Storage Provider: {cloudStatus.provider}
                </h2>
                <span className={`text-xs px-2 py-1 rounded-full ${cloudStatus.connected ? 'badge-success' : 'badge-error'}`}>
                  {cloudStatus.connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>

              {cloudStatus.warning && (
                <div className="flex items-start gap-2 bg-amber-900/20 border border-amber-800 rounded-lg p-3 mb-4">
                  <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                  <p className="text-amber-300 text-sm">{cloudStatus.warning}</p>
                </div>
              )}

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <InfoBox label="Bucket" value={cloudStatus.bucket || '—'} />
                <InfoBox label="Mode" value={cloudStatus.mode || '—'} />
                <InfoBox label="Objects" value={cloudStatus.object_count?.toString() ?? '—'} />
                <InfoBox label="Total Size" value={cloudStatus.total_bytes !== undefined ? formatBytes(cloudStatus.total_bytes) : '—'} />
              </div>

              <p className="text-slate-500 text-sm mt-4">{cloudStatus.message}</p>
            </div>
          )}

          {/* Live Connection Test */}
          <div className="card">
            <h2 className="font-semibold text-white mb-4">Live Connection Test</h2>
            <p className="text-slate-400 text-sm mb-4">
              Run a write-read-delete probe to verify the storage provider is fully operational.
            </p>
            <button onClick={runTest} disabled={testing} className="btn-primary flex items-center gap-2">
              {testing
                ? <><div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" /> Testing...</>
                : <><Activity className="w-4 h-4" /> Run Connection Test</>
              }
            </button>
            {testResult && (
              <div className={`mt-4 p-4 rounded-lg border ${testResult.test_passed ? 'bg-emerald-900/20 border-emerald-800' : 'bg-red-900/20 border-red-800'}`}>
                <div className="flex items-center gap-2">
                  {testResult.test_passed
                    ? <CheckCircle className="w-5 h-5 text-emerald-400" />
                    : <XCircle className="w-5 h-5 text-red-400" />
                  }
                  <span className={`font-medium ${testResult.test_passed ? 'text-emerald-300' : 'text-red-300'}`}>
                    {testResult.test_passed ? 'Connection Test Passed' : 'Connection Test Failed'}
                  </span>
                </div>
                {testResult.errors.length > 0 && (
                  <ul className="mt-2 text-red-400 text-sm list-disc list-inside">
                    {testResult.errors.map((e, i) => <li key={i}>{e}</li>)}
                  </ul>
                )}
              </div>
            )}
          </div>

          {/* Configuration Guide */}
          <div className="card">
            <h2 className="font-semibold text-white mb-4">Configuration Guide</h2>
            <div className="space-y-4 text-sm">
              <div>
                <h3 className="text-blue-300 font-medium mb-2">MinIO (Local Development — Current Default)</h3>
                <div className="bg-slate-800 rounded-lg p-4 font-mono text-xs text-slate-300 space-y-1">
                  <div>STORAGE_PROVIDER=minio</div>
                  <div>MINIO_ENDPOINT=localhost:9000</div>
                  <div>MINIO_ACCESS_KEY=minioadmin</div>
                  <div>MINIO_SECRET_KEY=minioadmin123</div>
                  <div>MINIO_BUCKET=afes-encrypted-files</div>
                  <div>MINIO_SECURE=false</div>
                </div>
                <p className="text-slate-400 mt-2">Start MinIO: <code className="bg-slate-800 px-1 rounded">docker compose up minio -d</code></p>
              </div>
              <div>
                <h3 className="text-amber-300 font-medium mb-2">AWS S3 (Production)</h3>
                <div className="bg-slate-800 rounded-lg p-4 font-mono text-xs text-slate-300 space-y-1">
                  <div>STORAGE_PROVIDER=s3</div>
                  <div>AWS_ACCESS_KEY_ID=YOUR_KEY</div>
                  <div>AWS_SECRET_ACCESS_KEY=YOUR_SECRET</div>
                  <div>AWS_REGION=us-east-1</div>
                  <div>S3_BUCKET=your-afes-bucket</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatusCard({ icon, label, ok, sub }: { icon: React.ReactNode; label: string; ok: boolean; sub?: string }) {
  return (
    <div className={`p-4 rounded-lg border ${ok ? 'bg-emerald-900/10 border-emerald-800' : 'bg-red-900/10 border-red-800'}`}>
      <div className="flex items-center gap-2 mb-1">
        {icon}
        <span className="text-white font-medium text-sm">{label}</span>
        {ok ? <CheckCircle className="w-4 h-4 text-emerald-400 ml-auto" /> : <XCircle className="w-4 h-4 text-red-400 ml-auto" />}
      </div>
      {sub && <div className="text-xs text-slate-400">{sub}</div>}
    </div>
  );
}

function InfoBox({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-slate-800 rounded-lg p-3">
      <div className="text-xs text-slate-400 mb-1">{label}</div>
      <div className="text-white text-sm font-medium break-all">{value}</div>
    </div>
  );
}

function formatBytes(bytes: number) {
  if (bytes === 0) return '0 B';
  const k = 1024, sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}
