"""
MediCloud Interactive Web Application Dashboard
Demonstrates:
  1. Client-side Authenticated Encryption (AES-256-GCM)
  2. Searchable Symmetric Encryption (SSE) blind trapdoor queries
  3. Multi-Authority Access Control (CMA, Hospital-A, Hospital-B, Lab)
  4. Proxy Re-Encryption (BBS98) staff revocation
  5. Dynamic Behavioral Trust & Automated Quarantine
  6. Semi-trusted Cloud Storage Inspector (zero plaintext verification)
"""
import os
import json
import secrets
from flask import Flask, render_template_string, request, jsonify
from medicloud import MediCloud, AttributeAuthority

app = Flask(__name__)
system = MediCloud()

# Initialize Multi-Authority infrastructure
cma = AttributeAuthority("CMA")
ha_a = AttributeAuthority("Hospital-A")
ha_b = AttributeAuthority("Hospital-B")
system.ma_manager.register_authority(cma)
system.ma_manager.register_authority(ha_a)
system.ma_manager.register_authority(ha_b)

# Shared master search key for demo
DEMO_SEARCH_KEY = hashlib_key = b"medicloud_demo_master_search_32"

# PRE Epoch Keys
sk_group_a, pk_group_a = system.pre_engine.generate_keypair()
sk_group_b, pk_group_b = system.pre_engine.generate_keypair()
current_pre_epoch = "Group-A (Pre-Revocation)"
active_pre_sk = sk_group_a

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MediCloud | Multi-Hospital Privacy Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-navy: #0D1B2A;
            --accent-blue: #0077B6;
            --accent-cyan: #00B4D8;
            --bg-light: #F8F9FA;
            --success-teal: #2A9D8F;
            --danger-coral: #E76F51;
        }
        body {
            background-color: var(--bg-light);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            color: #212529;
        }
        .navbar-custom {
            background: linear-gradient(135deg, var(--primary-navy) 0%, #1B263B 100%);
            border-bottom: 3px solid var(--accent-cyan);
        }
        .nav-pills .nav-link {
            color: #495057;
            font-weight: 600;
            border-radius: 8px;
            margin-right: 8px;
            padding: 10px 18px;
        }
        .nav-pills .nav-link.active {
            background-color: var(--accent-blue);
            color: #fff;
        }
        .card-custom {
            border: 1px solid #DEE2E6;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            background: #fff;
            margin-bottom: 24px;
        }
        .card-header-custom {
            background: #fff;
            border-bottom: 1px solid #E9ECEF;
            font-weight: 700;
            font-size: 1.1rem;
            color: var(--primary-navy);
            padding: 16px 20px;
            border-radius: 12px 12px 0 0 !important;
        }
        .code-block {
            background: #1E293B;
            color: #F8FAFC;
            padding: 14px;
            border-radius: 8px;
            font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
            font-size: 0.85rem;
            max-height: 280px;
            overflow-y: auto;
        }
        .badge-status {
            font-size: 0.9rem;
            padding: 6px 12px;
            border-radius: 6px;
        }
        .trust-meter {
            height: 24px;
            border-radius: 12px;
        }
    </style>
</head>
<body>

<!-- Navbar -->
<nav class="navbar navbar-dark navbar-custom px-4 py-3">
    <div class="container-fluid">
        <a class="navbar-brand d-flex align-items-center" href="#">
            <i class="fa-solid fa-shield-heart fa-2x me-3 text-info"></i>
            <div>
                <h4 class="mb-0 fw-bold">MediCloud SRE Dashboard</h4>
                <small class="text-light-50 opacity-75">Multi-Hospital Privacy-Preserving Cloud Data Sharing (IEEE Access 2019 / Sun)</small>
            </div>
        </a>
        <div class="text-end text-light">
            <span class="badge bg-info text-dark me-2"><i class="fa-solid fa-users"></i> Divyanshu | Adnan | Harshit</span>
            <span class="badge bg-secondary">IIIT Dharwad</span>
        </div>
    </div>
</nav>

<div class="container py-4">
    <!-- Navigation Tabs -->
    <ul class="nav nav-pills mb-4" id="pills-tab" role="tablist">
        <li class="nav-item">
            <button class="nav-link active" data-bs-toggle="pill" data-bs-target="#tab-search"><i class="fa-solid fa-magnifying-glass me-2"></i>Search & Access</button>
        </li>
        <li class="nav-item">
            <button class="nav-link" data-bs-toggle="pill" data-bs-target="#tab-upload"><i class="fa-solid fa-cloud-arrow-up me-2"></i>Upload Record</button>
        </li>
        <li class="nav-item">
            <button class="nav-link" data-bs-toggle="pill" data-bs-target="#tab-trust"><i class="fa-solid fa-gauge-high me-2"></i>Dynamic Trust Simulator</button>
        </li>
        <li class="nav-item">
            <button class="nav-link" data-bs-toggle="pill" data-bs-target="#tab-pre"><i class="fa-solid fa-arrows-rotate me-2"></i>Proxy Re-Encryption</button>
        </li>
        <li class="nav-item">
            <button class="nav-link" data-bs-toggle="pill" data-bs-target="#tab-cloud"><i class="fa-solid fa-database me-2"></i>Cloud Storage Inspector</button>
        </li>
    </ul>

    <div class="tab-content" id="pills-tabContent">
        <!-- TAB 1: Search & Access -->
        <div class="tab-pane fade show active" id="tab-search">
            <div class="row">
                <div class="col-md-6">
                    <div class="card card-custom">
                        <div class="card-header card-header-custom">
                            <i class="fa-solid fa-magnifying-glass text-primary me-2"></i>Phase 1: Searchable Symmetric Encryption (SSE)
                        </div>
                        <div class="card-body">
                            <p class="text-muted small">
                                Clinicians search by keyword (e.g. <code>cardiology</code>, <code>hypertension</code>). The client derives an HMAC-SHA256 blind trapdoor ($T_w$). The cloud server searches its inverted index <strong>without ever knowing the plain keyword</strong>.
                            </p>
                            <div class="input-group mb-3">
                                <input type="text" id="searchKeyword" class="form-control" placeholder="Enter keyword (e.g. cardiology)" value="cardiology">
                                <button class="btn btn-primary" onclick="executeSearch()"><i class="fa-solid fa-bolt me-1"></i>Search Cloud</button>
                            </div>
                            <div id="searchResultArea" class="d-none">
                                <div class="alert alert-info py-2">
                                    <small><strong>Generated Blind Trapdoor (Token):</strong></small>
                                    <div id="trapdoorOutput" class="small text-truncate font-monospace"></div>
                                </div>
                                <h6>Matching Encrypted Records Found:</h6>
                                <div id="matchingRecordsList" class="mb-3"></div>
                            </div>
                        </div>
                    </div>

                    <!-- Access & Decryption Form -->
                    <div class="card card-custom">
                        <div class="card-header card-header-custom">
                            <i class="fa-solid fa-key text-success me-2"></i>Phase 2: Attribute-Based Decryption
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label class="form-label small fw-bold">Select Record ID to Access:</label>
                                <input type="text" id="accessRecordId" class="form-control" value="ehr001">
                            </div>
                            <div class="mb-3">
                                <label class="form-label small fw-bold">Select Doctor Identity:</label>
                                <select id="doctorIdentity" class="form-select">
                                    <option value="doctor_a">Dr. Alice (Hospital-A, Cardiology) - Authorized</option>
                                    <option value="doctor_b">Dr. Bob (Hospital-B, Cardiology) - Cross-Hospital</option>
                                    <option value="cloud_op">Cloud Admin (No medical role) - Unauthorized</option>
                                </select>
                            </div>
                            <button class="btn btn-success w-100" onclick="attemptAccess()"><i class="fa-solid fa-lock-open me-2"></i>Verify Attributes & Decrypt Record</button>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card card-custom h-100">
                        <div class="card-header card-header-custom">
                            <i class="fa-solid fa-laptop-medical text-info me-2"></i>Decryption Outcome & Patient Plaintext
                        </div>
                        <div class="card-body">
                            <div id="accessStatusBadge" class="mb-3">
                                <span class="badge bg-secondary badge-status">Awaiting Access Request</span>
                            </div>
                            <h6>Result Details:</h6>
                            <div id="accessDetails" class="code-block mb-3">Submit access request on the left to view response.</div>
                            <h6>Decrypted Clinical EHR Payload:</h6>
                            <div id="plaintextView" class="code-block text-success">Plaintext will be displayed here only if authorized.</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: Upload Record -->
        <div class="tab-pane fade" id="tab-upload">
            <div class="card card-custom">
                <div class="card-header card-header-custom">
                    <i class="fa-solid fa-file-medical text-primary me-2"></i>Client-Side Encrypted Record Ingestion
                </div>
                <div class="card-body">
                    <p class="text-muted small">
                        Records are encrypted client-side using <strong>AES-256-GCM</strong> with <code>record_id</code> bound as Additional Authenticated Data (AAD).
                    </p>
                    <div class="row g-3">
                        <div class="col-md-4">
                            <label class="form-label fw-bold small">Record ID</label>
                            <input type="text" id="upRecordId" class="form-control" value="ehr003">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label fw-bold small">Patient ID</label>
                            <input type="text" id="upPatientId" class="form-control" value="P-789">
                        </div>
                        <div class="col-md-4">
                            <label class="form-label fw-bold small">Hospital</label>
                            <input type="text" id="upHospital" class="form-control" value="Hospital-A">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-bold small">Diagnosis</label>
                            <input type="text" id="upDiag" class="form-control" value="Type-2 Diabetes with Microvascular Complications">
                        </div>
                        <div class="col-md-6">
                            <label class="form-label fw-bold small">Search Keywords (Comma-separated)</label>
                            <input type="text" id="upKeywords" class="form-control" value="diabetes, endocrinology, hospital_a">
                        </div>
                        <div class="col-12">
                            <label class="form-label fw-bold small">Clinical Notes</label>
                            <textarea id="upNotes" class="form-control" rows="2">Patient responsive to Metformin 500mg BID. Scheduled for HbA1c review.</textarea>
                        </div>
                        <div class="col-12">
                            <button class="btn btn-primary" onclick="uploadRecord()"><i class="fa-solid fa-lock me-2"></i>Encrypt with AES-256-GCM & Store on Cloud</button>
                        </div>
                    </div>
                    <div id="uploadResult" class="mt-4 d-none">
                        <h6>Encrypted Cloud Package Generated:</h6>
                        <pre id="uploadOutput" class="code-block"></pre>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 3: Dynamic Trust Simulator -->
        <div class="tab-pane fade" id="tab-trust">
            <div class="card card-custom">
                <div class="card-header card-header-custom">
                    <i class="fa-solid fa-gauge-high text-warning me-2"></i>Phase 4: Behavioral Trust Telemetry & Automated Quarantine
                </div>
                <div class="card-body">
                    <p class="text-muted small">
                        Realizes Sun's 4 Trust Pillars: Initial baseline ($T_0=0.60$), Dynamic Updates ($+0.05$ / $-0.25$), Exponential Decay ($e^{-\lambda \Delta t}$), and Dual Gating ($T \ge 0.40$).
                    </p>
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Select Simulated Actor:</h6>
                            <select id="trustUser" class="form-select mb-3" onchange="refreshTrust()">
                                <option value="D-ALICE">Dr. Alice (Legitimate Clinician)</option>
                                <option value="D-MALICIOUS">Dr. Eve (Compromised / Rogue Credential)</option>
                            </select>
                            <h6>Current Trust Score:</h6>
                            <div class="progress trust-meter mb-2">
                                <div id="trustProgressBar" class="progress-bar bg-success progress-bar-striped" style="width: 60%">0.60</div>
                            </div>
                            <div class="d-flex justify-content-between small text-muted mb-4">
                                <span>0.0 (Quarantined)</span>
                                <span class="text-danger fw-bold">Threshold: 0.40</span>
                                <span>1.0 (Maximum)</span>
                            </div>

                            <h6>Trigger Behavioral Events:</h6>
                            <div class="d-grid gap-2">
                                <button class="btn btn-outline-success" onclick="triggerTrustEvent('SUCCESS')"><i class="fa-solid fa-check me-2"></i>Verified Clinical Query (+0.05)</button>
                                <button class="btn btn-outline-danger" onclick="triggerTrustEvent('POLICY_VIOLATION')"><i class="fa-solid fa-ban me-2"></i>Unauthorized Cross-Hospital Probe (-0.25)</button>
                                <button class="btn btn-outline-warning" onclick="triggerTrustEvent('EXPIRED_ACCESS')"><i class="fa-solid fa-clock me-2"></i>Expired Request Probe (-0.15)</button>
                            </div>
                        </div>

                        <div class="col-md-6">
                            <h6>Account Status & Gating:</h6>
                            <div id="quarantineAlert" class="alert alert-success">
                                <i class="fa-solid fa-circle-check me-2"></i><strong>Account Active:</strong> Trust score is sufficient ($\ge 0.40$). Access allowed with valid attributes.
                            </div>
                            <h6>Evaluation History / Telemetry:</h6>
                            <div id="trustHistory" class="code-block" style="height: 240px;">No events recorded yet.</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 4: Proxy Re-Encryption -->
        <div class="tab-pane fade" id="tab-pre">
            <div class="card card-custom">
                <div class="card-header card-header-custom">
                    <i class="fa-solid fa-arrows-rotate text-info me-2"></i>Phase 3: BBS98 Proxy Re-Encryption (PRE) Revocation
                </div>
                <div class="card-body">
                    <p class="text-muted small">
                        When medical staff depart, instead of re-downloading and re-encrypting gigabytes of data, the hospital sends an algebraic re-encryption key $rk_{A \to B} = sk_A^{-1} \cdot sk_B \pmod q$ to the semi-trusted cloud.
                    </p>
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Current Cryptographic Epoch:</h6>
                            <div class="alert alert-primary">
                                <strong id="preEpochLabel">Epoch: Group-A (Pre-Revocation)</strong>
                            </div>
                            <button class="btn btn-danger w-100 mb-3" onclick="triggerPreRevocation()"><i class="fa-solid fa-user-minus me-2"></i>Simulate Doctor Departure: Cloud Re-Encrypt</button>
                            <h6>Access Test Post-Departure:</h6>
                            <button class="btn btn-outline-secondary w-100 mb-2" onclick="testPreAccess('group_a')">Test Access as Departed Doctor (Key A)</button>
                            <button class="btn btn-outline-success w-100" onclick="testPreAccess('group_b')">Test Access as Active Doctor (Key B)</button>
                        </div>
                        <div class="col-md-6">
                            <h6>PRE Cryptographic Telemetry:</h6>
                            <div id="preLog" class="code-block" style="height: 260px;">Ready. Group-A key holds active encapsulation.</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 5: Cloud Storage Inspector -->
        <div class="tab-pane fade" id="tab-cloud">
            <div class="card card-custom">
                <div class="card-header card-header-custom">
                    <i class="fa-solid fa-eye-slash text-danger me-2"></i>Semi-Trusted Cloud Storage Inspector (Zero Plaintext Proof)
                </div>
                <div class="card-body">
                    <p class="text-muted small">
                        This view inspects the real files inside <code>cloud_storage/</code>. Notice that <strong>no patient names, diagnoses, or notes exist in plaintext</strong>.
                    </p>
                    <div class="row">
                        <div class="col-md-6">
                            <h6>Stored Encrypted Record (<code>cloud_storage/ehr001.json</code>):</h6>
                            <pre id="cloudRecordJson" class="code-block"></pre>
                        </div>
                        <div class="col-md-6">
                            <h6>Cloud Blind Search Index (<code>cloud_storage/cloud_search_index.json</code>):</h6>
                            <pre id="cloudIndexJson" class="code-block"></pre>
                        </div>
                    </div>
                    <button class="btn btn-outline-primary mt-3" onclick="refreshCloudView()"><i class="fa-solid fa-rotate me-2"></i>Refresh Cloud View</button>
                </div>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<script>
    // Search function
    function executeSearch() {
        const kw = document.getElementById('searchKeyword').value;
        fetch('/api/search?keyword=' + encodeURIComponent(kw))
            .then(r => r.json())
            .then(data => {
                document.getElementById('searchResultArea').classList.remove('d-none');
                document.getElementById('trapdoorOutput').innerText = data.trapdoor;
                const list = document.getElementById('matchingRecordsList');
                list.innerHTML = '';
                if (data.matches.length === 0) {
                    list.innerHTML = '<span class="text-danger small">No matching records found for this trapdoor.</span>';
                } else {
                    data.matches.forEach(m => {
                        list.innerHTML += `<button class="btn btn-sm btn-outline-primary me-2 mb-2" onclick="selectRecord('${m}')"><i class="fa-solid fa-file me-1"></i>${m}</button>`;
                    });
                }
            });
    }

    function selectRecord(id) {
        document.getElementById('accessRecordId').value = id;
    }

    // Access function
    function attemptAccess() {
        const recId = document.getElementById('accessRecordId').value;
        const identity = document.getElementById('doctorIdentity').value;

        fetch('/api/access', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({record_id: recId, identity: identity})
        })
        .then(r => r.json())
        .then(data => {
            const badge = document.getElementById('accessStatusBadge');
            const details = document.getElementById('accessDetails');
            const pt = document.getElementById('plaintextView');

            if (data.status === 'SUCCESS') {
                badge.innerHTML = '<span class="badge bg-success badge-status"><i class="fa-solid fa-circle-check me-1"></i>ACCESS GRANTED (200 OK)</span>';
                details.innerText = `[SUCCESS] Attributes verified against policy: ${JSON.stringify(data.attributes)}\nIntegrity Check: SHA-256 PASSED\nAEAD Tag: VALID`;
                pt.innerText = JSON.stringify(data.plaintext, null, 2);
                pt.className = 'code-block text-success';
            } else {
                badge.innerHTML = `<span class="badge bg-danger badge-status"><i class="fa-solid fa-circle-xmark me-1"></i>ACCESS DENIED: ${data.status}</span>`;
                details.innerText = `[REJECTED] Reason: ${data.status}\n${data.reason}\nUser Attributes: ${JSON.stringify(data.attributes)}`;
                pt.innerText = 'ACCESS_DENIED: Ciphertext was not decrypted.';
                pt.className = 'code-block text-danger';
            }
        });
    }

    // Upload function
    function uploadRecord() {
        const payload = {
            record_id: document.getElementById('upRecordId').value,
            patient_id: document.getElementById('upPatientId').value,
            hospital: document.getElementById('upHospital').value,
            diagnosis: document.getElementById('upDiag').value,
            keywords: document.getElementById('upKeywords').value.split(',').map(s => s.trim()),
            notes: document.getElementById('upNotes').value
        };

        fetch('/api/upload', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        })
        .then(r => r.json())
        .then(data => {
            document.getElementById('uploadResult').classList.remove('d-none');
            document.getElementById('uploadOutput').innerText = JSON.stringify(data.package, null, 2);
            refreshCloudView();
        });
    }

    // Trust functions
    function refreshTrust() {
        const user = document.getElementById('trustUser').value;
        fetch('/api/trust?user=' + encodeURIComponent(user))
            .then(r => r.json())
            .then(data => {
                const bar = document.getElementById('trustProgressBar');
                const pct = Math.round(data.score * 100);
                bar.style.width = pct + '%';
                bar.innerText = data.score.toFixed(2);
                
                const alert = document.getElementById('quarantineAlert');
                if (data.score < 0.40) {
                    bar.className = 'progress-bar bg-danger progress-bar-striped';
                    alert.className = 'alert alert-danger';
                    alert.innerHTML = '<i class="fa-solid fa-triangle-exclamation me-2"></i><strong>ACCOUNT QUARANTINED:</strong> Trust score < 0.40. All access requests will be blocked!';
                } else {
                    bar.className = 'progress-bar bg-success progress-bar-striped';
                    alert.className = 'alert alert-success';
                    alert.innerHTML = '<i class="fa-solid fa-circle-check me-2"></i><strong>Account Active:</strong> Trust score is sufficient ($\\\\ge 0.40$). Access allowed with valid attributes.';
                }
            });
    }

    function triggerTrustEvent(eventType) {
        const user = document.getElementById('trustUser').value;
        fetch('/api/trust_event', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({user: user, event: eventType})
        })
        .then(r => r.json())
        .then(data => {
            refreshTrust();
            const log = document.getElementById('trustHistory');
            log.innerText = `[${new Date().toLocaleTimeString()}] Event: ${eventType} -> Updated Trust: ${data.score.toFixed(2)}\\n` + log.innerText;
        });
    }

    // PRE functions
    function triggerPreRevocation() {
        fetch('/api/pre_reencrypt', {method: 'POST'})
            .then(r => r.json())
            .then(data => {
                document.getElementById('preEpochLabel').innerText = 'Epoch: Group-B (Post-Revocation)';
                const log = document.getElementById('preLog');
                log.innerText = `[${new Date().toLocaleTimeString()}] PRE Key rk_(A->B) generated: ${data.rk.substring(0, 32)}...\\n` +
                                `Cloud blindly re-encrypted ehr001 without knowing plaintext or secret keys.\\n` +
                                `Departed staff holding Key A are now locked out.\\n\\n` + log.innerText;
            });
    }

    function testPreAccess(keyType) {
        fetch('/api/pre_access?key_type=' + keyType)
            .then(r => r.json())
            .then(data => {
                const log = document.getElementById('preLog');
                log.innerText = `[${new Date().toLocaleTimeString()}] Attempt with ${keyType}: Outcome = ${data.status} (${data.message})\\n` + log.innerText;
            });
    }

    // Cloud inspector
    function refreshCloudView() {
        fetch('/api/cloud_inspector')
            .then(r => r.json())
            .then(data => {
                document.getElementById('cloudRecordJson').innerText = JSON.stringify(data.record, null, 2);
                document.getElementById('cloudIndexJson').innerText = JSON.stringify(data.index, null, 2);
            });
    }

    // Init
    window.onload = function() {
        refreshTrust();
        refreshCloudView();
    };
</script>
</body>
</html>
"""

# Store demo record keys in memory
record_keys = {}

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/search")
def api_search():
    kw = request.args.get("keyword", "cardiology")
    matches, trapdoor = system.search_records(kw, DEMO_SEARCH_KEY)
    return jsonify({"keyword": kw, "trapdoor": trapdoor, "matches": matches})

@app.route("/api/access", methods=["POST"])
def api_access():
    data = request.json or {}
    record_id = data.get("record_id", "ehr001")
    identity = data.get("identity", "doctor_a")

    if identity == "doctor_a":
        user = {"id": "D-ALICE", "attributes": ["doctor", "hospital_a", "cardiology"]}
    elif identity == "doctor_b":
        user = {"id": "D-BOB", "attributes": ["doctor", "hospital_b", "cardiology"]}
    else:
        user = {"id": "OP-01", "attributes": ["cloud_operator"]}

    # Check key
    key = record_keys.get(record_id)
    if not key and (system.storage / f"{record_id}.json").exists():
        # Fallback to key generated during upload
        key = record_keys.get("ehr001")

    res, status = system.access_record(record_id, user, key, evaluate_trust=True)
    reason = "Attributes match required policy." if status == "SUCCESS" else "Policy denied: missing required hospital or role attributes."
    return jsonify({
        "status": status,
        "reason": reason,
        "attributes": user["attributes"],
        "plaintext": res
    })

@app.route("/api/upload", methods=["POST"])
def api_upload():
    data = request.json or {}
    record_id = data.get("record_id", "ehr003")
    rec = {
        "patient_id": data.get("patient_id", "P-999"),
        "hospital": data.get("hospital", "Hospital-A"),
        "diagnosis": data.get("diagnosis", "Example diagnosis"),
        "notes": data.get("notes", "Synthetic data")
    }
    kws = data.get("keywords", ["cardiology"])
    key = system.upload_record(
        record_id=record_id,
        record=rec,
        required_attributes=["doctor", "hospital_a", "cardiology"],
        keywords=kws,
        search_key=DEMO_SEARCH_KEY,
        pre_pk=pk_group_a
    )
    record_keys[record_id] = key
    pkg = system.cloud_view(record_id)
    return jsonify({"status": "SUCCESS", "package": pkg})

@app.route("/api/trust")
def api_trust():
    user = request.args.get("user", "D-ALICE")
    score = system.trust_engine.get_score(user)
    return jsonify({"user": user, "score": score})

@app.route("/api/trust_event", methods=["POST"])
def api_trust_event():
    data = request.json or {}
    user = data.get("user", "D-ALICE")
    event = data.get("event", "SUCCESS")
    score = system.trust_engine.record_event(user, event)
    return jsonify({"user": user, "score": score})

@app.route("/api/pre_reencrypt", methods=["POST"])
def api_pre_reencrypt():
    global current_pre_epoch, active_pre_sk
    rk = system.pre_engine.generate_reencryption_key(sk_group_a, sk_group_b)
    system.cloud_reencrypt_record("ehr001", rk)
    current_pre_epoch = "Group-B (Post-Revocation)"
    active_pre_sk = sk_group_b
    return jsonify({"status": "SUCCESS", "rk": rk, "epoch": current_pre_epoch})

@app.route("/api/pre_access")
def api_pre_access():
    key_type = request.args.get("key_type", "group_a")
    doc = {"id": "D-ALICE", "attributes": ["doctor", "hospital_a", "cardiology"]}
    sk = sk_group_a if key_type == "group_a" else sk_group_b
    res, status = system.access_record_pre("ehr001", doc, sk)
    msg = "Access succeeded via valid PRE decapsulation." if status == "SUCCESS" else "Decapsulation failed: key belongs to departed/revoked epoch."
    return jsonify({"status": status, "message": msg})

@app.route("/api/cloud_inspector")
def api_cloud_inspector():
    rec = system.cloud_view("ehr001") if (system.storage / "ehr001.json").exists() else {}
    idx = system.search_index
    return jsonify({"record": rec, "index": idx})

if __name__ == "__main__":
    # Pre-seed ehr001
    sample_rec = {
        "patient_id": "P-001",
        "hospital": "Hospital-A",
        "diagnosis": "Cardiovascular Hypertension",
        "note": "Synthetic clinical demo record"
    }
    k1 = system.upload_record(
        "ehr001",
        sample_rec,
        ["doctor", "hospital_a", "cardiology"],
        keywords=["cardiology", "hypertension", "hospital_a"],
        search_key=DEMO_SEARCH_KEY,
        pre_pk=pk_group_a
    )
    record_keys["ehr001"] = k1

    print("\n" + "=" * 70)
    print("MediCloud Web Application starting on http://127.0.0.1:5000")
    print("=" * 70)
    app.run(host="127.0.0.1", port=5000, debug=False)
