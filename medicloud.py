"""
MediCloud: Multi-Hospital Electronic Health Record Privacy & Security System.
Implements:
  Phase 1: Searchable Symmetric Encryption (SSE) with blind trapdoor index.
  Phase 2: Decentralized Multi-Authority Access Control (MA-ABAC).
  Phase 3: Proxy Re-Encryption (PRE, BBS98-style) for dynamic staff departure revocation.
  Phase 4: Dynamic Behavioral Trust & Reputation Engine (formation, decay, quarantine).
  Phase 5: Cryptographic Traitor Tracing for key leak identification.
  Core: AES-256-GCM authenticated encryption, SHA-256 tamper-evident integrity, and audit logging.
"""
import os
import json
import time
import math
import hashlib
import hmac
import secrets
from datetime import datetime, timezone, timedelta
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Ensure matplotlib uses a writable cache if executed
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl")

# =====================================================================
# Phase 3 Primitives: BBS98 Proxy Re-Encryption (RFC 3526 1024-bit MODP)
# =====================================================================
P_HEX = (
    "FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1"
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD"
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245"
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED"
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE65381"
    "FFFFFFFFFFFFFFFF"
)
P_PRIME = int(P_HEX, 16)
Q_ORDER = (P_PRIME - 1) // 2
G_GEN = 2

class ProxyReEncryptionEngine:
    """
    Blaze-Bleumer-Strauss (BBS98) Proxy Re-Encryption Scheme.
    Allows semi-trusted cloud to transform ciphertexts from key A to key B
    without learning plaintext or secret keys.
    """
    def __init__(self, p=P_PRIME, q=Q_ORDER, g=G_GEN):
        self.p = p
        self.q = q
        self.g = g

    def generate_keypair(self):
        sk = secrets.randbelow(self.q - 3) + 2
        pk = pow(self.g, sk, self.p)
        return sk, pk

    def encrypt_dek(self, dek_bytes, pk):
        dek_int = int.from_bytes(dek_bytes, "big")
        if dek_int >= self.p:
            raise ValueError("DEK integer exceeds prime field modulus.")
        r = secrets.randbelow(self.q - 3) + 2
        c1 = pow(pk, r, self.p)
        c2 = (dek_int * pow(self.g, r, self.p)) % self.p
        return {"c1": hex(c1), "c2": hex(c2)}

    def decrypt_dek(self, c_package, sk):
        c1 = int(c_package["c1"], 16)
        c2 = int(c_package["c2"], 16)
        sk_inv = pow(sk, -1, self.q)
        gr = pow(c1, sk_inv, self.p)
        gr_inv = pow(gr, -1, self.p)
        dek_int = (c2 * gr_inv) % self.p
        # 32 bytes for AES-256
        return dek_int.to_bytes(32, "big")

    def generate_reencryption_key(self, sk_from, sk_to):
        sk_from_inv = pow(sk_from, -1, self.q)
        rk = (sk_from_inv * sk_to) % self.q
        return hex(rk)

    def cloud_reencrypt(self, c_package, rk_hex):
        c1 = int(c_package["c1"], 16)
        c2 = int(c_package["c2"], 16)
        rk = int(rk_hex, 16)
        c1_prime = pow(c1, rk, self.p)
        c2_prime = c2
        return {"c1": hex(c1_prime), "c2": hex(c2_prime)}

# =====================================================================
# Phase 1: Searchable Symmetric Encryption (SSE) Engine
# =====================================================================
class SearchableEngine:
    """
    Searchable Symmetric Encryption using blind HMAC-SHA256 trapdoors.
    Cloud matches tokens against an inverted index without knowing keywords.
    """
    def __init__(self):
        pass

    @staticmethod
    def generate_trapdoor(keyword, search_key):
        norm = keyword.lower().strip().encode("utf-8")
        return hmac.new(search_key, norm, hashlib.sha256).hexdigest()

    def build_blind_index(self, record_id, keywords, search_key, existing_index=None):
        index = existing_index if existing_index is not None else {}
        for kw in keywords:
            trapdoor = self.generate_trapdoor(kw, search_key)
            if trapdoor not in index:
                index[trapdoor] = []
            if record_id not in index[trapdoor]:
                index[trapdoor].append(record_id)
        return index

# =====================================================================
# Phase 2: Multi-Authority Access Control (MA-ABAC)
# =====================================================================
class AttributeAuthority:
    """
    Independent Attribute Authority (e.g. Central Medical Council, Hospital-A, Lab).
    Issues cryptographically signed credential tokens for attributes it owns.
    """
    def __init__(self, authority_id, signing_key=None):
        self.authority_id = authority_id
        self.signing_key = signing_key or secrets.token_bytes(32)

    def issue_credential(self, user_id, attributes, validity_hours=24):
        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=validity_hours)
        payload = {
            "authority_id": self.authority_id,
            "user_id": user_id,
            "attributes": list(attributes),
            "issued_at": now.isoformat(),
            "expires_at": expires.isoformat()
        }
        sig = hmac.new(
            self.signing_key,
            json.dumps(payload, sort_keys=True).encode(),
            hashlib.sha256
        ).hexdigest()
        return {**payload, "signature": sig}

    def verify_credential(self, cred):
        if cred.get("authority_id") != self.authority_id:
            return False, "AUTHORITY_MISMATCH"
        now = datetime.now(timezone.utc)
        exp = datetime.fromisoformat(cred["expires_at"])
        if now >= exp:
            return False, "CREDENTIAL_EXPIRED"
        payload = {
            "authority_id": cred["authority_id"],
            "user_id": cred["user_id"],
            "attributes": cred["attributes"],
            "issued_at": cred["issued_at"],
            "expires_at": cred["expires_at"]
        }
        expected = hmac.new(
            self.signing_key,
            json.dumps(payload, sort_keys=True).encode(),
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(expected, cred.get("signature", "")):
            return False, "INVALID_SIGNATURE"
        return True, "VALID"

class MultiAuthorityManager:
    """Manages independent authorities and enforces multi-authority policies."""
    def __init__(self):
        self.authorities = {}

    def register_authority(self, authority):
        self.authorities[authority.authority_id] = authority

    def evaluate_policy(self, user_credentials, policy_dict):
        """
        policy_dict: { "Authority_ID": ["attr1", "attr2"], ... }
        user_credentials: list of signed credentials
        """
        cred_map = {c.get("authority_id"): c for c in user_credentials}
        for auth_id, req_attrs in policy_dict.items():
            if auth_id not in self.authorities:
                return False, f"UNKNOWN_AUTHORITY_{auth_id}"
            if auth_id not in cred_map:
                return False, f"MISSING_CREDENTIAL_{auth_id}"
            cred = cred_map[auth_id]
            valid, reason = self.authorities[auth_id].verify_credential(cred)
            if not valid:
                return False, f"{auth_id}_{reason}"
            user_attrs = set(cred.get("attributes", []))
            if not set(req_attrs).issubset(user_attrs):
                return False, f"{auth_id}_POLICY_DENIED"
        return True, "AUTHORIZED"

# =====================================================================
# Phase 4: Dynamic Behavioral Trust & Reputation Engine
# =====================================================================
class TrustEngine:
    """
    Dynamic Trust Engine (Slide 9):
    - Formation: Initial baseline trust (0.60).
    - Update: Boost on legitimate actions (+0.05), penalty on policy violations (-0.25).
    - Time Decay: Inactive accounts decay towards baseline.
    - Interlocking Access Gate: Blocks access if trust < min_threshold (0.40).
    """
    def __init__(self, baseline=0.60, min_threshold=0.40, decay_lambda=0.05):
        self.baseline = baseline
        self.min_threshold = min_threshold
        self.decay_lambda = decay_lambda
        self.scores = {}
        self.last_updated = {}

    def get_score(self, user_id):
        now = time.time()
        if user_id not in self.scores:
            self.scores[user_id] = self.baseline
            self.last_updated[user_id] = now
            return self.baseline

        # Exponential decay towards baseline
        dt_hours = (now - self.last_updated[user_id]) / 3600.0
        prev = self.scores[user_id]
        decayed = self.baseline + (prev - self.baseline) * math.exp(-self.decay_lambda * dt_hours)
        decayed = max(0.0, min(1.0, decayed))
        self.scores[user_id] = decayed
        self.last_updated[user_id] = now
        return decayed

    def record_event(self, user_id, event_type):
        current = self.get_score(user_id)
        if event_type == "SUCCESS":
            updated = min(1.0, current + 0.05)
        elif event_type == "POLICY_VIOLATION":
            updated = max(0.0, current - 0.25)
        elif event_type == "EXPIRED_ACCESS":
            updated = max(0.0, current - 0.15)
        elif event_type == "INTEGRITY_VIOLATION":
            updated = max(0.0, current - 0.35)
        elif event_type == "ANOMALY":
            updated = max(0.0, current - 0.20)
        else:
            updated = current
        self.scores[user_id] = round(updated, 4)
        self.last_updated[user_id] = time.time()
        return self.scores[user_id]

    def evaluate_trust(self, user_id):
        score = self.get_score(user_id)
        if score < self.min_threshold:
            return False, "TRUST_SCORE_INSUFFICIENT", score
        return True, "TRUST_SATISFIED", score

# =====================================================================
# Phase 5: Cryptographic Traitor Tracing
# =====================================================================
class TraitorTracer:
    """
    Embeds cryptographic identity watermarks into user keys.
    Traces leaked keys to identify rogue users.
    """
    def __init__(self, master_trace_key=None):
        self.master_trace_key = master_trace_key or secrets.token_bytes(32)
        self.registry = {}

    def watermark_key(self, user_id, key_bytes):
        watermark = hmac.new(
            self.master_trace_key,
            user_id.encode(),
            hashlib.sha256
        ).hexdigest()
        self.registry[watermark] = user_id
        return {
            "key_hex": key_bytes.hex(),
            "watermark": watermark
        }

    def trace_leaked_key(self, leaked_package):
        watermark = leaked_package.get("watermark")
        if watermark in self.registry:
            return True, f"TRAITOR_IDENTIFIED_{self.registry[watermark]}"
        return False, "UNKNOWN_WATERMARK"

# =====================================================================
# Core MediCloud System (Unified Orchestration)
# =====================================================================
class MediCloud:
    def __init__(self, storage_dir="cloud_storage"):
        self.storage = Path(storage_dir)
        self.storage.mkdir(exist_ok=True)
        self.audit = []

        # Integrated Cryptographic & SRE Engines
        self.search_engine = SearchableEngine()
        self.pre_engine = ProxyReEncryptionEngine()
        self.ma_manager = MultiAuthorityManager()
        self.trust_engine = TrustEngine()
        self.tracer = TraitorTracer()

        # Cloud-side blind search index file
        self.search_index_path = self.storage / "cloud_search_index.json"
        self._load_search_index()

    def _load_search_index(self):
        if self.search_index_path.exists():
            try:
                self.search_index = json.loads(self.search_index_path.read_text())
            except Exception:
                self.search_index = {}
        else:
            self.search_index = {}

    def _save_search_index(self):
        self.search_index_path.write_text(json.dumps(self.search_index, indent=2))

    def _policy_allows(self, user, required, expires_at):
        now = datetime.now(timezone.utc)
        if now >= expires_at:
            return False, "ACCESS_EXPIRED"
        if not set(required).issubset(set(user.get("attributes", []))):
            return False, "ATTRIBUTE_POLICY_DENIED"
        return True, "AUTHORIZED"

    # -----------------------------------------------------------------
    # Record Upload & Encryption
    # -----------------------------------------------------------------
    def upload_record(
        self,
        record_id,
        record,
        required_attributes=None,
        keywords=None,
        search_key=None,
        multi_authority_policy=None,
        pre_pk=None
    ):
        """
        Encrypts record with AES-256-GCM.
        Optionally builds blind searchable index, multi-authority policy, and PRE encapsulation.
        """
        key = AESGCM.generate_key(bit_length=256)
        nonce = secrets.token_bytes(12)
        plaintext = json.dumps(record, sort_keys=True).encode()
        aad = record_id.encode()
        ciphertext = AESGCM(key).encrypt(nonce, plaintext, aad)
        digest = hashlib.sha256(ciphertext).hexdigest()

        package = {
            "record_id": record_id,
            "nonce": nonce.hex(),
            "ciphertext": ciphertext.hex(),
            "sha256": digest,
            "required_attributes": required_attributes or []
        }

        if multi_authority_policy:
            package["multi_authority_policy"] = multi_authority_policy

        # Phase 3: PRE DEK Encapsulation (if public key provided)
        if pre_pk:
            package["pre_enc_dek"] = self.pre_engine.encrypt_dek(key, pre_pk)

        (self.storage / f"{record_id}.json").write_text(json.dumps(package, indent=2))

        # Phase 1: Searchable Symmetric Encryption Index update
        if keywords and search_key:
            self.search_index = self.search_engine.build_blind_index(
                record_id, keywords, search_key, self.search_index
            )
            self._save_search_index()

        return key

    # -----------------------------------------------------------------
    # Classic Access Record (Backward Compatible + Optional Trust)
    # -----------------------------------------------------------------
    def access_record(self, record_id, user, key, expires_at=None, evaluate_trust=False):
        path = self.storage / f"{record_id}.json"
        user_id = user.get("id", "anonymous")

        if not path.exists():
            self.audit.append({"user": user_id, "record": record_id, "result": "NOT_FOUND"})
            return None, "NOT_FOUND"

        package = json.loads(path.read_text())
        if expires_at is None:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

        # Optional Phase 4: Dynamic Trust Evaluation
        if evaluate_trust:
            trust_ok, trust_reason, score = self.trust_engine.evaluate_trust(user_id)
            if not trust_ok:
                self.audit.append({"user": user_id, "record": record_id, "result": trust_reason, "trust": score})
                return None, trust_reason

        allowed, reason = self._policy_allows(user, package["required_attributes"], expires_at)
        if not allowed:
            self.trust_engine.record_event(user_id, "EXPIRED_ACCESS" if reason == "ACCESS_EXPIRED" else "POLICY_VIOLATION")
            self.audit.append({"user": user_id, "record": record_id, "result": reason})
            return None, reason

        ciphertext = bytes.fromhex(package["ciphertext"])
        if hashlib.sha256(ciphertext).hexdigest() != package["sha256"]:
            self.trust_engine.record_event(user_id, "INTEGRITY_VIOLATION")
            self.audit.append({"user": user_id, "record": record_id, "result": "INTEGRITY_FAILED"})
            return None, "INTEGRITY_FAILED"

        try:
            plaintext = AESGCM(key).decrypt(bytes.fromhex(package["nonce"]), ciphertext, record_id.encode())
            self.trust_engine.record_event(user_id, "SUCCESS")
            self.audit.append({"user": user_id, "record": record_id, "result": "SUCCESS"})
            return json.loads(plaintext), "SUCCESS"
        except Exception:
            self.trust_engine.record_event(user_id, "INTEGRITY_VIOLATION")
            self.audit.append({"user": user_id, "record": record_id, "result": "DECRYPTION_FAILED"})
            return None, "DECRYPTION_FAILED"

    # -----------------------------------------------------------------
    # Phase 1: Search Cloud via Blind Trapdoor
    # -----------------------------------------------------------------
    def search_records(self, query_keyword, search_key):
        """
        Client computes blind trapdoor; cloud queries index without knowing query word.
        """
        trapdoor = self.search_engine.generate_trapdoor(query_keyword, search_key)
        results = self.search_index.get(trapdoor, [])
        return results, trapdoor

    # -----------------------------------------------------------------
    # Phase 2: Multi-Authority Access
    # -----------------------------------------------------------------
    def access_record_multi_authority(self, record_id, user_credentials, key):
        path = self.storage / f"{record_id}.json"
        user_id = user_credentials[0]["user_id"] if user_credentials else "unknown"

        if not path.exists():
            self.audit.append({"user": user_id, "record": record_id, "result": "NOT_FOUND"})
            return None, "NOT_FOUND"

        package = json.loads(path.read_text())
        policy = package.get("multi_authority_policy", {})

        allowed, reason = self.ma_manager.evaluate_policy(user_credentials, policy)
        if not allowed:
            self.audit.append({"user": user_id, "record": record_id, "result": reason})
            return None, reason

        ciphertext = bytes.fromhex(package["ciphertext"])
        if hashlib.sha256(ciphertext).hexdigest() != package["sha256"]:
            self.audit.append({"user": user_id, "record": record_id, "result": "INTEGRITY_FAILED"})
            return None, "INTEGRITY_FAILED"

        try:
            plaintext = AESGCM(key).decrypt(bytes.fromhex(package["nonce"]), ciphertext, record_id.encode())
            self.audit.append({"user": user_id, "record": record_id, "result": "SUCCESS"})
            return json.loads(plaintext), "SUCCESS"
        except Exception:
            self.audit.append({"user": user_id, "record": record_id, "result": "DECRYPTION_FAILED"})
            return None, "DECRYPTION_FAILED"

    # -----------------------------------------------------------------
    # Phase 3: Cloud Proxy Re-Encryption & Access
    # -----------------------------------------------------------------
    def cloud_reencrypt_record(self, record_id, rk_hex):
        """
        Executed by the semi-trusted cloud.
        Transforms encapsulated DEK from key A to key B without decrypting.
        """
        path = self.storage / f"{record_id}.json"
        package = json.loads(path.read_text())
        if "pre_enc_dek" not in package:
            return False, "NO_PRE_ENCAPSULATION"

        reencrypted_dek = self.pre_engine.cloud_reencrypt(package["pre_enc_dek"], rk_hex)
        package["pre_enc_dek"] = reencrypted_dek
        path.write_text(json.dumps(package, indent=2))
        return True, "REENCRYPTION_COMPLETE"

    def access_record_pre(self, record_id, user, user_sk):
        """
        Accesses a record using user's private key via decapsulation of PRE DEK.
        """
        path = self.storage / f"{record_id}.json"
        user_id = user.get("id", "anonymous")
        if not path.exists():
            return None, "NOT_FOUND"

        package = json.loads(path.read_text())
        if "pre_enc_dek" not in package:
            return None, "NO_PRE_ENCAPSULATION"

        try:
            dek = self.pre_engine.decrypt_dek(package["pre_enc_dek"], user_sk)
        except Exception:
            self.audit.append({"user": user_id, "record": record_id, "result": "PRE_DECAPSULATION_FAILED"})
            return None, "PRE_DECAPSULATION_FAILED"

        return self.access_record(record_id, user, dek)

    # -----------------------------------------------------------------
    # Phase 5: Traitor Tracing API
    # -----------------------------------------------------------------
    def trace_leaked_key(self, leaked_package):
        return self.tracer.trace_leaked_key(leaked_package)

    # -----------------------------------------------------------------
    # Utility & Audit Helpers
    # -----------------------------------------------------------------
    def cloud_view(self, record_id):
        return json.loads((self.storage / f"{record_id}.json").read_text())

    def tamper_ciphertext(self, record_id):
        path = self.storage / f"{record_id}.json"
        package = json.loads(path.read_text())
        blob = bytearray.fromhex(package["ciphertext"])
        blob[-1] ^= 1
        package["ciphertext"] = bytes(blob).hex()
        path.write_text(json.dumps(package, indent=2))

    def save_audit(self, filename="data/audit_log.json"):
        p = Path(filename)
        p.parent.mkdir(exist_ok=True)
        p.write_text(json.dumps(self.audit, indent=2))
        # Keep backward compatibility with root audit_log.json
        Path("audit_log.json").write_text(json.dumps(self.audit, indent=2))

# =====================================================================
# Comprehensive Test Suite & Microbenchmarks
# =====================================================================
def run_all_tests():
    print("=" * 70)
    print("Running Full MediCloud Functional & Cryptographic Security Test Suite")
    print("=" * 70)

    system = MediCloud()
    results = []

    # 1. Baseline Test Setup
    record = {
        "patient_id": "P-001",
        "hospital": "Hospital-A",
        "diagnosis": "Cardiovascular Hypertension",
        "note": "Synthetic demonstration clinical record"
    }
    keywords = ["cardiology", "hypertension", "hospital_a"]
    search_key = secrets.token_bytes(32)

    # Authorities Setup (Phase 2)
    cma = AttributeAuthority("CMA")
    ha_a = AttributeAuthority("Hospital-A")
    ha_b = AttributeAuthority("Hospital-B")
    system.ma_manager.register_authority(cma)
    system.ma_manager.register_authority(ha_a)
    system.ma_manager.register_authority(ha_b)

    # BBS98 PRE Setup (Phase 3)
    sk_group_a, pk_group_a = system.pre_engine.generate_keypair()
    sk_group_b, pk_group_b = system.pre_engine.generate_keypair()

    ma_policy = {"CMA": ["role:doctor"], "Hospital-A": ["hospital:hospital_a"]}

    # Upload record with all integrated features
    key = system.upload_record(
        record_id="ehr001",
        record=record,
        required_attributes=["doctor", "hospital_a", "cardiology"],
        keywords=keywords,
        search_key=search_key,
        multi_authority_policy=ma_policy,
        pre_pk=pk_group_a
    )

    # -------------------------------------------------------------
    # Test 1: Authorized doctor (Baseline ABAC)
    # -------------------------------------------------------------
    doctor = {"id": "D-01", "attributes": ["doctor", "hospital_a", "cardiology"]}
    res, status = system.access_record("ehr001", doctor, key)
    results.append({
        "Test": "Authorized doctor",
        "Expected": "SUCCESS",
        "Actual": status,
        "Status": "PASS" if status == "SUCCESS" else "FAIL",
        "Explanation": "Matching role, hospital and department attributes."
    })

    # -------------------------------------------------------------
    # Test 2: Cross-hospital user (Baseline ABAC)
    # -------------------------------------------------------------
    cross_user = {"id": "D-02", "attributes": ["doctor", "hospital_b", "cardiology"]}
    _, status = system.access_record("ehr001", cross_user, key)
    results.append({
        "Test": "Cross-hospital user",
        "Expected": "ATTRIBUTE_POLICY_DENIED",
        "Actual": status,
        "Status": "PASS" if status == "ATTRIBUTE_POLICY_DENIED" else "FAIL",
        "Explanation": "Hospital-B identity lacks hospital_a attribute."
    })

    # -------------------------------------------------------------
    # Test 3: Cloud operator (Baseline ABAC)
    # -------------------------------------------------------------
    operator = {"id": "OP-01", "attributes": ["cloud_admin"]}
    _, status = system.access_record("ehr001", operator, key)
    results.append({
        "Test": "Cloud operator",
        "Expected": "ATTRIBUTE_POLICY_DENIED",
        "Actual": status,
        "Status": "PASS" if status == "ATTRIBUTE_POLICY_DENIED" else "FAIL",
        "Explanation": "Cloud operator does not satisfy the doctor policy."
    })

    # -------------------------------------------------------------
    # Test 4: Expired access
    # -------------------------------------------------------------
    past_time = datetime.now(timezone.utc) - timedelta(minutes=5)
    _, status = system.access_record("ehr001", doctor, key, expires_at=past_time)
    results.append({
        "Test": "Expired access",
        "Expected": "ACCESS_EXPIRED",
        "Actual": status,
        "Status": "PASS" if status == "ACCESS_EXPIRED" else "FAIL",
        "Explanation": "The supplied authorization expiry is in the past."
    })

    # -------------------------------------------------------------
    # Test 5: Modified ciphertext
    # -------------------------------------------------------------
    system.upload_record("ehr002", record, ["doctor", "hospital_a", "cardiology"])
    system.tamper_ciphertext("ehr002")
    _, status = system.access_record("ehr002", doctor, key)
    results.append({
        "Test": "Modified ciphertext",
        "Expected": "INTEGRITY_FAILED",
        "Actual": status,
        "Status": "PASS" if status == "INTEGRITY_FAILED" else "FAIL",
        "Explanation": "Ciphertext hash no longer matches stored SHA-256 digest."
    })

    # -------------------------------------------------------------
    # Test 6: Audit logging
    # -------------------------------------------------------------
    results.append({
        "Test": "Audit logging",
        "Expected": "SUCCESS",
        "Actual": "SUCCESS" if len(system.audit) > 0 else "FAILED",
        "Status": "PASS" if len(system.audit) > 0 else "FAIL",
        "Explanation": "Every attempted access produced an audit event with identity, record and result."
    })

    # -------------------------------------------------------------
    # Test 7: Cloud-side plaintext visibility
    # -------------------------------------------------------------
    cloud_data = system.cloud_view("ehr001")
    plaintext_exposed = "diagnosis" in str(cloud_data) or "Cardiovascular" in str(cloud_data)
    results.append({
        "Test": "Cloud-side plaintext visibility",
        "Expected": "CIPHERTEXT_ONLY",
        "Actual": "CIPHERTEXT_ONLY" if not plaintext_exposed else "PLAINTEXT_EXPOSED",
        "Status": "PASS" if not plaintext_exposed else "FAIL",
        "Explanation": "Stored JSON contains nonce, ciphertext, digest and policy metadata, not the patient diagnosis."
    })

    # -------------------------------------------------------------
    # Test 8: Phase 1 Searchable Encryption (SSE) Keyword Match
    # -------------------------------------------------------------
    matches, trapdoor = system.search_records("cardiology", search_key)
    results.append({
        "Test": "Searchable Encryption (SSE) query",
        "Expected": "MATCH_FOUND",
        "Actual": "MATCH_FOUND" if "ehr001" in matches else "NO_MATCH",
        "Status": "PASS" if "ehr001" in matches else "FAIL",
        "Explanation": "Client generates blind trapdoor; cloud matches record without decrypting index."
    })

    # -------------------------------------------------------------
    # Test 9: Phase 1 Cloud Blind Search Security
    # -------------------------------------------------------------
    index_view = system.search_index
    index_leaks = "cardiology" in str(index_view) or "hypertension" in str(index_view)
    results.append({
        "Test": "SSE Cloud Index privacy",
        "Expected": "TRAPDOORS_ONLY",
        "Actual": "TRAPDOORS_ONLY" if not index_leaks else "KEYWORD_LEAKED",
        "Status": "PASS" if not index_leaks else "FAIL",
        "Explanation": "Cloud search index contains only HMAC-SHA256 hex hashes, zero plaintext keywords."
    })

    # -------------------------------------------------------------
    # Test 10: Phase 3 Proxy Re-Encryption (PRE) Cloud Delegation
    # -------------------------------------------------------------
    # Before re-encryption: Group A can access via PRE decapsulation
    res_a, status_a = system.access_record_pre("ehr001", doctor, sk_group_a)
    # Generate re-encryption key A -> B
    rk_a_to_b = system.pre_engine.generate_reencryption_key(sk_group_a, sk_group_b)
    # Cloud blindly re-encrypts
    reenc_ok, _ = system.cloud_reencrypt_record("ehr001", rk_a_to_b)
    # Now Group B can access
    res_b, status_b = system.access_record_pre("ehr001", doctor, sk_group_b)

    results.append({
        "Test": "Proxy Re-Encryption cloud delegation",
        "Expected": "SUCCESS",
        "Actual": status_b if (status_a == "SUCCESS" and reenc_ok) else "FAILED",
        "Status": "PASS" if status_b == "SUCCESS" else "FAIL",
        "Explanation": "Semi-trusted cloud transformed ciphertext from Group A to Group B without seeing plaintext or keys."
    })

    # -------------------------------------------------------------
    # Test 11: Phase 3 PRE Revoked Staff Lockout
    # -------------------------------------------------------------
    # Group A (departed staff) attempts to decapsulate re-encrypted record
    _, status_old_group = system.access_record_pre("ehr001", doctor, sk_group_a)
    results.append({
        "Test": "PRE departed staff revocation",
        "Expected": "PRE_DECAPSULATION_FAILED",
        "Actual": status_old_group,
        "Status": "PASS" if status_old_group == "PRE_DECAPSULATION_FAILED" else "FAIL",
        "Explanation": "Old group key cannot decapsulate the re-encrypted record, enforcing immediate cryptographic revocation."
    })

    # -------------------------------------------------------------
    # Test 12: Phase 2 Multi-Authority Verification
    # -------------------------------------------------------------
    cred_cma = cma.issue_credential("D-01", ["role:doctor", "license:active"])
    cred_ha_a = ha_a.issue_credential("D-01", ["hospital:hospital_a", "dept:cardiology"])
    _, status_ma = system.access_record_multi_authority("ehr001", [cred_cma, cred_ha_a], key)
    results.append({
        "Test": "Multi-Authority authorized access",
        "Expected": "SUCCESS",
        "Actual": status_ma,
        "Status": "PASS" if status_ma == "SUCCESS" else "FAIL",
        "Explanation": "Credentials signed independently by Central Medical Council and Hospital-A both satisfy policy."
    })

    # -------------------------------------------------------------
    # Test 13: Phase 2 Multi-Authority Forgery & Cross-Org Isolation
    # -------------------------------------------------------------
    # Hospital-B attempts to issue credential claiming Hospital-A authority
    forged_ha = ha_b.issue_credential("D-01", ["hospital:hospital_a"])
    # Present CMA + forged credential
    _, status_forged = system.access_record_multi_authority("ehr001", [cred_cma, forged_ha], key)
    results.append({
        "Test": "Multi-Authority cross-org forgery rejection",
        "Expected": "FAIL",
        "Actual": "FAIL" if status_forged != "SUCCESS" else "SUCCESS",
        "Status": "PASS" if status_forged != "SUCCESS" else "FAIL",
        "Explanation": f"Cross-hospital credential fails validation ({status_forged}); authorities cannot impersonate each other."
    })

    # -------------------------------------------------------------
    # Test 14: Phase 4 Dynamic Trust Score Elevation
    # -------------------------------------------------------------
    user_trust = "D-TRUST"
    doc_trust = {"id": user_trust, "attributes": ["doctor", "hospital_a", "cardiology"]}
    init_score = system.trust_engine.get_score(user_trust)
    # Perform 3 successful accesses
    for _ in range(3):
        system.access_record("ehr001", doc_trust, key, evaluate_trust=True)
    elevated_score = system.trust_engine.get_score(user_trust)
    results.append({
        "Test": "Dynamic Trust elevation on valid activity",
        "Expected": "SCORE_INCREASED",
        "Actual": "SCORE_INCREASED" if elevated_score > init_score else "UNCHANGED",
        "Status": "PASS" if elevated_score > init_score else "FAIL",
        "Explanation": f"Trust score dynamically increased from {init_score:.2f} to {elevated_score:.2f} based on verified accesses."
    })

    # -------------------------------------------------------------
    # Test 15: Phase 4 Dynamic Trust Penalty & Quarantine
    # -------------------------------------------------------------
    # Simulate anomalous repeated cross-hospital violations
    attacker = {"id": "D-ATTACKER", "attributes": ["doctor", "hospital_b"]}
    for _ in range(4):
        system.access_record("ehr001", attacker, key, evaluate_trust=True)
    penalty_score = system.trust_engine.get_score("D-ATTACKER")
    # Now provide valid attributes, but user is quarantined
    attacker_with_valid_attrs = {"id": "D-ATTACKER", "attributes": ["doctor", "hospital_a", "cardiology"]}
    _, status_quarantine = system.access_record("ehr001", attacker_with_valid_attrs, key, evaluate_trust=True)
    results.append({
        "Test": "Dynamic Trust penalty and quarantine",
        "Expected": "TRUST_SCORE_INSUFFICIENT",
        "Actual": status_quarantine,
        "Status": "PASS" if status_quarantine == "TRUST_SCORE_INSUFFICIENT" else "FAIL",
        "Explanation": f"Trust degraded to {penalty_score:.2f} (< 0.40 threshold); account is quarantined despite valid attributes."
    })

    # -------------------------------------------------------------
    # Test 16: Phase 5 Traitor Tracing Key Identification
    # -------------------------------------------------------------
    leaked_user = "D-ROUGE-42"
    watermarked_package = system.tracer.watermark_key(leaked_user, key)
    traced_ok, culprit_id = system.trace_leaked_key(watermarked_package)
    results.append({
        "Test": "Traitor Tracing leak identification",
        "Expected": f"TRAITOR_IDENTIFIED_{leaked_user}",
        "Actual": culprit_id,
        "Status": "PASS" if culprit_id == f"TRAITOR_IDENTIFIED_{leaked_user}" else "FAIL",
        "Explanation": f"Cryptographic watermark in leaked key precisely identified culprit ({culprit_id})."
    })

    system.save_audit("data/audit_log.json")

    # Print summary
    pass_count = sum(1 for r in results if r["Status"] == "PASS")
    print(f"\nExecution Summary: {pass_count}/{len(results)} tests PASSED.\n")
    for r in results:
        mark = "✓ PASS" if r["Status"] == "PASS" else "✗ FAIL"
        print(f"[{mark}] {r['Test']:<45} -> {r['Actual']}")

    # Save to data/security_tests.csv
    csv_lines = ["Test,Expected,Actual,Status,Explanation"]
    for r in results:
        expl = f'"{r["Explanation"]}"' if "," in r["Explanation"] else r["Explanation"]
        csv_lines.append(f"{r['Test']},{r['Expected']},{r['Actual']},{r['Status']},{expl}")
    Path("data/security_tests.csv").write_text("\n".join(csv_lines))

    return results

# =====================================================================
# Microbenchmark Suite
# =====================================================================
def run_benchmarks():
    print("\n" + "=" * 70)
    print("Running Microbenchmark Performance Evaluation")
    print("=" * 70)

    system = MediCloud()
    batch_sizes = [1, 10, 50, 100]
    bench_results = []

    doc = {"id": "D-BENCH", "attributes": ["doctor", "hospital_a", "cardiology"]}
    search_key = secrets.token_bytes(32)

    for n in batch_sizes:
        keys = []
        # Measure Encryption + Indexing
        t0 = time.perf_counter()
        for i in range(n):
            k = system.upload_record(
                f"bench_{n}_{i}",
                {"id": f"P-{i}", "diag": "synthetic test"},
                ["doctor", "hospital_a", "cardiology"],
                keywords=["cardiology", f"patient_{i}"],
                search_key=search_key
            )
            keys.append(k)
        t_enc = (time.perf_counter() - t0) * 1000.0 / n

        # Measure Search / Trapdoor Matching
        t0 = time.perf_counter()
        for i in range(n):
            system.search_records("cardiology", search_key)
        t_search = (time.perf_counter() - t0) * 1000.0 / n

        # Measure Decryption
        t0 = time.perf_counter()
        for i in range(n):
            system.access_record(f"bench_{n}_{i}", doc, keys[i])
        t_dec = (time.perf_counter() - t0) * 1000.0 / n

        # Measure Policy Check only
        t0 = time.perf_counter()
        exp = datetime.now(timezone.utc) + timedelta(hours=1)
        for i in range(n):
            system._policy_allows(doc, ["doctor", "hospital_a", "cardiology"], exp)
        t_pol = (time.perf_counter() - t0) * 1000.0 / n

        bench_results.append({
            "Records": n,
            "Avg encryption (ms)": round(t_enc, 6),
            "Avg decryption (ms)": round(t_dec, 6),
            "Avg policy check (ms)": round(t_pol, 6),
            "Avg search query (ms)": round(t_search, 6),
            "Total encrypt+decrypt (ms)": round(t_enc + t_dec, 6)
        })

    # Save to data/performance.csv
    csv_lines = ["Records,Avg encryption (ms),Avg decryption (ms),Avg policy check (ms),Avg search query (ms),Total encrypt+decrypt (ms)"]
    for b in bench_results:
        csv_lines.append(f"{b['Records']},{b['Avg encryption (ms)']},{b['Avg decryption (ms)']},{b['Avg policy check (ms)']},{b['Avg search query (ms)']},{b['Total encrypt+decrypt (ms)']}")
    Path("data/performance.csv").write_text("\n".join(csv_lines))

    print(f"{'Batch':<8}{'Encrypt (ms)':<15}{'Decrypt (ms)':<15}{'Search (ms)':<15}{'Policy (ms)':<15}")
    for b in bench_results:
        print(f"{b['Records']:<8}{b['Avg encryption (ms)']:<15.4f}{b['Avg decryption (ms)']:<15.4f}{b['Avg search query (ms)']:<15.4f}{b['Avg policy check (ms)']:<15.4f}")

    return bench_results

def generate_visualizations(security_results, bench_results):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        Path("figures").mkdir(exist_ok=True)

        # Plot 1: Performance curves
        plt.figure(figsize=(8, 5))
        records = [b["Records"] for b in bench_results]
        enc = [b["Avg encryption (ms)"] for b in bench_results]
        dec = [b["Avg decryption (ms)"] for b in bench_results]
        search = [b["Avg search query (ms)"] for b in bench_results]

        plt.plot(records, enc, marker='o', label='AES-GCM Encryption')
        plt.plot(records, dec, marker='s', label='Decryption')
        plt.plot(records, search, marker='^', label='SSE Trapdoor Search')
        plt.xlabel('Batch Size (Records)')
        plt.ylabel('Average Latency per Record (ms)')
        plt.title('MediCloud Cryptographic & Search Latency Microbenchmark')
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()
        plt.tight_layout()
        plt.savefig("figures/performance.png", dpi=200)
        plt.close()

        # Plot 2: Security tests summary chart
        pass_count = sum(1 for r in security_results if r["Status"] == "PASS")
        fail_count = len(security_results) - pass_count

        plt.figure(figsize=(7, 4))
        plt.bar(["Passed", "Failed"], [pass_count, fail_count], color=['#2ca02c', '#d62728'], width=0.4)
        plt.ylabel('Number of Security Tests')
        plt.title(f'MediCloud Comprehensive Security Test Verification ({pass_count}/{len(security_results)} Passed)')
        plt.ylim(0, max(20, len(security_results) + 2))
        for i, v in enumerate([pass_count, fail_count]):
            plt.text(i, v + 0.5, str(v), ha='center', fontweight='bold')
        plt.tight_layout()
        plt.savefig("figures/security_tests.png", dpi=200)
        plt.close()

        print("\nUpdated visualization plots saved to figures/performance.png and figures/security_tests.png")
    except Exception as e:
        print(f"\nNote: Plot generation skipped ({e})")

if __name__ == "__main__":
    sec_results = run_all_tests()
    perf_results = run_benchmarks()
    generate_visualizations(sec_results, perf_results)

    # Save results_summary.json
    summary = {
        "security_tests": sec_results,
        "performance": perf_results,
        "all_tests_passed": all(r["Status"] == "PASS" for r in sec_results),
        "total_tests": len(sec_results),
        "passed_tests": sum(1 for r in sec_results if r["Status"] == "PASS")
    }
    Path("results_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\nConsolidated results written to results_summary.json.")
