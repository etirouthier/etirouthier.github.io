---
phase: 5
slug: suggestions-style
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-15
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — single-file Streamlit app, no pytest infrastructure |
| **Config file** | none |
| **Quick run command** | `python -c "import ast; ast.parse(open('app.py').read()); print('syntax OK')"` |
| **Full suite command** | `streamlit run app.py` — verify chips display and pill style renders |
| **Estimated runtime** | ~2 seconds (syntax check) / ~5 seconds (local run) |

---

## Sampling Rate

- **After every task commit:** Run `python -c "import ast; ast.parse(open('app.py').read()); print('syntax OK')"`
- **After every plan wave:** Run `streamlit run app.py` locally and verify visually
- **Before `/gsd:verify-work`:** All 4 chips visible on live URL, each triggers RAG correctly, buttons show pill shape
- **Max feedback latency:** ~2 seconds (syntax), ~30 seconds (visual)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 5-01-01 | 01 | 1 | BRAND-02 | syntax | `python -c "import ast; ast.parse(open('app.py').read())"` | ✅ | ⬜ pending |
| 5-01-02 | 01 | 1 | ACCU-02 | syntax+manual | `python -c "import ast; ast.parse(open('app.py').read())"` then verify chips locally | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements. No new test files required — manual validation is the appropriate strategy for a single-file Streamlit app.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 4 recruiter chips visible on first load | ACCU-02 | Streamlit UI requires a running browser | Open app locally or on live URL; confirm 4 buttons display with correct text on first load |
| Clicking each chip triggers RAG with correct question | ACCU-02 | Requires browser interaction | Click each chip; verify the displayed question in chat matches the button label |
| Buttons render with pill (rounded) style | BRAND-02 | Visual CSS rendering requires browser | Open app; confirm buttons have fully rounded corners |
| App loads without StreamlitAPIException | ACCU-02, BRAND-02 | Streamlit runtime required | `streamlit run app.py` — no exception on startup |
| config.toml pill style applies on live URL | BRAND-02 | Streamlit Cloud deployment required | Deploy and inspect at https://etirouthierappio.streamlit.app/ |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
