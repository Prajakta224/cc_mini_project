import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Lock, Cloud, Activity, ArrowRight, Server, Database, Key, CheckCircle } from 'lucide-react';

function ArchitectureDiagram() {
  const boxes = [
    { label: 'User Browser', color: 'border-blue-700 bg-blue-950' },
    { label: 'React Frontend\n(Vite + TypeScript)', color: 'border-blue-600 bg-blue-900/40' },
    { label: 'FastAPI Backend\n(Python)', color: 'border-purple-600 bg-purple-900/30' },
    { label: 'Cloud Storage\n(S3 / MinIO)', color: 'border-emerald-600 bg-emerald-900/30' },
  ];
  const services = [
    { label: 'Auth + JWT', icon: Shield },
    { label: 'AES-256-GCM', icon: Lock },
    { label: 'Key Manager', icon: Key },
    { label: 'Audit Log', icon: Activity },
    { label: 'SQLite / PostgreSQL', icon: Database },
  ];

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-2xl p-8">
      <div className="flex flex-col items-center gap-3">
        {/* User */}
        <div className="border border-blue-700 bg-blue-950 rounded-xl px-8 py-3 text-blue-300 font-medium">
          🌐 User Browser
        </div>
        <Arrow label="HTTPS in production" />
        {/* Frontend */}
        <div className="border border-blue-600 bg-blue-900/40 rounded-xl px-8 py-3 text-blue-200 font-medium text-center">
          ⚛️ React Frontend<br /><span className="text-xs text-blue-400">Vite + TypeScript + Tailwind</span>
        </div>
        <Arrow label="Authenticated REST API" />
        {/* Backend */}
        <div className="border-2 border-purple-600 bg-purple-900/20 rounded-xl px-8 py-4 w-full max-w-lg">
          <div className="text-purple-200 font-semibold text-center mb-3">🐍 FastAPI Backend</div>
          <div className="flex flex-wrap justify-center gap-2">
            {services.map(({ label, icon: Icon }) => (
              <div key={label} className="flex items-center gap-1 bg-purple-900/40 border border-purple-700 rounded-lg px-2 py-1 text-xs text-purple-300">
                <Icon className="w-3 h-3" /> {label}
              </div>
            ))}
          </div>
        </div>
        <Arrow label="Encrypted objects only" />
        {/* Storage */}
        <div className="flex gap-4">
          <div className="border border-amber-600 bg-amber-900/20 rounded-xl px-6 py-3 text-amber-200 font-medium text-center text-sm">
            ☁️ AWS S3<br /><span className="text-xs text-amber-400">Production</span>
          </div>
          <div className="border border-emerald-600 bg-emerald-900/20 rounded-xl px-6 py-3 text-emerald-200 font-medium text-center text-sm">
            📦 MinIO<br /><span className="text-xs text-emerald-400">Local Demo</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function Arrow({ label }: { label: string }) {
  return (
    <div className="flex flex-col items-center">
      <div className="w-px h-4 bg-slate-600" />
      <div className="text-xs text-slate-500 px-2 py-0.5 bg-slate-800 border border-slate-700 rounded">{label}</div>
      <div className="text-slate-500">↓</div>
    </div>
  );
}

const FEATURES = [
  { icon: Shield, title: 'User Authentication', desc: 'Argon2id password hashing, JWT tokens, role-based access control.' },
  { icon: Lock, title: 'AES-256-GCM Encryption', desc: 'Envelope encryption with per-file unique keys. Authenticated encryption prevents tampering.' },
  { icon: Cloud, title: 'Cloud Object Storage', desc: 'AWS S3 or MinIO — encrypted objects only. Modular provider abstraction.' },
  { icon: Activity, title: 'Audit Logging', desc: 'Every security event recorded: logins, encryptions, decryptions, unauthorized access.' },
  { icon: Server, title: 'REST API', desc: 'FastAPI with OpenAPI documentation. All endpoints secured server-side.' },
  { icon: Database, title: 'Structured Database', desc: 'SQLAlchemy ORM. Users, file metadata, and audit events. SQLite for dev, PostgreSQL for prod.' },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <header className="border-b border-slate-800 sticky top-0 bg-slate-950/90 backdrop-blur z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-blue-600 rounded-lg flex items-center justify-center">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="font-bold text-white">AFES</span>
              <span className="hidden md:inline text-slate-400 text-sm ml-2">Authenticated File Encryption System</span>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login" className="btn-secondary text-sm py-1.5 px-4">Sign In</Link>
            <Link to="/register" className="btn-primary text-sm py-1.5 px-4">Get Started</Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-24 text-center">
        <div className="inline-flex items-center gap-2 bg-blue-900/30 border border-blue-800 rounded-full px-4 py-2 mb-8 text-blue-300 text-sm">
          <Lock className="w-4 h-4" /> Cloud Computing Mini Project — AES-256-GCM + S3/MinIO
        </div>
        <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
          Authenticated<br />
          <span className="text-blue-400">File Encryption</span><br />
          in the Cloud
        </h1>
        <p className="text-slate-300 text-xl max-w-3xl mx-auto mb-12">
          A complete cloud security demonstration. Encrypt files with AES-256-GCM,
          store ciphertext in cloud object storage, and maintain a full audit trail —
          all with per-user isolation and authenticated access.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <Link to="/register" className="btn-primary py-3 px-8 text-lg flex items-center gap-2">
            Get Started <ArrowRight className="w-5 h-5" />
          </Link>
          <Link to="/login" className="btn-secondary py-3 px-8 text-lg">
            Sign In
          </Link>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-white text-center mb-12">Cloud Security Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {FEATURES.map(({ icon: Icon, title, desc }) => (
            <div key={title} className="card hover:border-slate-700 transition-colors">
              <div className="w-10 h-10 bg-blue-900/50 rounded-lg flex items-center justify-center mb-4">
                <Icon className="w-5 h-5 text-blue-400" />
              </div>
              <h3 className="text-white font-semibold mb-2">{title}</h3>
              <p className="text-slate-400 text-sm">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Architecture */}
      <section className="max-w-4xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-white text-center mb-4">System Architecture</h2>
        <p className="text-slate-400 text-center mb-10">
          The backend encrypts files before cloud object storage receives them.
          Only ciphertext is stored — never the original file.
        </p>
        <ArchitectureDiagram />
      </section>

      {/* Cloud Concepts */}
      <section className="max-w-7xl mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-white text-center mb-4">Cloud Computing Concepts</h2>
        <p className="text-slate-400 text-center mb-10">This project demonstrates real cloud computing principles</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            ['Object Storage', 'Encrypted files stored as cloud objects in S3/MinIO buckets'],
            ['Authentication & Authorization', 'JWT-based auth with server-side ownership enforcement'],
            ['REST API', 'React communicates with FastAPI through real authenticated API calls'],
            ['Scalability', 'Stateless API, shared object storage → horizontal scaling'],
            ['Provider Abstraction', 'Pluggable storage interface: swap AWS S3 for MinIO or GCS'],
            ['Data Security', 'AES-256-GCM at rest, HTTPS in transit, authenticated encryption'],
            ['Monitoring', 'Audit events, health endpoints, storage connectivity tests'],
            ['Containerization', 'Docker + Docker Compose for reproducible deployment'],
          ].map(([title, desc]) => (
            <div key={title} className="flex items-start gap-3 p-4 bg-slate-900 border border-slate-800 rounded-xl">
              <CheckCircle className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
              <div>
                <div className="text-white font-medium text-sm">{title}</div>
                <div className="text-slate-400 text-xs mt-0.5">{desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-3xl mx-auto px-6 py-16 text-center">
        <div className="card bg-gradient-to-br from-blue-900/40 to-slate-900">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to Start?</h2>
          <p className="text-slate-300 mb-8">Create an account and encrypt your first file in seconds.</p>
          <div className="flex justify-center gap-4">
            <Link to="/register" className="btn-primary py-3 px-8">Create Account</Link>
            <Link to="/login" className="btn-secondary py-3 px-8">Sign In</Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-slate-800 py-8 text-center text-slate-500 text-sm">
        AFES — Authenticated File Encryption System • Cloud Computing Mini Project • Educational Demonstration
      </footer>
    </div>
  );
}
