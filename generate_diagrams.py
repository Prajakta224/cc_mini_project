"""
Script to generate publication-quality figures for the AFES Project Report.
Matches the academic and technical style of the reference report.
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

os.makedirs('report_assets', exist_ok=True)
plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'

# ─── FIGURE 3.1: ARCHITECTURE DIAGRAM ─────────────────────────────────────────
def create_fig3_1():
    fig, ax = plt.subplots(figsize=(10, 6.5), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Main Title Header
    ax.text(50, 96, "AFES: Three-Tier Cloud Security Architecture", ha='center', va='center',
            fontsize=13, fontweight='bold', color='#0f172a')

    # 1. Presentation Tier Box
    p1 = patches.FancyBboxPatch((5, 78), 90, 14, boxstyle="round,pad=0.5,rounding_size=1.5",
                                ec="#2563eb", fc="#eff6ff", lw=1.5)
    ax.add_patch(p1)
    ax.text(7, 89, "1. PRESENTATION TIER (React 18 + TypeScript + Vite + Tailwind CSS)", 
            fontsize=9.5, fontweight='bold', color='#1e3a8a')
    
    # Submodules in Presentation
    frontend_mods = ["Landing Page (/)", "Auth & RBAC (/login, /register)", "Dashboard & Stats (/dashboard)", 
                     "Encrypt Vault (/encrypt)", "My Files & Tamper (/files)", "Audit Telemetry (/audit)"]
    for i, mod in enumerate(frontend_mods):
        x = 7 + (i % 3) * 29.5
        y = 83.5 if i < 3 else 79.5
        m_box = patches.FancyBboxPatch((x, y), 28, 3.2, boxstyle="round,pad=0.3,rounding_size=0.8",
                                      ec="#93c5fd", fc="#ffffff", lw=1)
        ax.add_patch(m_box)
        ax.text(x + 14, y + 1.6, mod, ha='center', va='center', fontsize=7.5, color='#1e293b', fontweight='medium')

    # Arrow 1 -> 2
    ax.annotate("", xy=(50, 71.5), xytext=(50, 77.5),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="#2563eb"))
    ax.text(50, 74.5, "HTTPS / RESTful JSON Requests (JWT Bearer Authorization)", ha='center', va='center',
            fontsize=7.5, color='#1e40af', fontweight='bold',
            bbox=dict(boxstyle="square,pad=0.2", fc="#ffffff", ec="#93c5fd", lw=0.8))

    # 2. Application & Core Orchestration Tier Box
    p2 = patches.FancyBboxPatch((5, 34), 90, 36.5, boxstyle="round,pad=0.5,rounding_size=1.5",
                                ec="#7c3aed", fc="#faf5ff", lw=1.5)
    ax.add_patch(p2)
    ax.text(7, 67.5, "2. APPLICATION & CRYPTOGRAPHIC ENGINE TIER (FastAPI + Python 3.12+)", 
            fontsize=9.5, fontweight='bold', color='#5b21b6')

    # Endpoints Header Bar
    api_box = patches.FancyBboxPatch((7, 61), 86, 4.5, boxstyle="round,pad=0.3,rounding_size=0.8",
                                     ec="#c4b5fd", fc="#ffffff", lw=1)
    ax.add_patch(api_box)
    ax.text(50, 63.25, "FastAPI Endpoints: /api/auth/*  |  /api/files/*  |  /api/audit  |  /api/cloud/*  |  /api/health",
            ha='center', va='center', fontsize=8, color='#4c1d95', fontweight='bold')

    # Core internal services in Backend
    services = [
        ("Identity & Access Control", ["Argon2id Password Hasher", "JWT Mint & Signature Verify", "Server-Side RBAC Enforcement"], "#3b82f6", "#eff6ff"),
        ("Cryptographic Engine", ["AES-256-GCM AEAD Mode", "Fresh 96-bit Nonces (IV)", "AAD Binding (owner_id, filename)"], "#10b981", "#ecfdf5"),
        ("Envelope Key Manager", ["256-bit Ephemeral DEK Generation", "Master KEK Key-Wrapping", "AWS KMS Compatible Boundary"], "#8b5cf6", "#f5f3ff"),
        ("Audit & Telemetry Logger", ["Non-Sensitive Event Logging", "Correlation Tracking", "IP Address & Operation Auditing"], "#f59e0b", "#fffbeb")
    ]
    for i, (title, items, border_c, fill_c) in enumerate(services):
        bx = 7 + (i % 2) * 44
        by = 47.5 if i < 2 else 35.5
        sb = patches.FancyBboxPatch((bx, by), 42, 11, boxstyle="round,pad=0.3,rounding_size=1",
                                    ec=border_c, fc=fill_c, lw=1.2)
        ax.add_patch(sb)
        ax.text(bx + 2, by + 8.8, title, fontsize=8.2, fontweight='bold', color='#0f172a')
        for idx, itm in enumerate(items):
            ax.text(bx + 3.5, by + 6.3 - idx * 2.2, f"• {itm}", fontsize=7.2, color='#334155')

    # Arrows 2 -> 3
    ax.annotate("", xy=(28, 25.5), xytext=(28, 33.5),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="#059669"))
    ax.text(28, 29.5, "SQL Metadata", ha='center', va='center',
            fontsize=7.5, color='#065f46', fontweight='bold',
            bbox=dict(boxstyle="square,pad=0.2", fc="#ffffff", ec="#6ee7b7", lw=0.8))

    ax.annotate("", xy=(72, 25.5), xytext=(72, 33.5),
                arrowprops=dict(arrowstyle="->", lw=1.5, color="#d97706"))
    ax.text(72, 29.5, "Encrypted Ciphertext Only", ha='center', va='center',
            fontsize=7.5, color='#92400e', fontweight='bold',
            bbox=dict(boxstyle="square,pad=0.2", fc="#ffffff", ec="#fcd34d", lw=0.8))

    # 3. Persistence & Cloud Object Storage Tier Box
    p3 = patches.FancyBboxPatch((5, 4), 90, 21, boxstyle="round,pad=0.5,rounding_size=1.5",
                                ec="#059669", fc="#ecfdf5", lw=1.5)
    ax.add_patch(p3)
    ax.text(7, 21.5, "3. DATA PERSISTENCE & PLUGGABLE CLOUD OBJECT STORAGE TIER", 
            fontsize=9.5, fontweight='bold', color='#065f46')

    # Relational Database
    db_box = patches.FancyBboxPatch((7, 6), 41, 13.5, boxstyle="round,pad=0.4,rounding_size=1",
                                    ec="#059669", fc="#ffffff", lw=1.2)
    ax.add_patch(db_box)
    ax.text(27.5, 16.5, "SQLAlchemy Relational Layer", ha='center', fontsize=8.5, fontweight='bold', color='#065f46')
    ax.text(27.5, 13.5, "SQLite (WAL Mode) / PostgreSQL", ha='center', fontsize=7.5, color='#334155')
    ax.text(27.5, 11, "Tables: users, file_records, audit_events", ha='center', fontsize=7, color='#64748b')
    ax.text(27.5, 8.5, "(Stores metadata, nonces & wrapped DEKs only)", ha='center', fontsize=6.8, color='#059669', fontstyle='italic')

    # Cloud Storage Abstraction
    stor_box = patches.FancyBboxPatch((52, 6), 41, 13.5, boxstyle="round,pad=0.4,rounding_size=1",
                                      ec="#d97706", fc="#ffffff", lw=1.2)
    ax.add_patch(stor_box)
    ax.text(72.5, 16.5, "Abstract StorageProvider Interface", ha='center', fontsize=8.5, fontweight='bold', color='#92400e')
    
    # Dual Cloud Modes
    m1 = patches.FancyBboxPatch((54, 8), 17.5, 6, boxstyle="round,pad=0.2,rounding_size=0.6",
                                ec="#f59e0b", fc="#fffbeb", lw=0.9)
    ax.add_patch(m1)
    ax.text(62.75, 12, "AWS S3", ha='center', fontsize=7.5, fontweight='bold', color='#b45309')
    ax.text(62.75, 9.5, "Production Cloud", ha='center', fontsize=6.8, color='#78350f')

    m2 = patches.FancyBboxPatch((73.5, 8), 17.5, 6, boxstyle="round,pad=0.2,rounding_size=0.6",
                                ec="#10b981", fc="#ecfdf5", lw=0.9)
    ax.add_patch(m2)
    ax.text(82.25, 12, "MinIO / Local", ha='center', fontsize=7.5, fontweight='bold', color='#047857')
    ax.text(82.25, 9.5, "S3-Compatible Demo", ha='center', fontsize=6.8, color='#064e3b')

    plt.tight_layout()
    plt.savefig('report_assets/fig3_1_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Figure 3.1 generated successfully.")

# ─── FIGURE 3.2: AUTH FLOWCHART ───────────────────────────────────────────────
def create_fig3_2():
    fig, ax = plt.subplots(figsize=(8, 6.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    ax.text(50, 97, "AFES: Authentication & Authorization Flowchart", ha='center', va='center',
            fontsize=12, fontweight='bold', color='#0f172a')

    # Flowchart steps:
    # 1. Start / User Request
    s1 = patches.FancyBboxPatch((35, 88), 30, 6, boxstyle="round,pad=0.3,rounding_size=3",
                                ec="#2563eb", fc="#eff6ff", lw=1.2)
    ax.add_patch(s1)
    ax.text(50, 91, "User Submits Credentials / Request", ha='center', va='center', fontsize=8, fontweight='bold', color='#1e40af')

    # Arrow
    ax.annotate("", xy=(50, 81), xytext=(50, 88), arrowprops=dict(arrowstyle="->", lw=1.2, color="#475569"))

    # 2. Input Validation
    s2 = patches.FancyBboxPatch((30, 75), 40, 6, boxstyle="round,pad=0.3,rounding_size=0.8",
                                ec="#64748b", fc="#f8fafc", lw=1.2)
    ax.add_patch(s2)
    ax.text(50, 78, "Validate Input (Pydantic Email & Password Guard)", ha='center', va='center', fontsize=8, color='#1e293b')

    # Arrow
    ax.annotate("", xy=(50, 68), xytext=(50, 75), arrowprops=dict(arrowstyle="->", lw=1.2, color="#475569"))

    # 3. Decision 1: Valid format?
    d1 = patches.Polygon([[50, 68], [68, 61], [50, 54], [32, 61]], closed=True,
                         ec="#f59e0b", fc="#fffbeb", lw=1.2)
    ax.add_patch(d1)
    ax.text(50, 61, "Valid Format & Hash?", ha='center', va='center', fontsize=7.8, fontweight='bold', color='#92400e')

    # Decision 1 No branch -> 422/401 Reject
    ax.annotate("", xy=(85, 61), xytext=(68, 61), arrowprops=dict(arrowstyle="->", lw=1.2, color="#dc2626"))
    ax.text(74, 62.5, "No", fontsize=7.5, color='#dc2626', fontweight='bold')
    rej1 = patches.FancyBboxPatch((85, 58), 13, 6, boxstyle="round,pad=0.2,rounding_size=0.6",
                                  ec="#dc2626", fc="#fef2f2", lw=1.2)
    ax.add_patch(rej1)
    ax.text(91.5, 61, "401 / 422\nReject & Log", ha='center', va='center', fontsize=6.8, color='#991b1b', fontweight='bold')

    # Decision 1 Yes branch -> Issue / Validate JWT
    ax.annotate("", xy=(50, 47), xytext=(50, 54), arrowprops=dict(arrowstyle="->", lw=1.2, color="#10b981"))
    ax.text(51.5, 50.5, "Yes", fontsize=7.5, color='#059669', fontweight='bold')

    s3 = patches.FancyBboxPatch((28, 41), 44, 6, boxstyle="round,pad=0.3,rounding_size=0.8",
                                ec="#10b981", fc="#ecfdf5", lw=1.2)
    ax.add_patch(s3)
    ax.text(50, 44, "Verify Argon2id Hash & Issue Signed JWT Bearer", ha='center', va='center', fontsize=8, color='#065f46', fontweight='bold')

    # Arrow
    ax.annotate("", xy=(50, 34), xytext=(50, 41), arrowprops=dict(arrowstyle="->", lw=1.2, color="#475569"))

    # 4. Protected Route & Ownership Verification Decision
    d2 = patches.Polygon([[50, 34], [72, 26], [50, 18], [28, 26]], closed=True,
                         ec="#8b5cf6", fc="#f5f3ff", lw=1.2)
    ax.add_patch(d2)
    ax.text(50, 26, "Server Ownership Check:\nowner_id == JWT.sub?", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#5b21b6')

    # Decision 2 No branch -> 403 Forbidden
    ax.annotate("", xy=(85, 26), xytext=(72, 26), arrowprops=dict(arrowstyle="->", lw=1.2, color="#dc2626"))
    ax.text(77, 27.5, "No", fontsize=7.5, color='#dc2626', fontweight='bold')
    rej2 = patches.FancyBboxPatch((85, 23), 13, 6, boxstyle="round,pad=0.2,rounding_size=0.6",
                                  ec="#dc2626", fc="#fef2f2", lw=1.2)
    ax.add_patch(rej2)
    ax.text(91.5, 26, "403 Forbidden\nLog Audit", ha='center', va='center', fontsize=6.8, color='#991b1b', fontweight='bold')

    # Decision 2 Yes branch -> Authorize Operation
    ax.annotate("", xy=(50, 11), xytext=(50, 18), arrowprops=dict(arrowstyle="->", lw=1.2, color="#10b981"))
    ax.text(51.5, 14.5, "Yes", fontsize=7.5, color='#059669', fontweight='bold')

    s4 = patches.FancyBboxPatch((30, 5), 40, 6, boxstyle="round,pad=0.3,rounding_size=3",
                                ec="#059669", fc="#d1fae5", lw=1.2)
    ax.add_patch(s4)
    ax.text(50, 8, "Authorize Operation (Encrypt / Download / Delete)", ha='center', va='center', fontsize=8, color='#065f46', fontweight='bold')

    plt.tight_layout()
    plt.savefig('report_assets/fig3_2_auth_flowchart.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Figure 3.2 generated successfully.")

# ─── FIGURE 3.3: CRYPTO & CLOUD WORKFLOW ──────────────────────────────────────
def create_fig3_3():
    fig, ax = plt.subplots(figsize=(10, 6.2), dpi=300)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    ax.text(50, 97, "AFES: Dual-Phase Cryptographic & Cloud Storage Workflow", ha='center', va='center',
            fontsize=12.5, fontweight='bold', color='#0f172a')

    # PHASE A: ENCRYPTION & UPLOAD (LEFT HALF)
    box_a = patches.FancyBboxPatch((2, 5), 46.5, 88, boxstyle="round,pad=0.5,rounding_size=1.5",
                                   ec="#2563eb", fc="#f8fafc", lw=1.2)
    ax.add_patch(box_a)
    ax.text(25.25, 89.5, "PHASE 1: ENCRYPTION & CLOUD UPLOAD", ha='center', fontsize=9, fontweight='bold', color='#1e3a8a')

    steps_a = [
        ("1. User File Selection", "Plaintext document selected (PDF, TXT, DOCX, IMG)", "#3b82f6"),
        ("2. Envelope Key Generation", "Generate unique 256-bit DEK & 96-bit random Nonce", "#8b5cf6"),
        ("3. AES-256-GCM AEAD Encryption", "Encrypt with DEK + AAD: 'AFES:v1:<owner_id>:<filename>'", "#10b981"),
        ("4. Key Wrapping", "Wrap ephemeral DEK with Master KEK (60 bytes)", "#8b5cf6"),
        ("5. Object Store Ingestion", "Upload ciphertext: users/{user_id}/{hash}_{fn}.enc", "#d97706"),
        ("6. Metadata & Audit Persistence", "Persist nonce_hex, wrapped_dek_hex, object_key in SQL", "#059669")
    ]
    for idx, (title, desc, col) in enumerate(steps_a):
        sy = 78 - idx * 12.5
        sb = patches.FancyBboxPatch((5, sy), 40.5, 9.5, boxstyle="round,pad=0.3,rounding_size=0.8",
                                    ec=col, fc="#ffffff", lw=1.1)
        ax.add_patch(sb)
        ax.text(7, sy + 6.8, title, fontsize=8, fontweight='bold', color='#0f172a')
        ax.text(7, sy + 3.2, desc, fontsize=6.8, color='#475569')
        if idx < 5:
            ax.annotate("", xy=(25.25, sy - 2.8), xytext=(25.25, sy),
                        arrowprops=dict(arrowstyle="->", lw=1.1, color="#64748b"))

    # PHASE B: DECRYPTION & VERIFICATION (RIGHT HALF)
    box_b = patches.FancyBboxPatch((51.5, 5), 46.5, 88, boxstyle="round,pad=0.5,rounding_size=1.5",
                                   ec="#059669", fc="#f8fafc", lw=1.2)
    ax.add_patch(box_b)
    ax.text(74.75, 89.5, "PHASE 2: VERIFICATION & DECRYPTION", ha='center', fontsize=9, fontweight='bold', color='#065f46')

    steps_b = [
        ("1. Decryption Request", "Authenticated user requests file download by file_id", "#3b82f6"),
        ("2. Ownership Verification", "Backend validates record.owner_id == JWT.sub", "#3b82f6"),
        ("3. Object Retrieval", "Ciphertext downloaded from AWS S3 / MinIO by key", "#d97706"),
        ("4. Key Unwrapping", "Unwrap DEK using Master KEK from secure settings", "#8b5cf6"),
        ("5. GCM Integrity Tag Check", "Verify 128-bit Tag & AAD metadata consistency", "#10b981"),
    ]
    for idx, (title, desc, col) in enumerate(steps_b):
        sy = 78 - idx * 12.5
        sb = patches.FancyBboxPatch((54.5, sy), 40.5, 9.5, boxstyle="round,pad=0.3,rounding_size=0.8",
                                    ec=col, fc="#ffffff", lw=1.1)
        ax.add_patch(sb)
        ax.text(56.5, sy + 6.8, title, fontsize=8, fontweight='bold', color='#0f172a')
        ax.text(56.5, sy + 3.2, desc, fontsize=6.8, color='#475569')
        if idx < 4:
            ax.annotate("", xy=(74.75, sy - 2.8), xytext=(74.75, sy),
                        arrowprops=dict(arrowstyle="->", lw=1.1, color="#64748b"))

    # Step 6: Dual Outcome (Success vs Failure)
    # Arrow to outcomes
    ax.annotate("", xy=(64, 21), xytext=(74.75, 28), arrowprops=dict(arrowstyle="->", lw=1.1, color="#10b981"))
    ax.annotate("", xy=(85, 21), xytext=(74.75, 28), arrowprops=dict(arrowstyle="->", lw=1.1, color="#dc2626"))

    # Success outcome
    sc_box = patches.FancyBboxPatch((54.5, 7), 19, 14, boxstyle="round,pad=0.3,rounding_size=0.8",
                                    ec="#10b981", fc="#ecfdf5", lw=1.2)
    ax.add_patch(sc_box)
    ax.text(64, 17, "TAG VALID (Success)", ha='center', fontsize=7.2, fontweight='bold', color='#065f46')
    ax.text(64, 12, "Stream Plaintext\nByte-Identical Original\nLog DECRYPT_FILE", ha='center', fontsize=6.5, color='#047857')

    # Failure outcome
    fl_box = patches.FancyBboxPatch((76, 7), 19, 14, boxstyle="round,pad=0.3,rounding_size=0.8",
                                    ec="#dc2626", fc="#fef2f2", lw=1.2)
    ax.add_patch(fl_box)
    ax.text(85.5, 17, "TAMPER DETECTED", ha='center', fontsize=7.2, fontweight='bold', color='#991b1b')
    ax.text(85.5, 12, "Tag Mismatch / Altered\nReturn 422 HTTP Error\nZero Plaintext Leaked", ha='center', fontsize=6.5, color='#b91c1c')

    plt.tight_layout()
    plt.savefig('report_assets/fig3_3_crypto_workflow.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Figure 3.3 generated successfully.")

# ─── FIGURE 5.1: TEST BREAKDOWN & VERIFICATION CHARTS ─────────────────────────
def create_fig5_1():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=300)

    # Subplot 1: Automated Test Results by Module (33 Tests)
    modules = ['Authentication\n& Passwords', 'Cross-User\nAuthorization', 'AES-256-GCM\nCrypto Engine', 'File Operations\n& Storage']
    counts = [11, 6, 8, 8]
    colors = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b']

    bars = ax1.bar(modules, counts, color=colors, width=0.55, edgecolor='#0f172a', linewidth=0.8)
    ax1.set_ylabel('Number of Automated Tests', fontsize=8.5, fontweight='bold', color='#0f172a')
    ax1.set_title('Test Suite Distribution: 33 Passed Tests (100% Pass Rate)', fontsize=9.5, fontweight='bold', color='#0f172a')
    ax1.set_ylim(0, 14)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)

    for bar in bars:
        h = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., h + 0.35, f"{int(h)} ({int(h/33*100)}%)",
                 ha='center', va='bottom', fontsize=8, fontweight='bold', color='#1e293b')

    ax1.tick_params(axis='x', labelsize=8)
    ax1.tick_params(axis='y', labelsize=8)

    # Subplot 2: Cryptographic Security Features Verification
    categories = ['Argon2id Hash\nVerification', 'Nonce & Key\nUniqueness', 'Ciphertext Tamper\nRejection', 'Ownership (AAD)\nBinding Enforcement']
    pct = [100, 100, 100, 100]
    bars2 = ax2.barh(categories, pct, color='#059669', height=0.45, edgecolor='#064e3b', linewidth=0.8)
    ax2.set_xlabel('Verification Compliance Rate (%)', fontsize=8.5, fontweight='bold', color='#0f172a')
    ax2.set_title('Core Security Primitives Integrity Verification', fontsize=9.5, fontweight='bold', color='#0f172a')
    ax2.set_xlim(0, 115)
    ax2.grid(axis='x', linestyle='--', alpha=0.5)

    for bar in bars2:
        w = bar.get_width()
        ax2.text(w + 1.5, bar.get_y() + bar.get_height()/2., "100% Verified",
                 ha='left', va='center', fontsize=7.8, fontweight='bold', color='#065f46')

    ax2.tick_params(axis='x', labelsize=8)
    ax2.tick_params(axis='y', labelsize=8)

    plt.tight_layout()
    plt.savefig('report_assets/fig5_1_test_breakdown.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Figure 5.1 generated successfully.")

if __name__ == '__main__':
    create_fig3_1()
    create_fig3_2()
    create_fig3_3()
    create_fig5_1()
    print("All figures generated successfully.")
