import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, Lock, CheckCircle, AlertCircle, Cloud, X, Shield } from 'lucide-react';
import { filesApi } from '../api/files';
import { getErrorMessage } from '../api/client';
import type { EncryptResponse } from '../types';
import toast from 'react-hot-toast';

function formatBytes(bytes: number) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

type Stage = 'idle' | 'encrypting' | 'uploading' | 'done' | 'error';

export default function EncryptFilePage() {
  const [file, setFile] = useState<File | null>(null);
  const [stage, setStage] = useState<Stage>('idle');
  const [uploadPct, setUploadPct] = useState(0);
  const [result, setResult] = useState<EncryptResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((accepted: File[]) => {
    if (accepted[0]) {
      setFile(accepted[0]);
      setStage('idle');
      setResult(null);
      setError(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: false,
    maxSize: 100 * 1024 * 1024, // 100 MB
  });

  const handleEncrypt = async () => {
    if (!file) return;
    setStage('encrypting');
    setError(null);
    setUploadPct(0);

    try {
      // Brief artificial delay to show "encrypting" step (actual encryption happens server-side during upload)
      await new Promise(r => setTimeout(r, 600));
      setStage('uploading');
      const res = await filesApi.encrypt(file, setUploadPct);
      setResult(res.data);
      setStage('done');
      toast.success('File encrypted and uploaded!');
    } catch (err) {
      setStage('error');
      const msg = getErrorMessage(err);
      setError(msg);
      toast.error(msg);
    }
  };

  const handleReset = () => {
    setFile(null);
    setStage('idle');
    setResult(null);
    setError(null);
    setUploadPct(0);
  };

  return (
    <div className="p-8 max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Encrypt File</h1>
        <p className="text-slate-400 mt-1">Upload a file to encrypt with AES-256-GCM and store in cloud storage</p>
      </div>

      {/* Algorithm Info */}
      <div className="flex gap-3 mb-6">
        <div className="flex items-center gap-2 bg-blue-900/30 border border-blue-800 rounded-lg px-3 py-2 text-sm">
          <Lock className="w-4 h-4 text-blue-400" />
          <span className="text-blue-300 font-medium">AES-256-GCM</span>
        </div>
        <div className="flex items-center gap-2 bg-emerald-900/30 border border-emerald-800 rounded-lg px-3 py-2 text-sm">
          <Shield className="w-4 h-4 text-emerald-400" />
          <span className="text-emerald-300">Envelope Encryption</span>
        </div>
        <div className="flex items-center gap-2 bg-purple-900/30 border border-purple-800 rounded-lg px-3 py-2 text-sm">
          <Cloud className="w-4 h-4 text-purple-400" />
          <span className="text-purple-300">Cloud Storage</span>
        </div>
      </div>

      {/* Dropzone */}
      {!result && (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all ${
            isDragActive
              ? 'border-blue-500 bg-blue-900/20'
              : 'border-slate-700 hover:border-slate-600 bg-slate-900/50'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="w-12 h-12 text-slate-500 mx-auto mb-4" />
          <p className="text-white font-medium mb-1">
            {isDragActive ? 'Drop your file here' : 'Drag & drop a file here'}
          </p>
          <p className="text-slate-400 text-sm">or click to browse — max 100 MB</p>
          <p className="text-slate-500 text-xs mt-2">Supports any file type: PDF, DOCX, images, ZIP, CSV, etc.</p>
        </div>
      )}

      {/* File selected */}
      {file && !result && (
        <div className="mt-4 p-4 bg-slate-800 rounded-xl border border-slate-700">
          <div className="flex items-start gap-3">
            <div className="w-10 h-10 bg-blue-900 rounded-lg flex items-center justify-center flex-shrink-0">
              <File className="w-5 h-5 text-blue-400" />
            </div>
            <div className="flex-1">
              <div className="text-white font-medium">{file.name}</div>
              <div className="text-slate-400 text-sm">{formatBytes(file.size)} • {file.type || 'unknown type'}</div>
            </div>
            <button onClick={handleReset} className="text-slate-400 hover:text-red-400 transition-colors">
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Progress */}
      {(stage === 'encrypting' || stage === 'uploading') && (
        <div className="mt-6 p-5 bg-slate-900 border border-slate-800 rounded-xl">
          <div className="space-y-4">
            <Step label="Encrypting with AES-256-GCM" done={stage === 'uploading'} active={stage === 'encrypting'} />
            <Step label={`Uploading to cloud storage${uploadPct > 0 ? ` (${uploadPct}%)` : ''}`} done={false} active={stage === 'uploading'} />
            <Step label="Saving metadata" done={false} active={false} />
          </div>
          {stage === 'uploading' && uploadPct > 0 && (
            <div className="mt-4">
              <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 rounded-full transition-all" style={{ width: `${uploadPct}%` }} />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error */}
      {stage === 'error' && error && (
        <div className="mt-4 p-4 bg-red-900/20 border border-red-800 rounded-xl flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <div className="text-red-300 font-medium">Encryption failed</div>
            <div className="text-red-400 text-sm mt-1">{error}</div>
          </div>
        </div>
      )}

      {/* Success */}
      {result && (
        <div className="mt-6 p-6 bg-emerald-900/10 border border-emerald-800 rounded-xl">
          <div className="flex items-center gap-3 mb-5">
            <CheckCircle className="w-6 h-6 text-emerald-400" />
            <h2 className="text-emerald-300 font-semibold text-lg">Successfully Encrypted & Uploaded!</h2>
          </div>
          <div className="grid grid-cols-1 gap-3 text-sm">
            <Row label="Original Filename" value={result.original_filename} />
            <Row label="File ID" value={`#${result.file_id}`} />
            <Row label="Original Size" value={formatBytes(result.original_size)} />
            <Row label="Encrypted Size" value={formatBytes(result.encrypted_size)} />
            <Row label="Encryption Algorithm" value={result.encryption_algorithm} highlight />
            <Row label="Storage Provider" value={result.storage_provider} />
            <Row label="Object Key" value={result.encrypted_object_key} mono />
          </div>
          <div className="mt-5 flex gap-3">
            <button onClick={handleReset} className="btn-primary">Encrypt Another File</button>
            <a href="/files" className="btn-secondary">View My Files</a>
          </div>
        </div>
      )}

      {/* Encrypt button */}
      {file && stage === 'idle' && (
        <button onClick={handleEncrypt} className="mt-6 btn-primary w-full py-3 flex items-center justify-center gap-2 text-base">
          <Lock className="w-5 h-5" />
          Encrypt & Upload File
        </button>
      )}
    </div>
  );
}

function Step({ label, done, active }: { label: string; done: boolean; active: boolean }) {
  return (
    <div className="flex items-center gap-3">
      {done ? (
        <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0" />
      ) : active ? (
        <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin flex-shrink-0" />
      ) : (
        <div className="w-5 h-5 rounded-full border-2 border-slate-600 flex-shrink-0" />
      )}
      <span className={`text-sm ${done ? 'text-emerald-400' : active ? 'text-blue-300' : 'text-slate-500'}`}>{label}</span>
    </div>
  );
}

function Row({ label, value, highlight, mono }: { label: string; value: string; highlight?: boolean; mono?: boolean }) {
  return (
    <div className="flex items-start gap-2 py-2 border-b border-slate-800 last:border-0">
      <span className="text-slate-400 w-40 flex-shrink-0">{label}</span>
      <span className={`font-medium break-all ${highlight ? 'text-emerald-400' : 'text-white'} ${mono ? 'font-mono text-xs' : ''}`}>
        {value}
      </span>
    </div>
  );
}
