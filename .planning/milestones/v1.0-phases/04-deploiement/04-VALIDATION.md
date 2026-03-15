---
phase: 4
slug: deploiement
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-13
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | bash (git/curl checks — no pytest needed for deploy phase) |
| **Config file** | none |
| **Quick run command** | `git ls-files faiss_index/ && echo OK` |
| **Full suite command** | `git ls-files faiss_index/ && git grep -r "MISTRAL_API_KEY" -- '*.py' || true` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After Task 1 commit:** Run `git ls-files faiss_index/` (index committed check)
- **After deploy:** `curl -I {deployed_url}` returns 200

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 4-01-01 | 01 | 1 | DEPLOY-01, DEPLOY-02 | automated | `git ls-files faiss_index/ \| wc -l` returns >0 | ⬜ pending |
| 4-01-02 | 01 | 1 | DEPLOY-02 | automated | `git grep -rn "MISTRAL_API_KEY" -- '*.py' '*.toml'` returns only config.py usage | ⬜ pending |
| 4-01-03 | 01 | 1 (CP) | DEPLOY-01 | manual | Human deploys on share.streamlit.io + verifies URL | ⬜ pending |

---

## Wave 0 Requirements

None — no new test files needed. Verification is git/curl based.

*Existing infrastructure covers all phase requirements.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| App deployed on Streamlit Cloud | DEPLOY-01 | No CLI for Streamlit Community Cloud | share.streamlit.io → New app → select repo/branch/file → Deploy |
| Secret configured in dashboard | DEPLOY-02 | Dashboard UI only | Advanced settings → Secrets → add MISTRAL_API_KEY |
| App loads and chat works | DEPLOY-01 | Browser required | Visit deployed URL, verify chat interface visible |

---

## Validation Sign-Off

- [ ] `faiss_index/` tracked in git
- [ ] No MISTRAL_API_KEY in committed source files
- [ ] Deployed URL returns HTTP 200
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
