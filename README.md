# Authenticated File Encryption System (AFES)
### Cloud Computing Engineering Mini Project

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg)](https://www.typescriptlang.org/)
[![AES-256-GCM](https://img.shields.io/badge/Cryptography-AES--256--GCM-success.svg)](https://cryptography.io/)
[![Cloud Storage](https://img.shields.io/badge/Cloud%20Storage-AWS%20S3%20%7C%20MinIO-orange.svg)](https://aws.amazon.com/s3/)
[![Tests](https://img.shields.io/badge/Tests-33%20Passed-brightgreen.svg)]()

---

## 1. College Mini Project Specification

### 1.1 Project Abstract
As organizations migrate critical records to public cloud environments, traditional network perimeter defenses become insufficient. The **Authenticated File Encryption System (AFES)** provides a defense-in-depth architecture where files undergo client-to-server authenticated cryptographic transformation prior to cloud persistence. Using **AES-256-GCM** with **Envelope Encryption**, each file receives a unique, cryptographically random Data Encryption Key (DEK) wrapped by a Master Key Encryption Key (KEK). The cloud object store (AWS S3 or local MinIO) retains only ciphertexts. Strict server-side authorization enforces complete multi-tenant tenant isolation, and all operational events are recorded in an auditable telemetry log.

### 1.2 Objectives
1. **Authenticated Cryptographic Protection:** Genuine file encryption with AES-256-GCM and fresh 96-bit nonces, ensuring both confidentiality and tamper detection.
2. **Envelope Key Architecture:** Implementation of a two-tier key hierarchy (DEK wrapped by KEK) designed for seamless integration with AWS Key Management Service (AWS KMS).
3. **Pluggable Cloud Object Storage:** Modular `StorageProvider` abstraction supporting AWS S3 and offline local MinIO without changing business logic.
4. **Zero-Trust Access Control:** Multi-tenant database schema where ownership is strictly verified on the backend via signed JSON Web Tokens (JWT).
5. **Observability & Security Auditing:** Non-repudiable audit logging tracking user registrations, logins, encryptions, decryptions, and unauthorized access attempts.

### 1.3 Problem Statement
Standard cloud storage solutions often store files in plaintext or rely exclusively on vendor-managed server-side encryption (SSE), leaving files vulnerable to cloud credential leaks, bucket misconfigurations, or insider threats. Furthermore, existing educational projects frequently rely on mocked uploads or fake frontend encryption. AFES solves this by executing genuine, mathematically validated encryption and cloud object operations.

### 1.4 Proposed System & Key Modules
* **Module 1 — User Authentication & Access Control:** Argon2id password hashing, JWT stateless session issuance, and server-side RBAC.
* **Module 2 — Cryptographic Engine:** AES-256-GCM encryption, envelope key wrapping, and authenticated additional data (AAD) binding.
* **Module 3 — Cloud Storage Abstraction:** S3-compatible interface executing bucket provisioning, private object uploads, downloads, and lifecycle management.
* **Module 4 — Observability & Administration:** Real-time health probes, telemetry logs, and diagnostic tamper-detection verification.

---

## 2. Technology Stack

| Layer | Technologies | Purpose |
|---|---|---|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS v4, Lucide Icons, Axios | Responsive, high-performance security dashboard |
| **Backend** | Python 3.12+, FastAPI, Uvicorn, Pydantic v2 | Asynchronous RESTful microservice with OpenAPI specs |
| **Database** | SQLAlchemy 2.0 ORM, SQLite (WAL mode) / PostgreSQL | Persistent user, file metadata, and audit records |
| **Cryptography** | AES-256-GCM, Argon2id, Python `cryptography`, `jose` | Authenticated encryption & memory-hard password hashing |
| **Cloud Storage** | AWS S3 SDK (`boto3`), MinIO S3 API, Local Simulation | Pluggable cloud object storage |
| **DevOps** | Docker, Docker Compose, Nginx Alpine, Multi-stage builds | Reproducible container orchestration |

---

## 3. System Architecture & Diagrams

### 3.1 High-Level Architecture Diagram

```
+-----------------------------------------------------------------+
|                       USER CLIENT (Browser)                     |
|            React 18 + TypeScript + Vite + Tailwind CSS          |
+-----------------------------------------------------------------+
                               |
                               | HTTPS / Authenticated REST (JWT Bearer)
                               v
+-----------------------------------------------------------------+
|                    FASTAPI APPLICATION SERVER                   |
|                                                                 |
|  +--------------------+   +----------------------------------+  |
|  | Auth & RBAC        |   | AES-256-GCM Crypto Engine        |  |
|  | - Argon2id Hasher  |   | - 96-bit Random Nonces           |  |
|  | - JWT Mint/Verify  |   | - Envelope DEK Wrapping          |  |
|  +--------------------+   +----------------------------------+  |
|                                                                 |
|  +--------------------+   +----------------------------------+  |
|  | Audit Telemetry    |   | SQLAlchemy ORM Metadata Layer    |  |
|  | - Non-sensitive    |   | - Users, Files, Audit Events     |  |
|  +--------------------+   +----------------------------------+  |
+-----------------------------------------------------------------+
           |                                     |
           | Metadata SQL                        | Ciphertext Objects Only
           v                                     v
+--------------------+               +----------------------------+
|  SQLite / Postgres |               | Cloud Storage Abstraction  |
|  Database Engine   |               | (Abstract StorageProvider) |
+--------------------+               +----------------------------+
                                                    |
                         +--------------------------+--------------------------+
                         |                                                     |
                         v                                                     v
        +----------------------------------+                  +----------------------------------+
        |             MODE A               |                  |             MODE B               |
        |        Amazon Web Services       |                  |              MinIO               |
        |          AWS S3 Bucket           |                  |      S3-Compatible Local Dev     |
        | (Private Bucket + KMS SSE Ready) |                  | (Simulated Cloud / Offline Mode) |
        +----------------------------------+                  +----------------------------------+
```

### 3.2 Database Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USERS ||--o{ FILE_RECORDS : owns
    USERS ||--o{ AUDIT_EVENTS : triggers

    USERS {
        int id PK
        string name
        string email UK
        string password_hash
        string role "user | admin"
        boolean is_active
        datetime created_at
        datetime last_login
    }

    FILE_RECORDS {
        int id PK
        int owner_id FK
        string original_filename
        bigint original_size
        string content_type
        string encrypted_object_key UK
        bigint encrypted_size
        string encryption_algorithm "AES-256-GCM"
        int format_version
        string nonce_hex
        string encrypted_dek_hex
        string storage_provider
        datetime upload_timestamp
        string status "active | deleted"
    }

    AUDIT_EVENTS {
        int id PK
        int user_id FK
        string event_type
        datetime timestamp
        boolean success
        string ip_address
        string correlation_id
        text details
    }
```

### 3.3 Cryptographic Workflow Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as User Browser
    participant API as FastAPI Backend
    participant Crypto as AES-256-GCM Engine
    participant DB as SQL Database
    participant S3 as S3 / MinIO Storage

    Note over User,S3: Encryption & Cloud Upload Phase
    User->>API: POST /api/files/encrypt (Multipart File + JWT)
    API->>API: Validate Token, Size limit & MIME type
    API->>Crypto: Generate random 256-bit DEK & 96-bit Nonce
    Crypto->>Crypto: Encrypt file payload with DEK + AAD(owner_id, filename)
    Crypto->>Crypto: Wrap DEK with Master KEK
    API->>S3: Upload Ciphertext to users/{user_id}/{hash}_{filename}.enc
    API->>DB: Persist metadata (nonce_hex, wrapped_dek_hex, object_key)
    API->>DB: Record ENCRYPT_FILE audit event
    API-->>User: 201 Created (File ID, Algorithm, Object Key)

    Note over User,S3: Decryption & Download Phase
    User->>API: POST /api/files/{id}/decrypt (JWT Bearer)
    API->>DB: Query FileRecord & verify owner_id == JWT sub
    API->>S3: Download Ciphertext object by key
    API->>Crypto: Unwrap DEK using Master KEK
    API->>Crypto: Decrypt & verify 128-bit GCM Auth Tag + AAD
    alt Authentication Tag Valid
        API->>DB: Record DECRYPT_FILE (Success)
        API-->>User: 200 OK (Original Plaintext Stream)
    else Tampering Detected / Invalid Tag
        API->>DB: Record DECRYPT_FILE (Failure)
        API-->>User: 422 Unprocessable Entity (Authentication Failed)
    end
```

---

## 4. Quick Start & Execution Guide

### 4.1 Prerequisites
* **Python 3.12+** installed (`python --version`)
* **Node.js 18+** & **npm** installed (`node --version`)
* *(Optional)* **Docker & Docker Compose** for containerized execution.

### 4.2 Local Running (Standard Setup)

#### Step 1: Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed demonstration accounts & sample encrypted files
python -m scripts.seed_demo

# Start the FastAPI application server
python -m uvicorn app.main:app --port 8000 --reload
```
* **API Server:** `http://localhost:8000`
* **Swagger OpenAPI Docs:** `http://localhost:8000/api/docs`
* **Health Endpoint:** `http://localhost:8000/api/health`

#### Step 2: Frontend Setup
In a new terminal window:
```bash
# Navigate to frontend directory
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```
* **Frontend Dashboard:** `http://localhost:5173`

---

### 4.3 Running with Docker Compose (Full Stack + MinIO)
To run backend, frontend, MinIO object store, and bucket provisioner in containers:
```bash
# Start all containers in the background
docker compose up -d

# Verify running services
docker compose ps
```
* **Frontend Web Application:** `http://localhost:5173`
* **FastAPI Backend:** `http://localhost:8000/api/docs`
* **MinIO Storage Console:** `http://localhost:9001` (User: `minioadmin`, Password: `minioadmin123`)

---

## 5. Demonstration Accounts & Credentials

The seed script creates three pre-configured accounts:

| Role | Email | Password | Purpose |
|---|---|---|---|
| **User A** | `alice@afes.demo` | `Demo@Alice1` | Test file encryption, download, and tamper test |
| **User B** | `bob@afes.demo` | `Demo@Bob1` | Demonstrate cross-user access denial against Alice's files |
| **Admin** | `admin@afes.demo` | `Demo@Admin1` | System health, global audit log review |

> [!WARNING]
> Demo credentials are strictly intended for local development and academic examination. Execute `python -m scripts.reset_demo` to purge demonstration data before deploying to production.

---

## 6. Four-Student Presentation Guide

AFES includes a built-in interactive presentation mode under `/demo`. Use the following speaking scripts and checklists:

### Student 1 — Authentication & Access Control
* **Checklist:**
  1. Open `/register` and demonstrate input validation (password strength and mismatch).
  2. Sign in as Alice (`alice@afes.demo`) and inspect the issued JWT session.
  3. Sign in as Bob (`bob@afes.demo`) in another tab.
  4. Attempt to query Alice's file ID (`/api/files/1`) as Bob; observe HTTP `403 Forbidden`.
* **Script:**
  > *"Good morning examiners. I am presenting Authentication & Access Control in AFES. In cloud multi-tenancy, perimeter defense is insufficient. We implemented Argon2id password hashing—the OWASP-recommended memory-hard algorithm resistant to GPU brute-forcing. Authenticated users receive a signed JWT token. Crucially, our authorization policy is enforced entirely server-side: even if an adversary tampers with parameters to request another user's files, our backend intercepts the call, rejects it with HTTP 403 Forbidden, and logs an unauthorized access attempt."*

### Student 2 — Cryptographic File Protection
* **Checklist:**
  1. Open `/encrypt` and upload a sample PDF, image, or TXT file.
  2. Explain the AES-256-GCM algorithm badge and per-file 96-bit nonce generation.
  3. Download and verify the decrypted file matches the original byte-for-byte.
  4. Trigger the live **Tamper Test** on an encrypted file and observe the cryptographic rejection.
* **Script:**
  > *"Respected faculty, my module covers Cryptographic File Protection. AFES implements AES-256-GCM authenticated encryption with Envelope Encryption: each file receives an ephemeral 32-byte Data Encryption Key (DEK). The DEK encrypts the payload and is wrapped by our Master Key (KEK). Furthermore, we bind file metadata into Authenticated Additional Data (AAD). As demonstrated in our live tamper test, if an attacker alters even a single bit in the ciphertext, the GCM authentication tag verification fails immediately, and the backend refuses to return corrupted data."*

### Student 3 — Cloud Object Storage Integration
* **Checklist:**
  1. Open `/cloud` and examine active storage provider status.
  2. Show that objects are stored under `users/{user_id}/{unique_hash}_{filename}.enc`.
  3. Run the live **Connection Test Probe** (probe upload, verify, and delete).
  4. Demonstrate deleting a file, showing synchronized removal from SQL and cloud storage.
* **Script:**
  > *"Hello everyone. I am presenting Cloud Object Storage and Provider Abstraction. Cloud storage handles immutable binary objects addressed via unique keys in private buckets. We built a modular StorageProvider abstraction in Python. For local demonstration, we communicate via Boto3 with MinIO. By toggling environment variables, the identical codebase connects directly to AWS S3. Most importantly, zero plaintext ever reaches the storage provider: even if a cloud bucket was made public, an attacker would obtain only undecryptable ciphertext."*

### Student 4 — Observability, Architecture & Deployment
* **Checklist:**
  1. Open `/audit` and review the chronologically ordered event timeline.
  2. Show that audit telemetry excludes passwords, tokens, and encryption keys.
  3. Open `/api/docs` and show Swagger OpenAPI specifications.
  4. Review `/api/health` system diagnostic JSON response.
  5. Explain Docker Compose orchestration and stateless horizontal scaling.
* **Script:**
  > *"Examiners, my module covers Observability, Cloud Architecture, and Deployment. AFES maintains an immutable audit log recording registrations, authentications, uploads, downloads, and intrusion attempts, adhering strictly to privacy-by-design. Our deployment is containerized with Docker Compose. Because the FastAPI backend instances are stateless, multiple backend containers can sit behind an AWS Application Load Balancer sharing the database and S3 bucket for horizontal scalability."*

---

## 7. Cloud Storage Configuration (AWS S3 & MinIO)

### 7.1 Configuring MinIO (Local S3 Simulation)
1. Run MinIO via Docker Compose:
   ```bash
   docker compose up minio -d
   ```
2. Set in `backend/.env`:
   ```ini
   STORAGE_PROVIDER=minio
   MINIO_ENDPOINT=localhost:9000
   MINIO_ACCESS_KEY=minioadmin
   MINIO_SECRET_KEY=minioadmin123
   MINIO_BUCKET=afes-encrypted-files
   MINIO_SECURE=false
   ```

### 7.2 Configuring AWS S3 (Production)
1. Create a private S3 bucket in your AWS Console (e.g. `my-afes-bucket`).
2. Enable "Block all public access" on the bucket.
3. Create an IAM User with the following least-privilege policy:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "s3:PutObject",
                   "s3:GetObject",
                   "s3:DeleteObject",
                   "s3:ListBucket"
               ],
               "Resource": [
                   "arn:aws:s3:::my-afes-bucket",
                   "arn:aws:s3:::my-afes-bucket/*"
               ]
           }
       ]
   }
   ```
4. Update `backend/.env`:
   ```ini
   STORAGE_PROVIDER=s3
   AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
   AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   AWS_REGION=us-east-1
   S3_BUCKET=my-afes-bucket
   ```

---

## 8. Automated Testing & Verification

The test suite covers authentication, password hashing, authorization, encryption roundtrips, tampering detection, and audit logging:

```bash
cd backend
pytest -v
```

### Test Suite Summary:
* **`tests/test_auth.py` (11 tests):** Registration, duplicate email rejection, weak password rejection, password mismatch, Argon2id hash verification, login success, wrong password rejection, protected route rejection without token.
* **`tests/test_authorization.py` (6 tests):** Cross-user file read denial, cross-user decryption denial, cross-user deletion denial, unauthorized access audit event creation, unauthenticated rejection, user file isolation.
* **`tests/test_encryption.py` (8 tests):** Valid encryption tuple, roundtrip integrity, 5MB large file roundtrip, ciphertext tamper detection, wrong owner rejection, wrong filename rejection, unique IV/ciphertext generation, wrapped DEK format.
* **`tests/test_files.py` (8 tests):** Encrypt API endpoint, file listing, decrypt-download stream, tamper-test endpoint, deletion, empty file rejection, stored object ciphertext verification, metadata persistence.

---

## 9. Security Limitations & Academic Disclaimer

AFES is an educational engineering project created to demonstrate cloud security and cryptography. The following production differences should be noted:
1. **Key Management:** In this demonstration, the Master KEK is supplied via environment variables. In an enterprise AWS environment, AWS KMS (`kms:GenerateDataKey`, `kms:Decrypt`) or an HSM should be used.
2. **Transport Security:** For local testing, plain HTTP is accepted. In production, HTTPS/TLS certificates must be enforced via AWS Certificate Manager (ACM) behind CloudFront or ALB.
3. **Key Rotation:** Automated key rotation pipelines should be scheduled to minimize cryptographic blast radius.

---

## 10. Authors & Acknowledgements
* **Course:** Cloud Computing Engineering Mini Project
* **Institution:** Department of Computer Science & Engineering
* **Project:** Authenticated File Encryption System (AFES)
