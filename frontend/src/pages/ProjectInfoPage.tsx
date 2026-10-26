import React from 'react';
import { 
  Shield, Lock, Cloud, Server, Database, Key, CheckCircle, 
  AlertTriangle, BookOpen, Layers, Cpu, FileCheck, ArrowRight
} from 'lucide-react';

export default function ProjectInfoPage() {
  return (
    <div className="p-8 max-w-5xl mx-auto space-y-10">
      {/* Title & Abstract */}
      <div className="border-b border-slate-800 pb-8">
        <div className="inline-flex items-center gap-2 bg-blue-900/30 border border-blue-800 rounded-full px-4 py-1.5 mb-4 text-blue-300 text-xs font-semibold uppercase tracking-wider">
          College Mini Project Specification
        </div>
        <h1 className="text-4xl font-extrabold text-white tracking-tight">
          Authenticated File Encryption System (AFES)
        </h1>
        <p className="text-slate-400 mt-3 text-lg leading-relaxed">
          A secure, cloud-native storage architecture combining client/server authenticated cryptography, 
          pluggable cloud object storage (AWS S3 & MinIO), role-based identity management, and comprehensive audit telemetry.
        </p>
      </div>

      {/* Abstract & Objectives */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-9 h-9 bg-blue-900/50 rounded-lg flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-blue-400" />
            </div>
            <h2 className="text-xl font-semibold text-white">Project Abstract</h2>
          </div>
          <p className="text-slate-300 text-sm leading-relaxed">
            As organizations migrate sensitive records to public cloud infrastructures, standard perimeter defenses are insufficient.
            AFES demonstrates defense-in-depth: prior to storing any payload into cloud buckets, the backend application cryptographically 
            binds ownership attributes and encrypts the file using AES-256-GCM under an envelope encryption model. Cloud object stores retain
            only ciphertexts, guaranteeing confidentiality even in the event of unauthorized storage bucket exposure.
          </p>
        </div>

        <div className="card">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-9 h-9 bg-emerald-900/50 rounded-lg flex items-center justify-center">
              <FileCheck className="w-5 h-5 text-emerald-400" />
            </div>
            <h2 className="text-xl font-semibold text-white">Core Objectives</h2>
          </div>
          <ul className="space-y-2.5 text-sm text-slate-300">
            <li className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
              <span>Genuinely encrypt arbitrary binary payloads using AES-256-GCM with fresh nonces.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
              <span>Implement envelope encryption: wrap unique Data Encryption Keys (DEKs) under a Master Key.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
              <span>Modular cloud storage abstraction compatible with AWS S3 and local MinIO.</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
              <span>Strict zero-trust server-side authorization ensuring complete cross-user file isolation.</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Technology Stack Grid */}
      <div className="card">
        <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-3">
          <Layers className="w-5 h-5 text-blue-400" />
          Technical Stack
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-4 bg-slate-800/60 rounded-lg border border-slate-700/50">
            <div className="text-blue-400 text-xs font-semibold uppercase tracking-wider mb-1">Frontend</div>
            <div className="text-white font-medium">React 18 + TypeScript</div>
            <div className="text-slate-400 text-xs mt-1">Vite, Tailwind CSS, Lucide Icons, Axios</div>
          </div>
          <div className="p-4 bg-slate-800/60 rounded-lg border border-slate-700/50">
            <div className="text-purple-400 text-xs font-semibold uppercase tracking-wider mb-1">Backend</div>
            <div className="text-white font-medium">FastAPI (Python 3.12+)</div>
            <div className="text-slate-400 text-xs mt-1">Asynchronous REST, Pydantic v2 validation</div>
          </div>
          <div className="p-4 bg-slate-800/60 rounded-lg border border-slate-700/50">
            <div className="text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-1">Cryptography</div>
            <div className="text-white font-medium">AES-256-GCM + Argon2id</div>
            <div className="text-slate-400 text-xs mt-1">Python Cryptography library, Envelope keys</div>
          </div>
          <div className="p-4 bg-slate-800/60 rounded-lg border border-slate-700/50">
            <div className="text-amber-400 text-xs font-semibold uppercase tracking-wider mb-1">Cloud & Storage</div>
            <div className="text-white font-medium">Boto3 S3 / MinIO</div>
            <div className="text-slate-400 text-xs mt-1">SQLAlchemy ORM, SQLite & PostgreSQL</div>
          </div>
        </div>
      </div>

      {/* 10 Real Cloud Computing Concepts */}
      <div>
        <h2 className="text-2xl font-bold text-white mb-2 flex items-center gap-2">
          <Cpu className="w-6 h-6 text-blue-400" />
          Demonstrated Cloud Computing Concepts
        </h2>
        <p className="text-slate-400 text-sm mb-6">
          AFES maps theoretical cloud computing principles to tangible software components.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            {
              title: "1. Object Storage Paradigm",
              desc: "Files are not saved on a POSIX filesystem path, but as immutable binary objects identified by unique keys inside partitioned cloud buckets.",
              tag: "Implemented: S3 & MinIO"
            },
            {
              title: "2. Identity & Access Management (IAM)",
              desc: "Principles of least privilege: authenticated JWT subjects determine authorized operations. No client-supplied owner IDs are ever trusted.",
              tag: "Implemented: Server Authorization"
            },
            {
              title: "3. Stateless REST Architecture",
              desc: "API compute instances hold zero local session state. Requests are authenticated on-the-fly, allowing instant horizontal scaling behind load balancers.",
              tag: "Implemented: FastAPI REST"
            },
            {
              title: "4. Cloud Resource Abstraction",
              desc: "Decoupling application code from vendor APIs through an abstract StorageProvider interface, enabling switching between AWS S3, MinIO, or GCP.",
              tag: "Implemented: Storage Factory"
            },
            {
              title: "5. Encryption at Rest & In Transit",
              desc: "All network traffic is encrypted via HTTPS/TLS. Payload data undergoes authenticated AES-GCM encryption before entering cloud buckets.",
              tag: "Implemented: AES-256-GCM"
            },
            {
              title: "6. Envelope Key Hierarchy",
              desc: "Individual files use distinct ephemeral Data Encryption Keys (DEKs) wrapped by a Master Key Encryption Key (KEK), ready for AWS KMS.",
              tag: "Implemented: Envelope Design"
            },
            {
              title: "7. Cloud Observability & Telemetry",
              desc: "Auditable structured event trails capture authentication attempts, uploads, downloads, and tamper rejections without leaking secrets.",
              tag: "Implemented: Audit Engine"
            },
            {
              title: "8. Availability & Fault Recovery",
              desc: "Dynamic health-checking probes and graceful degradation handle transient cloud disconnects, network timeouts, and storage unreachability.",
              tag: "Implemented: Health Endpoints"
            },
            {
              title: "9. Microservice Containerization",
              desc: "Docker and Docker Compose definitions package backend, frontend, database, and local cloud simulators into reproducible deployment units.",
              tag: "Implemented: Docker Compose"
            },
            {
              title: "10. Multi-Tenancy & Data Segregation",
              desc: "Logical namespace separation enforces that Tenant A cannot discover, enumerate, download, or tamper with Tenant B's encrypted objects.",
              tag: "Implemented: User Isolation"
            }
          ].map((item, idx) => (
            <div key={idx} className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-white font-semibold text-sm">{item.title}</h3>
                  <span className="text-[10px] bg-blue-900/40 text-blue-300 border border-blue-800 px-2 py-0.5 rounded-full font-mono">
                    {item.tag}
                  </span>
                </div>
                <p className="text-slate-400 text-xs leading-relaxed">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Security Limitations & Production Evolution */}
      <div className="card bg-slate-900/50 border-amber-800/40">
        <div className="flex items-center gap-3 mb-3">
          <AlertTriangle className="w-5 h-5 text-amber-400" />
          <h2 className="text-lg font-semibold text-amber-200">Security Limitations & Academic Disclaimer</h2>
        </div>
        <div className="text-slate-300 text-sm space-y-3 leading-relaxed">
          <p>
            AFES was engineered as an educational Cloud Computing engineering project. While it implements standard 
            primitives (AES-256-GCM, Argon2id, envelope wrapping), the following operational nuances differentiate 
            it from commercial enterprise systems:
          </p>
          <ul className="list-disc list-inside space-y-1 text-slate-400 text-xs">
            <li><strong>Key Storage:</strong> In this local demo, the Master KEK resides in environment variables. In enterprise environments, AWS KMS or HashiCorp Vault with Hardware Security Modules (HSM) must be used.</li>
            <li><strong>Transport Security:</strong> In local testing, plain HTTP is accepted. Production instances must be enforced via TLS/HTTPS certificates behind CloudFront or an Application Load Balancer.</li>
            <li><strong>Key Rotation:</strong> Automatic envelope key rotation pipelines should be scheduled in production to minimize blast radius.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
