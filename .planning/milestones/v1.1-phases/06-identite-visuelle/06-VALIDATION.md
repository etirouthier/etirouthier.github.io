---
phase: 6
slug: identite-visuelle
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-15
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None — single-file Streamlit app, no pytest infrastructure |
| **Config file** | none |
| **Quick run command** | `python -c "import ast; ast.parse(open('app.py').read()); print('syntax OK')"` |
| **Full suite command** | `streamlit run app.py` — verify header and welcome message render |
| **Estimated runtime** | ~2 seconds (syntax check) / ~5 seconds (local run) |

---

## Sampling Rate

- **After every task commit:** Run `python -c "import ast; ast.parse(open('app.py').read()); print('syntax OK')"`
- **After every plan wave:** Run `streamlit run app.py` locally and verify header + welcome message visually
- **Before `/gsd:verify-work`:** Header visible, welcome message appears on first load and disappears after first message, readable in light and dark themes
- **Max feedback latency:** ~2 seconds (syntax), ~30 seconds (visual)

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 6-01-01 | 01 | 1 | BRAND-01 | syntax+manual | `python -c "import ast; ast.parse(open('app.py').read())"` then verify header locally | ✅ | ⬜ pending |
| 6-01-02 | 01 | 1 | ACCU-01 | syntax+manual | `python -c "import ast; ast.parse(open('app.py').read())"` then verify welcome message locally | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

*Existing infrastructure covers all phase requirements. No new test files required — manual validation is the appropriate strategy for a single-file Streamlit app.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Header displays name and title | BRAND-01 | Visual HTML rendering requires browser | Open app; confirm "Etienne Routhier" and "Consultant Freelance — Data & IA" visible at top |
| Header readable in dark theme | BRAND-01 | Visual contrast requires browser | Toggle Streamlit dark mode; confirm header text is legible |
| Welcome message visible on first load | ACCU-01 | Streamlit UI requires browser | Open app in fresh session; confirm assistant bubble with intro text appears |
| Welcome message disappears after first message | ACCU-01 | Requires browser interaction | Send a message; confirm welcome bubble is no longer shown on rerun |
| Welcome message does not reappear on rerun | ACCU-01 | Requires interaction sequence | Continue chatting; confirm welcome bubble stays gone |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
