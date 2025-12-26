# To Run Locally

**Prerequisites:**  Node.js


1. Install dependencies:
   `npm install`
2. Set the `GEMINI_API_KEY` in [.env.local](.env.local) to your Gemini API key
3. Run the app:
   `npm run dev`


# Overview of the Redact AI's Working

**Interactive Data Anonymization Framework**

---

## Overview

SecureRedact Protocol is a multi-stage, user-controlled data anonymization framework designed to ensure sensitive information is handled with maximum transparency, privacy, and regulatory compliance. All critical screening and redaction steps occur locally before any optional cloud interaction.

---

## Multi-Stage Trust Architecture

A transparent process where you control exactly how your sensitive data is handled.

**Core Principles**
- Zero-Knowledge Screening
- Local Redaction
- Optional Cloud Audit

### Stage 1: Interactive Screening

Upon upload, the **Privacy Companion** performs a local scan that:
- Identifies document type
- Detects potential PII patterns (names, SSNs, identifiers)
- Operates entirely within the browser

No data leaves your device during this phase.

---

### Stage 2: Local Redaction

Redaction is performed locally using **Gemma-2-mini via Ollama**.

- Sensitive values are replaced with deterministic placeholders such as:

```
[REDACTED_NAME_1]
```

- Original data never leaves the local environment
- Redaction logic is repeatable and auditable

---

### Stage 3: Hybrid Verification

After local sanitization is complete, users may optionally send **only anonymized content** to **Gemini-3-Pro** for:
- Professional summarization
- Privacy leak detection
- Secondary risk analysis

Cloud interaction is strictly opt-in.

---

## Zero-Knowledge Screening Engine

### Conversational Intelligence

The Privacy Companion operates as a contextual, user-guided system:

- Automated detection of applicable privacy jurisdictions (GDPR, HIPAA, DPDP)
- Context-aware redaction (distinguishing headers, body text, identifiers)
- User-in-the-loop controls to adjust jurisdiction and redaction logic before processing

---

### Processing Lifecycle

```
1. INITIAL_SCAN(local_buffer)
   → COMPANION_CHAT(jurisdiction_match)
2. OLLAMA_REDACTION(deterministic_masking)
3. CLOUD_CONSENT_CHECK()
   → GEMINI_AUDIT(anonymized_view)
```

---

## Governance & Auditability

### Secure Export Options

Each session produces two independent artifacts:

**CLEAN DATA**  
Sanitized document suitable for sharing or storage in low-security environments.

**AUDIT LOG**  
A local JSON key enabling reversible redaction, allowing original values to be restored locally when authorized.

---

### Regulatory Compliance

By enforcing on-device risk assessment and redaction, SecureRedact supports strict data sovereignty and air-gapped compliance requirements.

Supported frameworks include:
- GDPR
- HIPAA
- DPDP
- PIPEDA
- CCPA
- LGPD

---

## Security Model Acknowledgement

The Redact AI is designed to ensure:
- User accountability of sharing sensitive data
- Deterministic and auditable anonymization
- Explicit consent for any cloud-based processing

Understanding this model is required before proceeding with document processing.

