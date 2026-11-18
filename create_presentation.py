import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_presentation():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Colors
    C_NAVY_DARK = RGBColor(13, 27, 42)      # #0D1B2A
    C_NAVY_MED  = RGBColor(27, 38, 59)      # #1B263B
    C_BLUE_ACC  = RGBColor(0, 119, 182)     # #0077B6
    C_BLUE_CYAN = RGBColor(72, 202, 228)    # #48CAE4
    C_BG_LIGHT  = RGBColor(245, 247, 250)   # #F5F7FA
    C_WHITE     = RGBColor(255, 255, 255)
    C_TEXT_DARK = RGBColor(33, 37, 41)
    C_CARD_BG   = RGBColor(255, 255, 255)
    C_CARD_BORDER=RGBColor(222, 226, 230)

    def set_slide_bg(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.color.rgb = color
        return bg

    def add_header(slide, title_text, category_text="MEDICLOUD RESEARCH & SRE ARCHITECTURE"):
        tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.3))
        tf_cat = tb_cat.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_right = tf_cat.margin_top = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_BLUE_ACC

        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.6))
        tf_title = tb_title.text_frame
        tf_title.word_wrap = True
        tf_title.margin_left = tf_title.margin_right = tf_title.margin_top = tf_title.margin_bottom = 0
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = C_NAVY_DARK

    def create_card(slide, left, top, width, height, bg_color=C_CARD_BG, border_color=C_CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)
        return card

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide1, C_NAVY_DARK)

    bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.2), Inches(0.1), Inches(4.8))
    bar.fill.solid()
    bar.fill.fore_color.rgb = C_BLUE_CYAN
    bar.line.fill.background()

    tb1 = slide1.shapes.add_textbox(Inches(1.2), Inches(1.3), Inches(11.0), Inches(4.6))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p0 = tf1.paragraphs[0]
    p0.text = "CLOUD SRE AND DATA SECURITY | RESEARCH PROTOTYPE"
    p0.font.size = Pt(12)
    p0.font.bold = True
    p0.font.color.rgb = C_BLUE_CYAN
    p0.space_after = Pt(12)

    p1 = tf1.add_paragraph()
    p1.text = "MediCloud: Privacy-Preserving Cloud Data Sharing for Multi-Hospital EHRs"
    p1.font.size = Pt(28)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE
    p1.space_after = Pt(14)

    p2 = tf1.add_paragraph()
    p2.text = "End-to-End Implementation of Cryptographic Primitives & Resilient SRE Controls:\nSearchable Encryption (SSE), Multi-Authority ABAC, Proxy Re-Encryption (PRE), Dynamic Trust & Traitor Tracing"
    p2.font.size = Pt(13.5)
    p2.font.color.rgb = RGBColor(200, 215, 230)
    p2.space_after = Pt(36)

    p3 = tf1.add_paragraph()
    p3.text = "Divyanshu (23BEC017)  •  Adnan Khan (23BEC028)  •  Harshit Tripathi (23BCS054)\nSupervisor: Prof. Malay Kumar  •  Indian Institute of Information Technology Dharwad"
    p3.font.size = Pt(13)
    p3.font.bold = True
    p3.font.color.rgb = C_BLUE_CYAN

    # =========================================================================
    # SLIDE 2: THE PROBLEM & MOTIVATION
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide2, C_BG_LIGHT)
    add_header(slide2, "Why Cloud Privacy in Healthcare is Inherently Hard")

    col_w = 3.65
    gap = 0.38
    top_pos = 1.6
    h_pos = 5.2

    # Card 1: Semi-Trusted Cloud
    create_card(slide2, 0.8, top_pos, col_w, h_pos)
    tb = slide2.shapes.add_textbox(Inches(1.0), Inches(top_pos + 0.3), Inches(col_w - 0.4), Inches(h_pos - 0.6))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Semi-Trusted Cloud"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(12)
    bullets = [
        "Data Outsourcing: Hospitals surrender physical storage control to cloud providers.",
        "Curious Provider Threat: Cloud operators have physical access but must be prevented from reading diagnoses.",
        "Virtualization Risks: Multi-tenant hardware exposes potential side-channel and memory leakage.",
        "Regulatory Mandates: Storing plaintext violates HIPAA, GDPR, and Indian DPDP Act."
    ]
    for b in bullets:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(8)

    # Card 2: Multi-Organization Friction
    create_card(slide2, 0.8 + col_w + gap, top_pos, col_w, h_pos)
    tb = slide2.shapes.add_textbox(Inches(1.0 + col_w + gap), Inches(top_pos + 0.3), Inches(col_w - 0.4), Inches(h_pos - 0.6))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. Cross-Hospital Friction"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(12)
    bullets = [
        "No Central Authority: Hospital A cannot issue credentials for Hospital B or commercial labs.",
        "Dynamic Staff Changes: Doctors and residents frequently rotate between departments or leave institutions.",
        "Revocation Bottlenecks: Standard encryption requires re-downloading, decrypting, and re-uploading all records.",
        "Fine-Grained Isolation: Cardiologists in Hospital A must never access Oncology records in Hospital B."
    ]
    for b in bullets:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(8)

    # Card 3: Usability vs Security
    create_card(slide2, 0.8 + (col_w + gap) * 2, top_pos, col_w, h_pos)
    tb = slide2.shapes.add_textbox(Inches(1.0 + (col_w + gap) * 2), Inches(top_pos + 0.3), Inches(col_w - 0.4), Inches(h_pos - 0.6))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3. Usability & Insider Risks"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(12)
    bullets = [
        "Encrypted Search Need: Clinicians cannot operate if they must know exact record IDs; keyword queries are mandatory.",
        "Static Policy Failure: A doctor with legitimate credentials might turn rogue or suffer account takeover.",
        "Key Leakage & Espionage: If a clinician leaks their secret attribute key, identifying the culprit is traditionally impossible.",
        "The Research Goal: Interlock cryptography and SRE behavioral telemetry to solve all three."
    ]
    for b in bullets:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(12)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 3: LAYERED ARCHITECTURE (Interlocking 4 Families)
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide3, C_BG_LIGHT)
    add_header(slide3, "Layered Architecture: Interlocking Sun's 4 Primitive Families")

    qw = 5.6
    qh = 2.45
    
    create_card(slide3, 0.8, 1.6, qw, qh)
    tb = slide3.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(qw - 0.4), Inches(qh - 0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Multi-Authority ABAC (Policy Formulation)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    bullets = [
        "Eliminates single master key bottleneck across healthcare providers.",
        "CMA issues professional roles; Hospital Authorities issue local affiliations.",
        "Cryptographically signed credential tokens prevent cross-org forgery."
    ]
    for b in bullets:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK

    create_card(slide3, 6.8, 1.6, qw, qh)
    tb = slide3.shapes.add_textbox(Inches(7.0), Inches(1.75), Inches(qw - 0.4), Inches(qh - 0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. Proxy Re-Encryption (Dynamic Revocation)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    bullets = [
        "Textbook BBS98-style ElGamal over RFC 3526 1024-bit MODP safe prime.",
        "Delegates blind ciphertext transformation from Key A to Key B to cloud.",
        "Zero plaintext exposure to cloud; departing staff locked out immediately."
    ]
    for b in bullets:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK

    create_card(slide3, 0.8, 4.35, qw, qh)
    tb = slide3.shapes.add_textbox(Inches(1.0), Inches(4.5), Inches(qw - 0.4), Inches(qh - 0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3. Searchable Symmetric Encryption (Usability)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    bullets = [
        "Inverted index utilizing blind HMAC-SHA256 keyword trapdoors.",
        "Enables clinical search queries (e.g. 'cardiology', 'hypertension').",
        "Cloud matches trapdoors blindly with zero knowledge of search terms."
    ]
    for b in bullets:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK

    create_card(slide3, 6.8, 4.35, qw, qh)
    tb = slide3.shapes.add_textbox(Inches(7.0), Inches(4.5), Inches(qw - 0.4), Inches(qh - 0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "4. Dynamic Trust & Traitor Tracing (Behavior & Leaks)"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    bullets = [
        "Continuous behavioral telemetry: penalty on expired/cross-hospital probes.",
        "Dual-gate access control: quarantines users falling below threshold (0.40).",
        "HMAC key watermarking pinpoints rogue staff if keys are leaked online."
    ]
    for b in bullets:
        p = tf.add_paragraph()
        p.text = "• " + b
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_TEXT_DARK

    # =========================================================================
    # SLIDE 4: PHASE 1 - SEARCHABLE ENCRYPTION + PLOT
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide4, C_BG_LIGHT)
    add_header(slide4, "Phase 1: Searchable Symmetric Encryption (SSE)")

    create_card(slide4, 0.8, 1.6, 5.6, 5.2)
    tb = slide4.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Cryptographic Workflow & Guarantees"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(8)

    steps = [
        "• Deterministic Trapdoor Derivation:\n  Client hashes keyword w with master search key:\n  Tw = HMAC-SHA256(K_search, normalize(w))",
        "• Cloud-Side Blind Inverted Index:\n  Cloud stores Index[Tw] → [record_id_1, record_id_2, ...]\n  Contains only 64-char hex digests, zero plaintext words.",
        "• Sub-Millisecond Search Latency:\n  Trapdoor generation and index lookup complete in ~2.8 µs, supporting real-time clinical querying.",
        "• Security Verification (Test 8 & 9):\n  ✓ Keyword query matches valid records without decrypting.\n  ✓ Cloud index privacy verified (trapdoors only)."
    ]
    for s in steps:
        p = tf.add_paragraph()
        p.text = s
        p.font.size = Pt(11)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(6)

    # Embed SSE scaling plot
    create_card(slide4, 6.8, 1.6, 5.6, 5.2)
    img_sse = "figures/sse_search_scaling.png"
    if os.path.exists(img_sse):
        slide4.shapes.add_picture(img_sse, Inches(6.9), Inches(1.8), width=Inches(5.4))

    # =========================================================================
    # SLIDE 5: PHASE 2 - MULTI-AUTHORITY ABAC + PLOT
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide5, C_BG_LIGHT)
    add_header(slide5, "Phase 2: Decentralized Multi-Authority Access Control")

    create_card(slide5, 0.8, 1.6, 5.6, 5.2)
    tb = slide5.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Federated Multi-Organization Model"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(8)

    items = [
        "• Eliminating Single Points of Trust:\n  No single organization holds master encryption keys.",
        "• Independent Authority Roles:\n  - CMA: National roles ('role:doctor', 'license:active').\n  - Hospital Authorities: Local departments ('cardiology').\n  - Diagnostic Labs: Pathology credentials.",
        "• Cross-Organization Forgery Defense:\n  Hospital B cannot sign credentials for Hospital A; signature verification instantly rejects forged claims.",
        "• Linear Verification Scaling O(k):\n  Verification overhead scales at ~0.8 µs per authority.",
        "• Security Verification (Test 12 & 13):\n  ✓ Multi-authority authorized access passes.\n  ✓ Cross-organization forgery is cleanly rejected."
    ]
    for it in items:
        p = tf.add_paragraph()
        p.text = it
        p.font.size = Pt(11)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(6)

    # Embed Multi-Authority scaling plot
    create_card(slide5, 6.8, 1.6, 5.6, 5.2)
    img_ma = "figures/multi_authority_scaling.png"
    if os.path.exists(img_ma):
        slide5.shapes.add_picture(img_ma, Inches(7.0), Inches(1.8), width=Inches(5.2))

    # =========================================================================
    # SLIDE 6: PHASE 3 - PROXY RE-ENCRYPTION + PLOT
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide6, C_BG_LIGHT)
    add_header(slide6, "Phase 3: Proxy Re-Encryption (PRE) for Staff Revocation")

    create_card(slide6, 0.8, 1.6, 5.6, 5.2)
    tb = slide6.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "BBS98 Construction & SRE Benefits"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(8)

    pre_items = [
        "• Safe Prime Cryptosystem:\n  MODP safe prime p = 2q + 1 (RFC 3526), generator g = 2.",
        "• Delegated Re-Encryption Key:\n  rk_(A→B) = (sk_A)^(-1) · sk_B mod q\n  Authority sends only rk to cloud upon staff departure.",
        "• Cloud Blind Transformation:\n  Cloud computes c1' = (c1)^(rk_(A→B)) = g^(sk_B · r) mod p\n  Transforms ciphertext without knowing plaintext or keys!",
        "• Network Bandwidth Savings:\n  Replaces gigabytes of client download/upload with an O(1) single key transmission.",
        "• Security Verification (Test 10 & 11):\n  ✓ Cloud delegation succeeds.\n  ✓ Departed staff locked out (PRE_DECAPSULATION_FAILED)."
    ]
    for it in pre_items:
        p = tf.add_paragraph()
        p.text = it
        p.font.size = Pt(11)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(6)

    # Embed PRE vs Traditional plot
    create_card(slide6, 6.8, 1.6, 5.6, 5.2)
    img_pre = "figures/pre_vs_traditional.png"
    if os.path.exists(img_pre):
        slide6.shapes.add_picture(img_pre, Inches(6.9), Inches(1.8), width=Inches(5.4))

    # =========================================================================
    # SLIDE 7: PHASE 4 - DYNAMIC TRUST ENGINE + PLOT
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide7, C_BG_LIGHT)
    add_header(slide7, "Phase 4: Dynamic Behavioral Trust & Reputation Engine")

    create_card(slide7, 0.8, 1.6, 5.6, 5.2)
    tb = slide7.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Behavioral Telemetry & Quarantine"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(8)

    trust_items = [
        "• Sun's 4 Trust Pillars Implemented:\n  Formation (T_0=0.60), Dynamic Updates, Time Decay, and Interlocking Access Gate.",
        "• Continuous Scoring Telemetry:\n  +0.05 on verified clinical accesses.\n  -0.25 penalty on unauthorized cross-hospital probes.\n  -0.15 on expired requests; -0.35 on tampering.",
        "• Inactivity Exponential Decay:\n  Trust score regresses towards baseline during idle periods.",
        "• Automated Account Quarantine:\n  Scores falling below 0.40 are quarantined; requests are blocked (TRUST_SCORE_INSUFFICIENT) even if attributes match!",
        "• Security Verification (Test 14 & 15):\n  ✓ Valid activity boosts trust (0.60 → 0.75).\n  ✓ Repeated attack probes trigger immediate quarantine."
    ]
    for it in trust_items:
        p = tf.add_paragraph()
        p.text = it
        p.font.size = Pt(11)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(6)

    # Embed Trust Decay plot
    create_card(slide7, 6.8, 1.6, 5.6, 5.2)
    img_trust = "figures/trust_decay_timeline.png"
    if os.path.exists(img_trust):
        slide7.shapes.add_picture(img_trust, Inches(6.9), Inches(1.8), width=Inches(5.4))

    # =========================================================================
    # SLIDE 8: PHASE 5 - TRAITOR TRACING & RADAR CHART
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide8, C_BG_LIGHT)
    add_header(slide8, "Phase 5: Traitor Tracing & Comprehensive Security Profile")

    create_card(slide8, 0.8, 1.6, 5.6, 5.2)
    tb = slide8.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(5.2), Inches(4.8))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Key Leak Tracing & SRE Controls"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(8)

    tracer_items = [
        "• Cryptographic Identity Watermarks:\n  Every issued user key embeds an HMAC fingerprint:\n  Watermark = HMAC-SHA256(K_master_trace, user_id)",
        "• Pinpointing Rogue Staff:\n  If a doctor key is leaked or posted online, trace_leaked_key() extracts the tag and identifies the culprit with 100% mathematical certainty.",
        "• AES-256-GCM AEAD Binding:\n  Binds record_id as Additional Authenticated Data (AAD) to prevent ciphertext swapping attacks.",
        "• Tamper-Evident SHA-256 Digest:\n  Bit alterations trigger INTEGRITY_FAILED before decryption.",
        "• Security Verification (Test 16):\n  ✓ Leaked key for 'D-ROUGE-42' precisely identified."
    ]
    for it in tracer_items:
        p = tf.add_paragraph()
        p.text = it
        p.font.size = Pt(11)
        p.font.color.rgb = C_TEXT_DARK
        p.space_after = Pt(6)

    # Embed Radar plot
    create_card(slide8, 6.8, 1.6, 5.6, 5.2)
    img_radar = "figures/security_radar.png"
    if os.path.exists(img_radar):
        slide8.shapes.add_picture(img_radar, Inches(7.0), Inches(1.8), width=Inches(5.2))

    # =========================================================================
    # SLIDE 9: TEST SUITE VERIFICATION (16/16 PASSED) + PLOT
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide9, C_BG_LIGHT)
    add_header(slide9, "Security Verification: 16 / 16 Functional Tests Passed")

    create_card(slide9, 0.8, 1.6, 6.2, 5.2)
    tb = slide9.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.8), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Executed Security Test Suite (100% Pass Rate)"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_NAVY_DARK
    p.space_after = Pt(6)

    tests_list = [
        ("1. Authorized Doctor", "SUCCESS"),
        ("2. Cross-Hospital Isolation", "ATTRIBUTE_POLICY_DENIED"),
        ("3. Cloud Operator Access", "ATTRIBUTE_POLICY_DENIED"),
        ("4. Expired Access Check", "ACCESS_EXPIRED"),
        ("5. Modified Ciphertext", "INTEGRITY_FAILED"),
        ("6. Access Audit Trail", "SUCCESS"),
        ("7. Plaintext Visibility", "CIPHERTEXT_ONLY"),
        ("8. SSE Keyword Match", "MATCH_FOUND"),
        ("9. SSE Index Privacy", "TRAPDOORS_ONLY"),
        ("10. PRE Cloud Delegation", "SUCCESS"),
        ("11. PRE Departed Staff Revocation", "PRE_DECAPSULATION_FAILED"),
        ("12. Multi-Authority Doctor Access", "SUCCESS"),
        ("13. Multi-Authority Cross-Org Forgery", "REJECTED (FAIL)"),
        ("14. Dynamic Trust Elevation", "SCORE_INCREASED"),
        ("15. Dynamic Trust Quarantine", "TRUST_SCORE_INSUFFICIENT"),
        ("16. Traitor Tracing Key Leak", "TRAITOR_IDENTIFIED")
    ]
    for t_name, t_res in tests_list:
        p = tf.add_paragraph()
        p.text = f"✓ {t_name:<36} → {t_res}"
        p.font.size = Pt(9.2)
        p.font.color.rgb = C_TEXT_DARK

    # Embed security tests bar chart
    create_card(slide9, 7.3, 1.6, 5.2, 5.2)
    img_sec = "figures/security_tests.png"
    if os.path.exists(img_sec):
        slide9.shapes.add_picture(img_sec, Inches(7.4), Inches(1.8), width=Inches(5.0))

    # =========================================================================
    # SLIDE 10: PERFORMANCE LATENCY BREAKDOWN + PLOT
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide10, C_BG_LIGHT)
    add_header(slide10, "Performance Evaluation: Sub-Millisecond SRE Overhead")

    # Left: Embed Performance Plot
    create_card(slide10, 0.8, 1.6, 5.6, 5.2)
    img_breakdown = "figures/latency_breakdown.png"
    if os.path.exists(img_breakdown):
        slide10.shapes.add_picture(img_breakdown, Inches(0.9), Inches(1.8), width=Inches(5.4))

    # Right: Embed Performance curves plot
    create_card(slide10, 6.8, 1.6, 5.6, 5.2)
    img_perf = "figures/performance.png"
    if os.path.exists(img_perf):
        slide10.shapes.add_picture(img_perf, Inches(6.9), Inches(1.8), width=Inches(5.4))

    # =========================================================================
    # SLIDE 11: CONCLUSION & ENGINEERING ROADMAP
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_bg(slide11, C_NAVY_DARK)

    tb_c = slide11.shapes.add_textbox(Inches(1.2), Inches(1.0), Inches(11.0), Inches(5.5))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True

    p = tf_c.paragraphs[0]
    p.text = "CONCLUSION & ENGINEERING ROADMAP"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_BLUE_CYAN
    p.space_after = Pt(12)

    p1 = tf_c.add_paragraph()
    p1.text = "MediCloud: Transforming Theoretical Survey into a Working Prototype"
    p1.font.size = Pt(26)
    p1.font.bold = True
    p1.font.color.rgb = C_WHITE
    p1.space_after = Pt(18)

    c_points = [
        "1. Full Feature Implementation: Successfully realized all 5 theoretical mechanisms from Sun's IEEE Access (2019) survey (SSE, MA-ABAC, BBS98 PRE, Dynamic Trust, and Traitor Tracing).",
        "2. Rigorous Security Verification: 16 out of 16 security and cryptographic tests passed without a single failure.",
        "3. High SRE Efficiency: Maintained sub-millisecond per-record processing speeds, proving that layered multi-hospital privacy is practical on modern cloud systems.",
        "4. Production Roadmap: Future integration with Hardware Security Modules (AWS CloudHSM / GCP Cloud KMS), Zero-Knowledge Proofs (ZKP), and Post-Quantum Cryptography (PQC) lattice-based schemes."
    ]
    for cp in c_points:
        p = tf_c.add_paragraph()
        p.text = cp
        p.font.size = Pt(13)
        p.font.color.rgb = RGBColor(220, 230, 240)
        p.space_after = Pt(12)

    output_file = "MediCloud_Presentation.pptx"
    prs.save(output_file)
    print(f"Presentation successfully updated with all embedded plots: {output_file}")

if __name__ == "__main__":
    build_presentation()
