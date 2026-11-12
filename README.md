# MediCloud: Privacy-Preserving Cloud Data Sharing for Multi-Hospital EHRs

[![Security Tests](https://img.shields.io/badge/Security%20Tests-16%2F16%20Passed-brightgreen)](file:///Users/divyanshu/Desktop/Cloud%20SRE/cloud_sre_medicloud_submission/data/security_tests.csv)
[![License: Academic](https://img.shields.io/badge/License-Academic%20Research-blue)](file:///Users/divyanshu/Desktop/Cloud%20SRE/cloud_sre_medicloud_submission/MediCloud_Research_Paper.pdf)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-informational)](file:///Users/divyanshu/Desktop/Cloud%20SRE/cloud_sre_medicloud_submission/medicloud.py)

**Course:** Cloud SRE and Security  
**Institution:** Indian Institute of Information Technology Dharwad  
**Author:** MOHIT (Roll No.: 25BDA069)  
**Theoretical Foundation:** Pan Jun Sun, *"Privacy Protection and Data Security in Cloud Computing: A Survey, Challenges, and Solutions"*, **IEEE Access**, vol. 7, 2019.

---

## 1. Project Overview

**MediCloud** is a secure, privacy-preserving cloud data-sharing architecture designed for multi-hospital Electronic Health Record (EHR) exchange over semi-trusted public cloud infrastructure.

This implementation realizes all foundational cryptographic and SRE controls surveyed by Pan Jun Sun (2019):

* **Phase 1: Searchable Symmetric Encryption (SSE)**
  - Blind HMAC-SHA256 inverted trapdoor indexing.
  - Allows clinicians to query encrypted patient records by diagnosis or specialty with **zero plaintext keyword leakage** to the cloud provider.
* **Phase 2: Decentralized Multi-Authority Access Control (MA-ABAC)**
  - Partitions credential issuance across autonomous trust domains:
    - **Central Medical Council (CMA):** National professional roles (`role:doctor`, `license:active`).
    - **Hospital Authorities (HA-A, HA-B):** Institutional affiliations (`hospital:hospital_a`, `dept:cardiology`).
    - **Diagnostic Labs (DLA):** Laboratory clearance.
  - Eliminates single-master-key bottlenecks and cryptographically rejects cross-organizational forgery.
* **Phase 3: BBS98 Proxy Re-Encryption (PRE) for Dynamic Revocation**
  - Textbook ElGamal PRE implemented over RFC 3526 1024-bit MODP safe prime fields ($g=2, p$).
  - When medical personnel depart, the authority computes an algebraic re-encryption key:
    $$rk_{A \to B} = sk_A^{-1} \cdot sk_B \pmod q$$
  - The semi-trusted cloud transforms ciphertexts blindly from Group A to Group B **without decrypting or learning patient data**, achieving $O(1)$ client bandwidth savings and immediate departed staff lockout.
* **Phase 4: Dynamic Behavioral Trust & Reputation Engine**
  - Realizes Sun's 4 trust pillars: Formation, Dynamic Updates, Exponential Time Decay ($e^{-\lambda \Delta t}$), and Access Gating.
  - Telemetry tracks behavioral integrity: bonuses for valid queries ($+0.05$), penalties for cross-hospital probes ($-0.25$), and expired requests ($-0.15$).
  - Interlocking dual gate: automatically quarantines accounts falling below the $0.40$ trust threshold, blocking access even if static attributes match.
* **Phase 5: Cryptographic Traitor Tracing**
  - Embeds unique HMAC-SHA256 identity watermarks into user key packages.
  - Pinpoints the exact rogue employee ID with 100% mathematical certainty if a private decryption key is leaked in the wild.
* **Core Cryptographic & SRE Baseline**
  - **AES-256-GCM** Authenticated Encryption with Additional Authenticated Data (AAD) record binding.
  - **SHA-256** tamper-evident integrity digests.
  - Centralized, tamper-resistant access audit trails.

---

## 2. Directory Structure

```text
cloud_sre_medicloud_submission/
├── medicloud.py                 # Core system, test suite runner, and microbenchmarks
├── README.md                    # Project documentation and guide
├── results_summary.json         # Consolidated test outcomes & benchmark JSON
├── MediCloud_Presentation.pptx  # 11-slide presentation deck with embedded figures
├── MediCloud_Research_Paper.docx# Academic research paper (Word) with all 8 figures
├── MediCloud_Research_Paper.pdf # Compiled academic research paper (PDF)
├── data/
│   ├── security_tests.csv       # Execution log of all 16 security test cases
│   ├── performance.csv          # Microbenchmark timings across batch sizes
│   └── audit_log.json           # Comprehensive access audit events
├── figures/                     # Publication-quality scientific figures
│   ├── architecture.png         # Multi-hospital cloud threat model & architecture
│   ├── security_tests.png       # 16/16 test verification bar chart
│   ├── security_radar.png       # 6-axis security coverage profile
│   ├── performance.png          # Latency scaling curves (1, 10, 50, 100 records)
│   ├── latency_breakdown.png    # Cryptographic upload pipeline breakdown
│   ├── pre_vs_traditional.png   # SRE efficiency: PRE vs. Traditional re-upload
│   ├── trust_decay_timeline.png # Dynamic trust evolution & quarantine timeline
│   ├── sse_search_scaling.png   # SSE query latency vs. catalog size
│   └── multi_authority_scaling.png # Multi-authority evaluation overhead
├── cloud_storage/               # Simulated semi-trusted cloud repository
│   ├── ehr001.json              # Encrypted EHR payload (nonce, ciphertext, hash, metadata)
│   ├── ehr002.json              # Encrypted EHR payload
│   └── cloud_search_index.json  # Blind trapdoor index (zero plaintext words)
├── generate_all_plots.py        # Scientific plotting script
├── create_presentation.py       # Presentation builder script
├── update_paper.py              # Research paper document builder
└── generate_paper_pdf.py        # PDF paper compiler
```

---

## 3. Installation & Execution

### Prerequisites
- Python 3.9+
- Standard libraries + `cryptography`, `matplotlib`, `python-pptx`, `reportlab`:

```bash
python3 -m pip install cryptography matplotlib python-pptx reportlab
```

### Running the System
To execute the comprehensive **16-test security verification** and **microbenchmark evaluation**:

```bash
python3 medicloud.py
```

This single command:
1. Runs all 16 automated cryptographic and functional security tests.
2. Executes microbenchmarks over record batches (1, 10, 50, 100 records).
3. Updates `data/security_tests.csv`, `data/performance.csv`, `data/audit_log.json`, `results_summary.json`, and charts in `figures/`.

---

## 4. Security Test Results (16 / 16 PASSED)

| # | Security Test Case | Expected Outcome | Observed Outcome | Status | Explanation |
| :-: | :--- | :--- | :--- | :-: | :--- |
| **1** | **Authorized Doctor** | `SUCCESS` | `SUCCESS` | **PASS** | Matching role, hospital, and department attributes. |
| **2** | **Cross-Hospital Isolation** | `ATTRIBUTE_POLICY_DENIED` | `ATTRIBUTE_POLICY_DENIED` | **PASS** | Hospital-B identity lacks Hospital-A attributes. |
| **3** | **Cloud Operator Access** | `ATTRIBUTE_POLICY_DENIED` | `ATTRIBUTE_POLICY_DENIED` | **PASS** | Cloud admin does not satisfy clinical doctor policy. |
| **4** | **Expired Access** | `ACCESS_EXPIRED` | `ACCESS_EXPIRED` | **PASS** | Authorization timestamp is in the past. |
| **5** | **Modified Ciphertext** | `INTEGRITY_FAILED` | `INTEGRITY_FAILED` | **PASS** | Ciphertext hash does not match stored SHA-256 digest. |
| **6** | **Audit Logging** | `SUCCESS` | `SUCCESS` | **PASS** | Every attempted access is recorded with identity and outcome. |
| **7** | **Cloud Plaintext Visibility** | `CIPHERTEXT_ONLY` | `CIPHERTEXT_ONLY` | **PASS** | Cloud sees only nonce, ciphertext, and hashes—no diagnosis. |
| **8** | **SSE Keyword Search** | `MATCH_FOUND` | `MATCH_FOUND` | **PASS** | Client derives blind trapdoor; cloud matches record without decrypting index. |
| **9** | **SSE Cloud Index Privacy** | `TRAPDOORS_ONLY` | `TRAPDOORS_ONLY` | **PASS** | Cloud index contains only HMAC-SHA256 hex hashes, zero plain keywords. |
| **10** | **PRE Cloud Delegation** | `SUCCESS` | `SUCCESS` | **PASS** | Cloud blindly transforms ciphertext from Group A to Group B. |
| **11** | **PRE Staff Revocation** | `PRE_DECAPSULATION_FAILED` | `PRE_DECAPSULATION_FAILED` | **PASS** | Departed staff's old key fails decapsulation on re-encrypted records. |
| **12** | **Multi-Authority Access** | `SUCCESS` | `SUCCESS` | **PASS** | Valid credentials independently signed by CMA and Hospital-A. |
| **13** | **Multi-Authority Cross-Org Forgery** | `FAIL` | `FAIL` | **PASS** | Hospital-B cannot impersonate Hospital-A; signature check rejects forgery. |
| **14** | **Dynamic Trust Elevation** | `SCORE_INCREASED` | `SCORE_INCREASED` | **PASS** | Trust score increases ($0.60 \to 0.75$) with verified activity. |
| **15** | **Dynamic Trust Quarantine** | `TRUST_SCORE_INSUFFICIENT` | `TRUST_SCORE_INSUFFICIENT` | **PASS** | Trust drops below $0.40$; user is quarantined despite valid attributes. |
| **16** | **Traitor Tracing Key Leak** | `TRAITOR_IDENTIFIED` | `TRAITOR_IDENTIFIED` | **PASS** | Embedded watermark accurately identifies the rogue employee (`D-ROUGE-42`). |

---

## 5. Performance & SRE Benchmarks

Local microbenchmarks demonstrate sub-millisecond execution times:

| Batch Size | Avg Encryption (ms) | Avg Decryption (ms) | Avg Search Query (ms) | Avg Policy Check (ms) | Total Pipeline (ms) |
| :-: | :-: | :-: | :-: | :-: | :-: |
| **1 Record** | 0.5188 | 0.0795 | 0.0067 | 0.0040 | 0.5983 |
| **10 Records** | 0.4420 | 0.0607 | 0.0030 | 0.0011 | 0.5027 |
| **50 Records** | 0.5511 | 0.0554 | 0.0026 | 0.0008 | 0.6065 |
| **100 Records** | 0.4843 | 0.0561 | 0.0026 | 0.0007 | 0.5404 |

---

## 6. Disclaimer

> [!WARNING]
> All clinical records, patient identifiers, and diagnostic entries used in this repository are **entirely synthetic** and generated solely for academic benchmarking and laboratory demonstration. **Do not use real patient data.**

# Cloud-SRE---MediCloud
