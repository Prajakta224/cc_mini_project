import React, { useState } from 'react';
import { 
  Users, Shield, Lock, Cloud, Activity, CheckSquare, 
  Play, MessageSquare, Terminal, AlertCircle, ChevronRight, CheckCircle, FileText
} from 'lucide-react';
import { Link } from 'react-router-dom';

export default function DemoPage() {
  const [activeTab, setActiveTab] = useState<number>(1);

  const students = [
    {
      id: 1,
      role: "Student 1",
      topic: "Authentication & Access Control",
      icon: Shield,
      color: "text-blue-400",
      border: "border-blue-500",
      bg: "bg-blue-900/20",
      summary: "User registration, Argon2id password hashing, stateless JWT authentication, and strict multi-tenant access control preventing cross-user file breaches.",
      checklist: [
        "Open Registration form and demonstrate input validation (password strength & mismatch).",
        "Explain that passwords are never stored in plaintext — inspect database Argon2id hashes.",
        "Log in as Alice (alice@afes.demo) and observe the issued JWT session.",
        "Demonstrate accessing protected dashboard endpoints.",
        "Log in as Bob (bob@afes.demo) in an incognito window or alternate session.",
        "Attempt to query or decrypt Alice's file IDs and observe the server-side 403 Forbidden rejection.",
        "Review how server-side ownership checks derive identity strictly from the JWT sub claim."
      ],
      script: `"Good morning examiners. I will be demonstrating the Authentication & Access Control layer of AFES.

In cloud multi-tenant applications, perimeter security alone is insufficient. We implemented password hashing using Argon2id, the state-of-the-art memory-hard hashing algorithm resistant to GPU and ASIC brute-force attacks.

When a user signs in, the FastAPI backend validates the hash and produces a signed JSON Web Token (JWT). Every subsequent API request carries this bearer token. Crucially, our authorization policy is strictly enforced on the server: even if User B attempts to tamper with request parameters to request User A's file, our backend intercepts the request, verifies ownership against the database, rejects the call with HTTP 403 Forbidden, and records a security audit event."`,
      links: [
        { label: "Go to Registration", to: "/register" },
        { label: "Go to Login", to: "/login" },
        { label: "Audit Log (Unauthorized Attempts)", to: "/audit" }
      ]
    },
    {
      id: 2,
      role: "Student 2",
      topic: "Cryptographic File Protection",
      icon: Lock,
      color: "text-purple-400",
      border: "border-purple-500",
      bg: "bg-purple-900/20",
      summary: "Client-to-server authenticated file encryption with AES-256-GCM, per-file Data Encryption Keys (DEKs), envelope encryption, and cryptographic tamper detection.",
      checklist: [
        "Select a sample document (PDF, TXT, or image) on the Encrypt File page.",
        "Inspect original filename, MIME type, and size in the UI preview.",
        "Execute encryption and show the AES-256-GCM algorithm badge.",
        "Explain the Envelope Encryption design: random 256-bit DEK generated per file, encrypted under Master KEK.",
        "Demonstrate downloading and decrypting the original plaintext file successfully.",
        "Execute the live 'Tamper Test' on an encrypted file to demonstrate how AES-GCM's 128-bit authentication tag detects bit-level manipulation and aborts decryption.",
        "Explain why authenticated additional data (AAD) binds user ownership and filename directly to ciphertext."
      ],
      script: `"Respected faculty, my module covers File Encryption & Cryptographic Integrity.

Rather than relying on basic storage-level encryption, AFES implements application-level authenticated encryption using AES-256-GCM with a fresh 96-bit cryptographically random nonce for every upload. 

To manage keys securely at scale, we use Envelope Encryption: each file receives its own 32-byte Data Encryption Key (DEK). This DEK encrypts the payload, and is then itself wrapped using our Master Key Encryption Key (KEK). Furthermore, we bind metadata—including the user's ID and filename—as Authenticated Additional Data (AAD). 

As shown in our live tamper test, if an attacker alters even a single bit of the stored ciphertext or attempts to associate the ciphertext with a different user, the GCM authentication tag verification fails immediately, and the backend refuses to return compromised data."`,
      links: [
        { label: "Encrypt a Sample File", to: "/encrypt" },
        { label: "My Files & Live Tamper Test", to: "/files" }
      ]
    },
    {
      id: 3,
      role: "Student 3",
      topic: "Cloud Object Storage & Abstraction",
      icon: Cloud,
      color: "text-emerald-400",
      border: "border-emerald-500",
      bg: "bg-emerald-900/20",
      summary: "Pluggable S3-compatible cloud storage architecture supporting AWS S3 and local MinIO with private bucket policies, object lifecycle, and zero plaintext exposure.",
      checklist: [
        "Open Cloud Infrastructure page and verify the active storage provider status.",
        "Highlight that our system is running locally via MinIO (S3-compatible) or AWS S3.",
        "Inspect the assigned object key structure: users/{user_id}/{unique_hash}_{filename}.enc",
        "Confirm that only encrypted ciphertext is written to the cloud bucket, never plaintext.",
        "Demonstrate the live Storage Connectivity probe (upload, read, delete test object).",
        "Perform a file deletion and show the coordinated removal from both database and cloud object store.",
        "Explain how the abstract StorageProvider interface allows switching providers with zero code changes."
      ],
      script: `"Hello everyone. I will be presenting the Cloud Object Storage integration and Provider Abstraction in AFES.

Cloud object storage differs fundamentally from traditional block or filesystem storage. In AFES, objects are addressed immutably via unique resource keys inside private buckets. 

We engineered a modular StorageProvider abstraction layer in Python. For local offline development and academic demonstration, we connect to an S3-compatible MinIO service using Boto3. By toggling environment variables, the exact same codebase communicates natively with Amazon Web Services S3 with Server-Side Encryption (SSE) and strict Public Access Blocks.

Crucially, zero plaintext ever reaches the storage provider. Even if a cloud bucket was inadvertently misconfigured to be public, an adversary would only retrieve encrypted bytes without the wrapped data keys."`,
      links: [
        { label: "Cloud Infrastructure Status", to: "/cloud" },
        { label: "View Stored Files", to: "/files" }
      ]
    },
    {
      id: 4,
      role: "Student 4",
      topic: "Observability, Architecture & Deployment",
      icon: Activity,
      color: "text-amber-400",
      border: "border-amber-500",
      bg: "bg-amber-900/20",
      summary: "System health monitoring, audit trail telemetry, microservice containerization with Docker Compose, and scalability analysis.",
      checklist: [
        "Review the Audit Log page showing real-time timestamps, IP addresses, and event classifications.",
        "Verify that audit logs never record passwords, encryption keys, tokens, or plaintext payload data.",
        "Show the FastAPI automated documentation (/api/docs Swagger UI).",
        "Review the health probe endpoint (/api/health) showing API status and database responsiveness.",
        "Explain how Docker Compose orchestrates the frontend, backend, database, and MinIO containers.",
        "Discuss cloud horizontal scalability: how stateless FastAPI workers scale behind cloud load balancers.",
        "Discuss failure handling: how AFES handles storage downtime and network partition errors."
      ],
      script: `"Examiners, I will be presenting System Observability, Cloud Architecture, and Deployment.

Reliable cloud architectures require end-to-end observability and resilient deployment. AFES maintains an immutable audit log recording all critical events: user registrations, authentications, file uploads, decryption actions, and unauthorized intrusion attempts. In adherence to privacy-by-design standards, sensitive keys and credentials are systematically sanitized from telemetry.

Our deployment architecture is fully containerized using Docker and Docker Compose. Because our FastAPI backend instances are completely stateless, multiple worker containers can sit behind an AWS Application Load Balancer, sharing the common SQL database and S3 bucket for horizontal elasticity.

We also expose standardized health probes suitable for Kubernetes liveness and readiness monitoring."`,
      links: [
        { label: "Open Audit Log", to: "/audit" },
        { label: "System Health & Cloud Probes", to: "/cloud" },
        { label: "Interactive Architecture Diagram", to: "/project" }
      ]
    }
  ];

  const current = students.find(s => s.id === activeTab) || students[0];

  return (
    <div className="p-8 max-w-5xl mx-auto space-y-8">
      <div>
        <div className="inline-flex items-center gap-2 bg-purple-900/30 border border-purple-800 rounded-full px-4 py-1.5 mb-3 text-purple-300 text-xs font-semibold uppercase tracking-wider">
          Live Presentation Mode
        </div>
        <h1 className="text-3xl font-extrabold text-white">Four-Student Project Demonstration</h1>
        <p className="text-slate-400 text-sm mt-1">
          A structured, sequential presentation guide dividing AFES across 4 team members with checklists, talking points, and scripts.
        </p>
      </div>

      {/* Student selector tabs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {students.map((s) => {
          const Icon = s.icon;
          const isActive = s.id === activeTab;
          return (
            <button
              key={s.id}
              onClick={() => setActiveTab(s.id)}
              className={`p-4 rounded-xl border text-left transition-all ${
                isActive 
                  ? `bg-slate-900 ${s.border} ring-1 ring-blue-500/50 shadow-lg` 
                  : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">{s.role}</span>
                <Icon className={`w-4 h-4 ${s.color}`} />
              </div>
              <div className="text-sm font-semibold text-white leading-snug">{s.topic}</div>
            </button>
          );
        })}
      </div>

      {/* Selected Student Card */}
      <div className="card space-y-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-800 gap-3">
          <div>
            <div className="flex items-center gap-2">
              <span className={`text-xs px-2.5 py-1 rounded-full font-bold uppercase tracking-wider ${current.bg} ${current.color}`}>
                {current.role}
              </span>
              <h2 className="text-2xl font-bold text-white">{current.topic}</h2>
            </div>
            <p className="text-slate-300 text-sm mt-2">{current.summary}</p>
          </div>
        </div>

        {/* Action Checklist */}
        <div>
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-3 flex items-center gap-2">
            <CheckSquare className="w-4 h-4 text-emerald-400" />
            Live Demonstration Checklist
          </h3>
          <div className="space-y-2 bg-slate-950/60 p-4 rounded-xl border border-slate-800">
            {current.checklist.map((item, idx) => (
              <div key={idx} className="flex items-start gap-3 text-sm text-slate-300">
                <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                <span>{item}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Speaking Script */}
        <div>
          <h3 className="text-sm font-semibold text-white uppercase tracking-wider mb-3 flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-blue-400" />
            Recommended Speaking Script & Talking Points
          </h3>
          <div className="p-4 bg-slate-800/40 border border-slate-700/50 rounded-xl text-slate-300 text-sm whitespace-pre-line leading-relaxed font-sans">
            {current.script}
          </div>
        </div>

        {/* Quick Links for this student */}
        <div>
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
            Quick Navigation For Demonstration
          </h3>
          <div className="flex flex-wrap gap-3">
            {current.links.map((link, idx) => (
              <Link
                key={idx}
                to={link.to}
                className="btn-secondary text-xs flex items-center gap-1.5 py-2 px-3 hover:text-blue-300"
              >
                <span>{link.label}</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
