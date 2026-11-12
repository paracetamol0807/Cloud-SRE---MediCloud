import os
import csv
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak
)

def build_pdf():
    pdf_filename = "MediCloud_Research_Paper.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#0D1B2A'),
        alignment=1, # Center
        spaceAfter=6
    )

    author_style = ParagraphStyle(
        'DocAuthor',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#333333'),
        alignment=1, # Center
        spaceAfter=12
    )

    sec_style = ParagraphStyle(
        'SecHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#0D1B2A'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    subsec_style = ParagraphStyle(
        'SubSecHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#0077B6'),
        spaceBefore=6,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Times-Roman',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#212529'),
        spaceAfter=6
    )

    cap_style = ParagraphStyle(
        'CaptionStyle',
        parent=styles['Normal'],
        fontName='Times-Italic',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#555555'),
        alignment=1,
        spaceAfter=8
    )

    story = []

    # Title & Metadata
    story.append(Paragraph(
        "A Privacy-Preserving Cloud Data Sharing Architecture for Multi-Hospital Electronic Health Records: "
        "Integrating Searchable Encryption, Multi-Authority ABAC, Proxy Re-Encryption, and Dynamic Behavioral Trust",
        title_style
    ))
    story.append(Paragraph(
        "<b>MOHIT | Roll No.: 25BDA069</b><br/>"
        "Department of Data Science & Engineering, Indian Institute of Information Technology Dharwad<br/>"
        "Course: Cloud SRE and Security",
        author_style
    ))

    # Abstract
    story.append(Paragraph(
        "<b>Abstract—</b> Cloud-based healthcare information sharing significantly improves diagnostic availability and multi-institutional collaboration "
        "but introduces severe privacy risks when sensitive records are stored by semi-trusted third-party cloud providers. "
        "Based on the cloud privacy framework reviewed by Pan Jun Sun (IEEE Access 2019), this work designs, implements, and evaluates the complete "
        "MediCloud prototype for multi-hospital Electronic Health Record (EHR) sharing. The architecture realizes five foundational cryptographic "
        "and SRE primitives: (1) AES-256-GCM authenticated encryption with Additional Authenticated Data (AAD) record binding; "
        "(2) Searchable Symmetric Encryption (SSE) utilizing blind HMAC-SHA256 trapdoor indexing for zero-leakage diagnostic searching; "
        "(3) Decentralized Multi-Authority Access Control (MA-ABAC) separating role licensing from local hospital governance; "
        "(4) BBS98-style Proxy Re-Encryption (PRE) over RFC 3526 1024-bit MODP safe prime fields for cloud-delegated, O(1) staff revocation; "
        "(5) Dynamic Behavioral Trust & Reputation telemetry enforcing automated quarantine gating below a 0.40 score threshold; "
        "(6) Cryptographic traitor tracing for rogue key leak identification; and (7) SHA-256 tamper-evident integrity auditing. "
        "Sixteen functional security tests were executed using synthetic clinical records; all 16 checks passed (100% pass rate). "
        "Empirical microbenchmarks demonstrate sub-millisecond execution times (~0.45 ms upload/indexing, ~0.06 ms decryption, ~0.003 ms keyword search), "
        "proving that comprehensive defense-in-depth cloud security imposes negligible SRE overhead on modern healthcare workflows.",
        body_style
    ))

    story.append(Paragraph(
        "<b>Index Terms—</b> Cloud security, cloud privacy, electronic health records, AES-GCM, attribute-based access control, searchable encryption, proxy re-encryption, dynamic trust, traitor tracing, SRE.",
        body_style
    ))

    # Section I
    story.append(Paragraph("I. INTRODUCTION", sec_style))
    story.append(Paragraph(
        "Modern healthcare organizations increasingly outsource clinical electronic health records (EHRs) to commercial cloud platforms to enhance "
        "interoperability across hospitals, diagnostic laboratories, and emergency care networks. However, public cloud infrastructure is maintained by "
        "third-party cloud service providers (CSPs) that are considered 'honest-but-curious' or semi-trusted: providers faithfully execute storage and "
        "compute instructions but possess strong commercial and technical incentives to observe outsourced plaintext data. Furthermore, multi-tenant "
        "cloud virtualization creates persistent attack surfaces for co-tenant data leakage, hypervisor vulnerabilities, and administrative insider threats. "
        "Consequently, health privacy regulations including HIPAA, the European GDPR, and the Indian Digital Personal Data Protection (DPDP) Act mandate "
        "strict access controls, cryptographic confidentiality at rest, and verifiable audit logging.<br/><br/>"
        "In his seminal 2019 IEEE Access survey, Pan Jun Sun established that no single security primitive suffices to resolve cloud privacy challenges. "
        "Instead, resilient cloud security requires an interlocking defense-in-depth architecture combining Access Control (rules formulation), "
        "Attribute-Based Encryption / Cryptographic Enforcement, Searchable Encryption (usability), and Behavioral Trust Systems. "
        "This research project narrows Sun's theoretical framework into an operational, fully verified software implementation called MediCloud, "
        "designed specifically for multi-hospital EHR federations.",
        body_style
    ))

    # Section II
    story.append(Paragraph("II. LITERATURE REVIEW & BACKGROUND", sec_style))
    story.append(Paragraph(
        "Pan Jun Sun's 2019 survey systematically analyzed cloud privacy across four technological dimensions: classical access control (DAC, MAC, RBAC, ABAC), "
        "attribute-based encryption (KP-ABE vs. CP-ABE), searchable encryption (SSE and asymmetric PEKS/ABKS), and trust/reputation systems. "
        "The survey emphasizes that in outsourced environments, Ciphertext-Policy ABE (CP-ABE) is inherently superior to Key-Policy ABE because the data owner "
        "retains sovereign authority to encode access predicates directly into the ciphertext packaging. However, standard CP-ABE introduces severe "
        "practical bottlenecks: key generation relies on a single central authority, computational pairing overhead scales with policy complexity, and "
        "revoking departing personnel necessitates re-encrypting entire cloud databases.<br/><br/>"
        "To mitigate these challenges, subsequent literature proposed Proxy Re-Encryption (PRE), initially pioneered by Blaze, Bleumer, and Strauss (BBS98), "
        "which allows a semi-trusted proxy to transform ciphertexts from an old authorization key to a new one using an algebraic re-encryption key, without "
        "ever decrypting the underlying plaintext. Concurrently, Searchable Symmetric Encryption (SSE) schemes developed by Curtmola et al. established "
        "that inverted index structures keyed by deterministic trapdoors (HMACs) provide sub-millisecond query evaluation while preserving confidentiality.",
        body_style
    ))

    # Section III
    story.append(Paragraph("III. MEDICLOUD ARCHITECTURAL DESIGN", sec_style))
    story.append(Paragraph(
        "The MediCloud system simulates a realistic healthcare consortium comprising Hospital-A, Hospital-B, a centralized diagnostic laboratory, "
        "a National Central Medical Council (CMA), and a public cloud storage service.",
        body_style
    ))

    if os.path.exists("figures/architecture.png"):
        story.append(Image("figures/architecture.png", width=4.8*inch, height=2.4*inch))
        story.append(Paragraph("Fig. 1. High-level architecture and trust boundaries of the MediCloud system.", cap_style))

    story.append(Paragraph("A. Authenticated Encryption & Integrity Binding", subsec_style))
    story.append(Paragraph(
        "Clinical EHR payloads are serialized to standardized JSON and encrypted using AES-256 in Galois/Counter Mode (GCM). "
        "For each record, a fresh 96-bit cryptographic nonce is sampled using system entropy (secrets.token_bytes). Crucially, the record identifier "
        "(e.g., 'ehr001') is passed as Additional Authenticated Data (AAD) into the GCM cipher. This cryptographic binding guarantees that ciphertext packages "
        "cannot be swapped or renamed inside the cloud repository without triggering authentication tag failure. A supplementary SHA-256 digest is maintained "
        "as an upfront integrity sentinel.",
        body_style
    ))

    story.append(Paragraph("B. Phase 1: Searchable Symmetric Encryption (SSE)", subsec_style))
    story.append(Paragraph(
        "To enable clinical search without compromising patient confidentiality, MediCloud deploys an inverted trapdoor index. "
        "Let K_search be the clinician consortium's master search key. During record upload, diagnostic terms W = {w_1, w_2, ...} are normalized and hashed: "
        "T_w = HMAC-SHA256(K_search, w). The cloud maintains an inverted mapping Index[T_w] → [record_id_1, record_id_2, ...]. "
        "When querying for 'cardiology', the client computes only the blind token T_query and transmits it to the cloud. The cloud performs an exact hash lookup "
        "and returns matching identifiers without learning the underlying medical condition.",
        body_style
    ))

    story.append(Paragraph("C. Phase 2: Decentralized Multi-Authority Access Control (MA-ABAC)", subsec_style))
    story.append(Paragraph(
        "Rather than relying on a vulnerable single master authority, MediCloud partitions identity issuance across autonomous cryptographic authorities: "
        "(1) The Central Medical Council (CMA) signs professional qualifications ('role:doctor', 'license:active'); "
        "(2) Hospital Authorities (HA-A, HA-B) manage departmental affiliations ('hospital:hospital_a', 'dept:cardiology'); and "
        "(3) Diagnostic Laboratories issue diagnostic credentials. Each authority signs credential packages with HMAC-SHA256. "
        "Access policies are formulated as multi-authority conjunctions: Policy = { CMA: ['role:doctor'], HA-A: ['hospital:hospital_a'] }. "
        "A user must present valid, unexpired credentials from all designated authorities; cross-hospital forgery is cryptographically rejected.",
        body_style
    ))

    story.append(Paragraph("D. Phase 3: BBS98 Proxy Re-Encryption (PRE) for Dynamic Revocation", subsec_style))
    story.append(Paragraph(
        "When clinical staff depart an institution, re-encrypting the hospital's entire outsourced database on client workstations is computationally and "
        "bandwidth prohibitive. MediCloud implements BBS98 Proxy Re-Encryption over an RFC 3526 1024-bit MODP safe prime field (p = 2q + 1, g = 2). "
        "The Data Encryption Key (DEK) is encapsulated under group keypair (sk_A, pk_A) where pk_A = g^(sk_A) mod p: c_1 = (pk_A)^r mod p, c_2 = m · g^r mod p. "
        "Upon staff departure, the authority generates a new group key sk_B and derives re-encryption key rk_(A→B) = (sk_A)^(-1) · sk_B mod q. "
        "The cloud blindly computes c_1' = (c_1)^(rk_(A→B)) = g^(sk_B · r) mod p. The cloud transforms the ciphertext without learning m, sk_A, or sk_B, "
        "and departed personnel holding sk_A are immediately locked out.",
        body_style
    ))

    story.append(Paragraph("E. Phase 4: Dynamic Behavioral Trust & Reputation Telemetry", subsec_style))
    story.append(Paragraph(
        "Addressing Sun's fourth primitive family, MediCloud incorporates continuous behavioral telemetry. Users possess a dynamic trust score T ∈ [0.0, 1.0], "
        "initialized at T_0 = 0.60. Verified clinical queries boost trust (+0.05 up to 1.00), while suspicious activity incurs severe penalties: "
        "-0.25 for unauthorized cross-hospital access attempts, -0.15 for expired requests, and -0.35 for tampering. "
        "Inactive accounts undergo exponential time decay towards baseline: T(t) = T_0 + (T_prev - T_0) · e^(-λ · Δt). "
        "MediCloud interlocks trust with authorization: access is granted if and only if both attribute policies are satisfied AND T_user ≥ 0.40. "
        "Compromised accounts exhibiting probe behavior are automatically quarantined.",
        body_style
    ))

    story.append(Paragraph("F. Phase 5: Cryptographic Traitor Tracing", subsec_style))
    story.append(Paragraph(
        "To mitigate insider threats where corrupt staff leak or sell secret attribute keys, MediCloud embeds an unforgeable identity watermark "
        "Watermark = HMAC-SHA256(K_master_trace, user_id) into every issued key package. An automated tracing procedure (trace_leaked_key) "
        "extracts the embedded tag from discovered key material and maps it to the registered user ID with 100% mathematical certainty.",
        body_style
    ))

    # Section IV
    story.append(Paragraph("IV. EXPERIMENTAL EVALUATION & RESULTS", sec_style))
    story.append(Paragraph(
        "The complete MediCloud implementation was evaluated on a macOS workstation equipped with Python 3.13 and the standard cryptography library. "
        "Sixteen distinct functional security and cryptographic tests were executed against synthetic clinical EHR records.",
        body_style
    ))

    story.append(Paragraph("A. Comprehensive Security Verification (16 / 16 Tests Passed)", subsec_style))
    story.append(Paragraph(
        "Table I summarizes the 16 executed security test cases, their expected cryptographic responses, observed behaviors, and verification statuses. "
        "All 16 test cases achieved a 100% pass rate.",
        body_style
    ))

    # Table 1: Security tests
    t1_data = [["Test Case", "Expected Outcome", "Observed Outcome", "Status"]]
    with open("data/security_tests.csv", "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) >= 4:
                t1_data.append([row[0], row[1], row[2], row[3]])

    t1 = Table(t1_data, colWidths=[2.2*inch, 2.0*inch, 2.0*inch, 0.7*inch])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0D1B2A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 7.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('ALIGN', (3,0), (3,-1), 'CENTER'),
        ('TEXTCOLOR', (3,1), (3,-1), colors.HexColor('#2A9D8F')),
        ('FONTNAME', (3,1), (3,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,1), (-1,-1), 7),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DEE2E6')),
    ]))
    story.append(t1)
    story.append(Spacer(1, 8))

    if os.path.exists("figures/security_tests.png"):
        story.append(Image("figures/security_tests.png", width=4.5*inch, height=2.3*inch))
        story.append(Paragraph("Fig. 2. Functional security test verification breakdown (16/16 Passed).", cap_style))

    if os.path.exists("figures/security_radar.png"):
        story.append(Image("figures/security_radar.png", width=4.5*inch, height=3.6*inch))
        story.append(Paragraph("Fig. 3. Six-axis security and SRE capability profile: Baseline ABAC prototype vs. Full MediCloud Architecture.", cap_style))

    story.append(Paragraph("B. Microbenchmark Performance & SRE Latency", subsec_style))
    story.append(Paragraph(
        "Microbenchmarks were conducted across batch sizes of 1, 10, 50, and 100 records. Table II displays the observed latencies in milliseconds.",
        body_style
    ))

    t2_data = [["Batch", "Encryption (ms)", "Decryption (ms)", "Search (ms)", "Policy (ms)", "Total (ms)"]]
    with open("data/performance.csv", "r") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) >= 6:
                t2_data.append([
                    row[0],
                    f"{float(row[1]):.4f}",
                    f"{float(row[2]):.4f}",
                    f"{float(row[4]):.4f}",
                    f"{float(row[3]):.4f}",
                    f"{float(row[5]):.4f}"
                ])

    t2 = Table(t2_data, colWidths=[1.1*inch, 1.2*inch, 1.2*inch, 1.1*inch, 1.1*inch, 1.2*inch])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0D1B2A')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 7.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTSIZE', (0,1), (-1,-1), 7.5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DEE2E6')),
    ]))
    story.append(t2)
    story.append(Spacer(1, 8))

    if os.path.exists("figures/performance.png"):
        story.append(Image("figures/performance.png", width=4.6*inch, height=2.6*inch))
        story.append(Paragraph("Fig. 4. Microbenchmark latency curves across record batches.", cap_style))

    if os.path.exists("figures/latency_breakdown.png"):
        story.append(Image("figures/latency_breakdown.png", width=4.6*inch, height=2.6*inch))
        story.append(Paragraph("Fig. 5. Cryptographic latency breakdown per upload operation.", cap_style))

    if os.path.exists("figures/pre_vs_traditional.png"):
        story.append(Image("figures/pre_vs_traditional.png", width=5.0*inch, height=2.1*inch))
        story.append(Paragraph("Fig. 6. SRE bandwidth and CPU comparison: Proxy Re-Encryption vs. Traditional Re-Upload.", cap_style))

    if os.path.exists("figures/trust_decay_timeline.png"):
        story.append(Image("figures/trust_decay_timeline.png", width=4.8*inch, height=2.5*inch))
        story.append(Paragraph("Fig. 7. Dynamic behavioral trust score trajectory under legitimate use, idle decay, and automated quarantine.", cap_style))

    if os.path.exists("figures/sse_search_scaling.png"):
        story.append(Image("figures/sse_search_scaling.png", width=4.6*inch, height=2.4*inch))
        story.append(Paragraph("Fig. 8. Searchable Symmetric Encryption (SSE) query scalability across catalog sizes.", cap_style))

    # Section V
    story.append(Paragraph("V. DISCUSSION & SRE IMPLICATIONS", sec_style))
    story.append(Paragraph(
        "The empirical findings demonstrate that MediCloud resolves key operational tensions in cloud healthcare data sharing:<br/>"
        "<b>1. Bandwidth and Availability:</b> Traditional staff revocation requires downloading, decrypting, and re-uploading gigabytes of clinical records. "
        "As illustrated in Fig. 6, MediCloud's BBS98 PRE achieves O(1) constant client bandwidth by delegating blind re-encryption to cloud servers.<br/>"
        "<b>2. Clinical Usability:</b> Searchable symmetric encryption allows instantaneous keyword queries (~0.0026 ms) while keeping diagnostic tags fully confidential from the cloud provider.<br/>"
        "<b>3. Adaptive Resilience:</b> Static cryptographic keys cannot prevent misuse by compromised legitimate accounts. MediCloud's behavioral trust engine "
        "detects lateral reconnaissance probes and quarantines compromised credentials in real time before data exfiltration occurs.<br/>"
        "<b>4. Insider Accountability:</b> Cryptographic traitor tracing closes the accountability gap, providing mathematical proof of identity if secret keys are leaked.",
        body_style
    ))

    # Section VI
    story.append(Paragraph("VI. CONCLUSION & FUTURE WORK", sec_style))
    story.append(Paragraph(
        "This research successfully transformed Pan Jun Sun's theoretical cloud privacy framework into a complete, verified, and performant prototype. "
        "By interlocking AES-256-GCM, searchable encryption, multi-authority governance, BBS98 proxy re-encryption, behavioral trust telemetry, and traitor tracing, "
        "MediCloud establishes a practical blueprint for secure multi-hospital healthcare collaboration. "
        "Future engineering milestones include integrating Hardware Security Modules (CloudHSM / KMS), deploying Zero-Knowledge Proofs (ZKPs) for private credential verification, "
        "and evaluating Post-Quantum Cryptography (PQC) lattice-based replacements for discrete logarithm groups.",
        body_style
    ))

    # References
    story.append(Paragraph("REFERENCES", sec_style))
    refs = [
        "[1] P. J. Sun, 'Privacy Protection and Data Security in Cloud Computing: A Survey, Challenges, and Solutions,' <i>IEEE Access</i>, vol. 7, pp. 147420–147452, 2019.",
        "[2] M. Blaze, G. Bleumer, and M. Strauss, 'Divertible protocols and atomic proxy cryptography,' in <i>Advances in Cryptology — EUROCRYPT '98</i>, Berlin: Springer, 1998, pp. 127–144.",
        "[3] R. Curtmola, J. Garay, S. Kamara, and R. Ostrovsky, 'Searchable symmetric encryption: Improved definitions and efficient constructions,' in <i>ACM CCS</i>, 2006, pp. 79–88.",
        "[4] V. Goyal, O. Pandey, A. Sahai, and B. Waters, 'Attribute-based encryption for fine-grained access control of encrypted data,' in <i>ACM CCS</i>, 2006, pp. 89–98.",
        "[5] M. Li, S. Yu, Y. Zheng, K. Ren, and W. Lou, 'Scalable and secure sharing of personal health records in cloud computing using attribute-based encryption,' <i>IEEE TPDS</i>, vol. 24, no. 1, pp. 131–143, 2013."
    ]
    for r in refs:
        story.append(Paragraph(r, body_style))

    doc.build(story)
    print(f"MediCloud_Research_Paper.pdf successfully generated: {pdf_filename}")

if __name__ == "__main__":
    build_pdf()
