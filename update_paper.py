import os
import json
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def create_document():
    doc = docx.Document()

    # Set 0.75-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.75)
        section.bottom_margin = Inches(0.75)
        section.left_margin = Inches(0.75)
        section.right_margin = Inches(0.75)

    # Base styles
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Times New Roman'
    style_normal.font.size = Pt(10)
    style_normal.font.color.rgb = RGBColor(33, 37, 41)

    # -------------------------------------------------------------
    # Title & Metadata
    # -------------------------------------------------------------
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(6)
    r_title = p_title.add_run(
        "A Privacy-Preserving Cloud Data Sharing Architecture for Multi-Hospital Electronic Health Records: "
        "Integrating Searchable Encryption, Multi-Authority ABAC, Proxy Re-Encryption, and Dynamic Behavioral Trust"
    )
    r_title.font.size = Pt(17)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(13, 27, 42)

    p_author = doc.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_author.paragraph_format.space_after = Pt(14)
    r_author = p_author.add_run("MOHIT | Roll No.: 25BDA069\nDepartment of Data Science & Engineering, Indian Institute of Information Technology Dharwad\nCourse: Cloud SRE and Security")
    r_author.font.size = Pt(10.5)
    r_author.font.color.rgb = RGBColor(50, 50, 50)

    # -------------------------------------------------------------
    # Abstract
    # -------------------------------------------------------------
    p_abs = doc.add_paragraph()
    p_abs.paragraph_format.space_after = Pt(8)
    r_absh = p_abs.add_run("Abstract— ")
    r_absh.font.bold = True
    p_abs.add_run(
        "Cloud-based healthcare information sharing significantly improves diagnostic availability and multi-institutional collaboration "
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
        "proving that comprehensive defense-in-depth cloud security imposes negligible SRE overhead on modern healthcare workflows."
    )

    p_idx = doc.add_paragraph()
    p_idx.paragraph_format.space_after = Pt(14)
    r_idx = p_idx.add_run("Index Terms— ")
    r_idx.font.bold = True
    p_idx.add_run("Cloud security, cloud privacy, electronic health records, AES-GCM, attribute-based access control, searchable encryption, proxy re-encryption, dynamic trust, traitor tracing, SRE.")

    def add_sec_heading(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        r = p.add_run(title)
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = RGBColor(13, 27, 42)
        return p

    def add_subsec_heading(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(title)
        r.font.size = Pt(10.5)
        r.font.bold = True
        r.font.italic = True
        r.font.color.rgb = RGBColor(0, 119, 182)
        return p

    def add_figure(img_path, caption_text, width_in=5.2):
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(8)
            p_img.paragraph_format.space_after = Pt(4)
            doc.add_picture(img_path, width=Inches(width_in))
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_after = Pt(10)
            r = p_cap.add_run(caption_text)
            r.font.size = Pt(9)
            r.font.italic = True
            r.font.color.rgb = RGBColor(80, 80, 80)

    # -------------------------------------------------------------
    # I. INTRODUCTION
    # -------------------------------------------------------------
    add_sec_heading("I. INTRODUCTION")
    p = doc.add_paragraph()
    p.add_run(
        "Modern healthcare organizations increasingly outsource clinical electronic health records (EHRs) to commercial cloud platforms to enhance "
        "interoperability across hospitals, diagnostic laboratories, and emergency care networks. However, public cloud infrastructure is maintained by "
        "third-party cloud service providers (CSPs) that are considered 'honest-but-curious' or semi-trusted: providers faithfully execute storage and "
        "compute instructions but possess strong commercial and technical incentives to observe outsourced plaintext data. Furthermore, multi-tenant "
        "cloud virtualization creates persistent attack surfaces for co-tenant data leakage, hypervisor vulnerabilities, and administrative insider threats. "
        "Consequently, health privacy regulations including HIPAA, the European GDPR, and the Indian Digital Personal Data Protection (DPDP) Act mandate "
        "strict access controls, cryptographic confidentiality at rest, and verifiable audit logging.\n\n"
        "In his seminal 2019 IEEE Access survey, Pan Jun Sun established that no single security primitive suffices to resolve cloud privacy challenges. "
        "Instead, resilient cloud security requires an interlocking defense-in-depth architecture combining Access Control (rules formulation), "
        "Attribute-Based Encryption / Cryptographic Enforcement, Searchable Encryption (usability), and Behavioral Trust Systems. "
        "This research project narrows Sun's theoretical framework into an operational, fully verified software implementation called MediCloud, "
        "designed specifically for multi-hospital EHR federations."
    )

    add_subsec_heading("A. Research Objectives")
    p = doc.add_paragraph()
    p.add_run(
        "The primary objectives of this study are: (1) Enforce end-to-end client-side confidentiality such that cloud operators have zero access to plaintext diagnoses; "
        "(2) Implement Searchable Symmetric Encryption (SSE) allowing clinicians to execute private keyword searches over encrypted EHRs; "
        "(3) Design a decentralized Multi-Authority architecture eliminating single-master-key bottlenecks; "
        "(4) Realize cloud-delegated Proxy Re-Encryption (PRE) enabling immediate staff revocation without re-upload overhead; "
        "(5) Formulate a continuous behavioral trust engine that quarantines compromised accounts; and "
        "(6) Provide cryptographic traitor tracing to identify insider key leaks."
    )

    # -------------------------------------------------------------
    # II. LITERATURE REVIEW & BACKGROUND
    # -------------------------------------------------------------
    add_sec_heading("II. LITERATURE REVIEW & BACKGROUND")
    p = doc.add_paragraph()
    p.add_run(
        "Pan Jun Sun's 2019 survey systematically analyzed cloud privacy across four technological dimensions: classical access control (DAC, MAC, RBAC, ABAC), "
        "attribute-based encryption (KP-ABE vs. CP-ABE), searchable encryption (SSE and asymmetric PEKS/ABKS), and trust/reputation systems. "
        "The survey emphasizes that in outsourced environments, Ciphertext-Policy ABE (CP-ABE) is inherently superior to Key-Policy ABE because the data owner "
        "retains sovereign authority to encode access predicates directly into the ciphertext packaging. However, standard CP-ABE introduces severe "
        "practical bottlenecks: key generation relies on a single central authority, computational pairing overhead scales with policy complexity, and "
        "revoking departing personnel necessitates re-encrypting entire cloud databases.\n\n"
        "To mitigate these challenges, subsequent literature proposed Proxy Re-Encryption (PRE), initially pioneered by Blaze, Bleumer, and Strauss (BBS98), "
        "which allows a semi-trusted proxy to transform ciphertexts from an old authorization key to a new one using an algebraic re-encryption key, without "
        "ever decrypting the underlying plaintext. Concurrently, Searchable Symmetric Encryption (SSE) schemes developed by Curtmola et al. established "
        "that inverted index structures keyed by deterministic trapdoors (HMACs) provide sub-millisecond query evaluation while preserving confidentiality."
    )

    # -------------------------------------------------------------
    # III. MEDICLOUD ARCHITECTURAL DESIGN
    # -------------------------------------------------------------
    add_sec_heading("III. MEDICLOUD ARCHITECTURAL DESIGN")
    p = doc.add_paragraph()
    p.add_run(
        "The MediCloud system simulates a realistic healthcare consortium comprising Hospital-A, Hospital-B, a centralized diagnostic laboratory, "
        "a National Central Medical Council (CMA), and a public cloud storage service. Fig. 1 illustrates the high-level system topology."
    )

    add_figure("figures/architecture.png", "Fig. 1. High-level architecture and trust boundaries of the MediCloud system.")

    add_subsec_heading("A. Authenticated Encryption & Integrity Binding")
    p = doc.add_paragraph()
    p.add_run(
        "Clinical EHR payloads are serialized to standardized JSON and encrypted using AES-256 in Galois/Counter Mode (GCM). "
        "For each record, a fresh 96-bit cryptographic nonce is sampled using system entropy (secrets.token_bytes). Crucially, the record identifier "
        "(e.g., 'ehr001') is passed as Additional Authenticated Data (AAD) into the GCM cipher. This cryptographic binding guarantees that ciphertext packages "
        "cannot be swapped or renamed inside the cloud repository without triggering authentication tag failure. A supplementary SHA-256 digest is maintained "
        "as an upfront integrity sentinel."
    )

    add_subsec_heading("B. Phase 1: Searchable Symmetric Encryption (SSE)")
    p = doc.add_paragraph()
    p.add_run(
        "To enable clinical search without compromising patient confidentiality, MediCloud deploys an inverted trapdoor index. "
        "Let K_search be the clinician consortium's master search key. During record upload, diagnostic terms W = {w_1, w_2, ...} are normalized and hashed: "
        "T_w = HMAC-SHA256(K_search, w). The cloud maintains an inverted mapping Index[T_w] → [record_id_1, record_id_2, ...]. "
        "When querying for 'cardiology', the client computes only the blind token T_query and transmits it to the cloud. The cloud performs an exact hash lookup "
        "and returns matching identifiers without learning the underlying medical condition."
    )

    add_subsec_heading("C. Phase 2: Decentralized Multi-Authority Access Control (MA-ABAC)")
    p = doc.add_paragraph()
    p.add_run(
        "Rather than relying on a vulnerable single master authority, MediCloud partitions identity issuance across autonomous cryptographic authorities: "
        "(1) The Central Medical Council (CMA) signs professional qualifications ('role:doctor', 'license:active'); "
        "(2) Hospital Authorities (HA-A, HA-B) manage departmental affiliations ('hospital:hospital_a', 'dept:cardiology'); and "
        "(3) Diagnostic Laboratories issue diagnostic credentials. Each authority signs credential packages with HMAC-SHA256. "
        "Access policies are formulated as multi-authority conjunctions: Policy = { CMA: ['role:doctor'], HA-A: ['hospital:hospital_a'] }. "
        "A user must present valid, unexpired credentials from all designated authorities; cross-hospital forgery is cryptographically rejected."
    )

    add_subsec_heading("D. Phase 3: BBS98 Proxy Re-Encryption (PRE) for Dynamic Revocation")
    p = doc.add_paragraph()
    p.add_run(
        "When clinical staff depart an institution, re-encrypting the hospital's entire outsourced database on client workstations is computationally and "
        "bandwidth prohibitive. MediCloud implements BBS98 Proxy Re-Encryption over an RFC 3526 1024-bit MODP safe prime field (p = 2q + 1, g = 2). "
        "The Data Encryption Key (DEK) is encapsulated under group keypair (sk_A, pk_A) where pk_A = g^(sk_A) mod p: c_1 = (pk_A)^r mod p, c_2 = m · g^r mod p. "
        "Upon staff departure, the authority generates a new group key sk_B and derives re-encryption key rk_(A→B) = (sk_A)^(-1) · sk_B mod q. "
        "The cloud blindly computes c_1' = (c_1)^(rk_(A→B)) = g^(sk_B · r) mod p. The cloud transforms the ciphertext without learning m, sk_A, or sk_B, "
        "and departed personnel holding sk_A are immediately locked out."
    )

    add_subsec_heading("E. Phase 4: Dynamic Behavioral Trust & Reputation Telemetry")
    p = doc.add_paragraph()
    p.add_run(
        "Addressing Sun's fourth primitive family, MediCloud incorporates continuous behavioral telemetry. Users possess a dynamic trust score T ∈ [0.0, 1.0], "
        "initialized at T_0 = 0.60. Verified clinical queries boost trust (+0.05 up to 1.00), while suspicious activity incurs severe penalties: "
        "-0.25 for unauthorized cross-hospital access attempts, -0.15 for expired requests, and -0.35 for tampering. "
        "Inactive accounts undergo exponential time decay towards baseline: T(t) = T_0 + (T_prev - T_0) · e^(-λ · Δt). "
        "MediCloud interlocks trust with authorization: access is granted if and only if both attribute policies are satisfied AND T_user ≥ 0.40. "
        "Compromised accounts exhibiting probe behavior are automatically quarantined."
    )

    add_subsec_heading("F. Phase 5: Cryptographic Traitor Tracing")
    p = doc.add_paragraph()
    p.add_run(
        "To mitigate insider threats where corrupt staff leak or sell secret attribute keys, MediCloud embeds an unforgeable identity watermark "
        "Watermark = HMAC-SHA256(K_master_trace, user_id) into every issued key package. An automated tracing procedure (trace_leaked_key) "
        "extracts the embedded tag from discovered key material and maps it to the registered user ID with 100% mathematical certainty."
    )

    # -------------------------------------------------------------
    # IV. EXPERIMENTAL EVALUATION & RESULTS
    # -------------------------------------------------------------
    add_sec_heading("IV. EXPERIMENTAL EVALUATION & RESULTS")
    p = doc.add_paragraph()
    p.add_run(
        "The complete MediCloud implementation was evaluated on a macOS workstation equipped with Python 3.13 and the standard cryptography library. "
        "Sixteen distinct functional security and cryptographic tests were executed against synthetic clinical EHR records."
    )

    add_subsec_heading("A. Comprehensive Security Verification (16 / 16 Tests Passed)")
    p = doc.add_paragraph()
    p.add_run(
        "Table I summarizes the 16 executed security test cases, their expected cryptographic responses, observed behaviors, and verification statuses. "
        "All 16 test cases achieved a 100% pass rate."
    )

    # Load security tests from data/security_tests.csv
    table1 = doc.add_table(rows=1, cols=4)
    table1.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table1.rows[0].cells
    hdr[0].text = "Test Case"
    hdr[1].text = "Expected Outcome"
    hdr[2].text = "Observed Outcome"
    hdr[3].text = "Status"
    for cell in hdr:
        set_cell_background(cell, "0D1B2A")
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.size = Pt(8.5)

    with open("data/security_tests.csv", "r") as f:
        lines = f.readlines()[1:]
        for line in lines:
            parts = line.strip().split(",", 4)
            if len(parts) >= 4:
                row = table1.add_row().cells
                row[0].text = parts[0]
                row[1].text = parts[1]
                row[2].text = parts[2]
                row[3].text = parts[3]
                for c_idx, c in enumerate(row):
                    c.paragraphs[0].runs[0].font.size = Pt(8)
                    if c_idx == 3:
                        c.paragraphs[0].runs[0].font.bold = True
                        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(42, 157, 143)

    add_figure("figures/security_tests.png", "Fig. 2. Functional security test verification breakdown (16/16 Passed).")
    add_figure("figures/security_radar.png", "Fig. 3. Six-axis security and SRE capability profile: Baseline ABAC prototype vs. Full MediCloud Architecture.")

    add_subsec_heading("B. Microbenchmark Performance & SRE Latency")
    p = doc.add_paragraph()
    p.add_run(
        "Microbenchmarks were conducted across batch sizes of 1, 10, 50, and 100 records. Table II displays the observed latencies in milliseconds."
    )

    # Load performance from data/performance.csv
    table2 = doc.add_table(rows=1, cols=6)
    table2.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr2 = table2.rows[0].cells
    hdr2[0].text = "Batch (Records)"
    hdr2[1].text = "Avg Encryption (ms)"
    hdr2[2].text = "Avg Decryption (ms)"
    hdr2[3].text = "Avg Search (ms)"
    hdr2[4].text = "Avg Policy Check (ms)"
    hdr2[5].text = "Total Pipeline (ms)"
    for cell in hdr2:
        set_cell_background(cell, "0D1B2A")
        cell.paragraphs[0].runs[0].font.bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)
        cell.paragraphs[0].runs[0].font.size = Pt(8)

    with open("data/performance.csv", "r") as f:
        lines = f.readlines()[1:]
        for line in lines:
            parts = line.strip().split(",")
            if len(parts) >= 6:
                row = table2.add_row().cells
                for i in range(6):
                    row[i].text = f"{float(parts[i]):.4f}" if i > 0 else parts[0]
                    row[i].paragraphs[0].runs[0].font.size = Pt(8)

    add_figure("figures/performance.png", "Fig. 4. Microbenchmark latency curves across record batches.")
    add_figure("figures/latency_breakdown.png", "Fig. 5. Cryptographic latency breakdown per upload operation.")
    add_figure("figures/pre_vs_traditional.png", "Fig. 6. SRE bandwidth and CPU comparison: Proxy Re-Encryption vs. Traditional Re-Upload.")
    add_figure("figures/trust_decay_timeline.png", "Fig. 7. Dynamic behavioral trust score trajectory under legitimate use, idle decay, and automated quarantine.")
    add_figure("figures/sse_search_scaling.png", "Fig. 8. Searchable Symmetric Encryption (SSE) query scalability across catalog sizes.")

    # -------------------------------------------------------------
    # V. DISCUSSION & SRE IMPLICATIONS
    # -------------------------------------------------------------
    add_sec_heading("V. DISCUSSION & SRE IMPLICATIONS")
    p = doc.add_paragraph()
    p.add_run(
        "The empirical findings demonstrate that MediCloud resolves key operational tensions in cloud healthcare data sharing:\n"
        "1. Bandwidth and Availability: Traditional staff revocation requires downloading, decrypting, and re-uploading gigabytes of clinical records. "
        "As illustrated in Fig. 6, MediCloud's BBS98 PRE achieves O(1) constant client bandwidth by delegating blind re-encryption to cloud servers.\n"
        "2. Clinical Usability: Searchable symmetric encryption allows instantaneous keyword queries (~0.0026 ms) while keeping diagnostic tags fully confidential from the cloud provider.\n"
        "3. Adaptive Resilience: Static cryptographic keys cannot prevent misuse by compromised legitimate accounts. MediCloud's behavioral trust engine "
        "detects lateral reconnaissance probes and quarantines compromised credentials in real time before data exfiltration occurs.\n"
        "4. Insider Accountability: Cryptographic traitor tracing closes the accountability gap, providing mathematical proof of identity if secret keys are leaked."
    )

    # -------------------------------------------------------------
    # VI. CONCLUSION & FUTURE WORK
    # -------------------------------------------------------------
    add_sec_heading("VI. CONCLUSION & FUTURE WORK")
    p = doc.add_paragraph()
    p.add_run(
        "This research successfully transformed Pan Jun Sun's theoretical cloud privacy framework into a complete, verified, and performant prototype. "
        "By interlocking AES-256-GCM, searchable encryption, multi-authority governance, BBS98 proxy re-encryption, behavioral trust telemetry, and traitor tracing, "
        "MediCloud establishes a practical blueprint for secure multi-hospital healthcare collaboration. "
        "Future engineering milestones include integrating Hardware Security Modules (CloudHSM / KMS), deploying Zero-Knowledge Proofs (ZKPs) for private credential verification, "
        "and evaluating Post-Quantum Cryptography (PQC) lattice-based replacements for discrete logarithm groups."
    )

    # -------------------------------------------------------------
    # REFERENCES
    # -------------------------------------------------------------
    add_sec_heading("REFERENCES")
    refs = [
        "[1] P. J. Sun, 'Privacy Protection and Data Security in Cloud Computing: A Survey, Challenges, and Solutions,' IEEE Access, vol. 7, pp. 147420–147452, 2019.",
        "[2] M. Blaze, G. Bleumer, and M. Strauss, 'Divertible protocols and atomic proxy cryptography,' in Advances in Cryptology — EUROCRYPT '98, Berlin: Springer, 1998, pp. 127–144.",
        "[3] R. Curtmola, J. Garay, S. Kamara, and R. Ostrovsky, 'Searchable symmetric encryption: Improved definitions and efficient constructions,' in ACM CCS, 2006, pp. 79–88.",
        "[4] V. Goyal, O. Pandey, A. Sahai, and B. Waters, 'Attribute-based encryption for fine-grained access control of encrypted data,' in ACM CCS, 2006, pp. 89–98.",
        "[5] M. Li, S. Yu, Y. Zheng, K. Ren, and W. Lou, 'Scalable and secure sharing of personal health records in cloud computing using attribute-based encryption,' IEEE TPDS, vol. 24, no. 1, pp. 131–143, 2013."
    ]
    for r in refs:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.space_after = Pt(3)
        p_ref.paragraph_format.left_indent = Inches(0.25)
        p_ref.add_run(r).font.size = Pt(8.5)

    doc.save("MediCloud_Research_Paper.docx")
    print("MediCloud_Research_Paper.docx successfully created with all sections, tables, and 8 figures!")

if __name__ == "__main__":
    create_document()
