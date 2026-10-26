import React, { useEffect, useState } from 'react';
import { filesApi } from '../api/files';
import type { FileRecord } from '../types';
import { Download, Trash2, Lock, Search, AlertCircle, Files, Shield, AlertTriangle, CheckCircle } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { getErrorMessage } from '../api/client';
import toast from 'react-hot-toast';

function formatBytes(bytes: number) {
  if (!bytes) return '—';
  const k = 1024, sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export default function MyFilesPage() {
  const [files, setFiles] = useState<FileRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [decryptingId, setDecryptingId] = useState<number | null>(null);
  const [tamperTestId, setTamperTestId] = useState<number | null>(null);
  const [tamperResult, setTamperResult] = useState<{ id: number; detected: boolean; message: string } | null>(null);

  const loadFiles = async () => {
    try {
      const res = await filesApi.list();
      setFiles(res.data.files);
    } catch (e) {
      toast.error('Failed to load files');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadFiles(); }, []);

  const filtered = files.filter(f =>
    f.original_filename.toLowerCase().includes(search.toLowerCase())
  );

  const handleDownload = async (file: FileRecord) => {
    setDecryptingId(file.id);
    try {
      const res = await filesApi.decrypt(file.id);
      const blob = new Blob([res.data], { type: file.content_type || 'application/octet-stream' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = file.original_filename; a.click();
      URL.revokeObjectURL(url);
      toast.success('File decrypted and downloaded');
    } catch (e) {
      toast.error(getErrorMessage(e));
    } finally {
      setDecryptingId(null);
    }
  };

  const handleDelete = async (file: FileRecord) => {
    if (!confirm(`Delete "${file.original_filename}"? This will also remove it from cloud storage.`)) return;
    setDeletingId(file.id);
    try {
      await filesApi.delete(file.id);
      setFiles(f => f.filter(x => x.id !== file.id));
      toast.success('File deleted');
    } catch (e) {
      toast.error(getErrorMessage(e));
    } finally {
      setDeletingId(null);
    }
  };

  const handleTamperTest = async (file: FileRecord) => {
    setTamperTestId(file.id);
    try {
      const res = await filesApi.tamperTest(file.id);
      setTamperResult({ id: file.id, detected: res.data.tamper_detected, message: res.data.message });
      toast.success(res.data.tamper_detected ? '✓ Tampering correctly detected!' : '⚠ Tampering not detected');
    } catch (e) {
      toast.error(getErrorMessage(e));
    } finally {
      setTamperTestId(null);
    }
  };

  if (loading) return (
    <div className="p-8 flex justify-center">
      <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="p-8 max-w-7xl mx-auto">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">My Files</h1>
          <p className="text-slate-400 mt-1">{files.length} encrypted {files.length === 1 ? 'file' : 'files'} in your vault</p>
        </div>
        <a href="/encrypt" className="btn-primary flex items-center gap-2">
          <Lock className="w-4 h-4" /> Encrypt New File
        </a>
      </div>

      {/* Search */}
      {files.length > 0 && (
        <div className="relative mb-6">
          <Search className="absolute left-3 top-3.5 w-4 h-4 text-slate-400" />
          <input value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Search files..." className="input-field pl-10 max-w-sm" />
        </div>
      )}

      {/* Tamper test result */}
      {tamperResult && (
        <div className={`mb-4 p-4 rounded-lg border flex items-start gap-3 ${
          tamperResult.detected
            ? 'bg-emerald-900/20 border-emerald-800'
            : 'bg-red-900/20 border-red-800'
        }`}>
          {tamperResult.detected
            ? <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
            : <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          }
          <div>
            <div className="font-medium text-sm">{tamperResult.detected ? '✓ Tamper Detection Confirmed' : '⚠ Tamper Not Detected'}</div>
            <div className="text-xs text-slate-400 mt-1">{tamperResult.message}</div>
          </div>
          <button onClick={() => setTamperResult(null)} className="ml-auto text-slate-400 hover:text-white">✕</button>
        </div>
      )}

      {/* File table */}
      {filtered.length === 0 ? (
        <div className="card text-center py-16">
          <Files className="w-12 h-12 mx-auto mb-3 text-slate-600" />
          <p className="text-slate-400 mb-2">{search ? 'No files match your search' : 'No encrypted files yet'}</p>
          {!search && (
            <a href="/encrypt" className="text-blue-400 hover:text-blue-300 text-sm">Encrypt your first file →</a>
          )}
        </div>
      ) : (
        <div className="card overflow-hidden p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-800">
                  {['Filename', 'Size', 'Algorithm', 'Provider', 'Uploaded', 'Actions'].map(h => (
                    <th key={h} className="text-left text-xs font-medium text-slate-400 px-4 py-3">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {filtered.map(file => (
                  <tr key={file.id} className="hover:bg-slate-800/50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <Lock className="w-4 h-4 text-blue-400 flex-shrink-0" />
                        <div>
                          <div className="text-white font-medium">{file.original_filename}</div>
                          <div className="text-slate-500 text-xs font-mono">{file.encrypted_object_key.slice(0, 30)}...</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-300">{formatBytes(file.original_size)}</td>
                    <td className="px-4 py-3">
                      <span className="badge-info"><Shield className="w-3 h-3" />{file.encryption_algorithm}</span>
                    </td>
                    <td className="px-4 py-3 text-slate-400">{file.storage_provider}</td>
                    <td className="px-4 py-3 text-slate-400 text-xs">
                      {formatDistanceToNow(new Date(file.upload_timestamp), { addSuffix: true })}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleDownload(file)}
                          disabled={decryptingId === file.id}
                          title="Decrypt & Download"
                          className="p-1.5 text-slate-400 hover:text-emerald-400 disabled:opacity-50 transition-colors"
                        >
                          {decryptingId === file.id
                            ? <div className="w-4 h-4 border border-slate-400 border-t-transparent rounded-full animate-spin" />
                            : <Download className="w-4 h-4" />
                          }
                        </button>
                        <button
                          onClick={() => handleTamperTest(file)}
                          disabled={tamperTestId === file.id}
                          title="Tamper Test (Demo)"
                          className="p-1.5 text-slate-400 hover:text-amber-400 disabled:opacity-50 transition-colors"
                        >
                          {tamperTestId === file.id
                            ? <div className="w-4 h-4 border border-slate-400 border-t-transparent rounded-full animate-spin" />
                            : <AlertTriangle className="w-4 h-4" />
                          }
                        </button>
                        <button
                          onClick={() => handleDelete(file)}
                          disabled={deletingId === file.id}
                          title="Delete"
                          className="p-1.5 text-slate-400 hover:text-red-400 disabled:opacity-50 transition-colors"
                        >
                          {deletingId === file.id
                            ? <div className="w-4 h-4 border border-red-400 border-t-transparent rounded-full animate-spin" />
                            : <Trash2 className="w-4 h-4" />
                          }
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
