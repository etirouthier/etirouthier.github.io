---
phase: 2
slug: build-de-l-index-faiss
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-13
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Aucun framework de test — smoke tests via CLI |
| **Config file** | none |
| **Quick run command** | `python -c "from config import EMBEDDING_MODEL, FAISS_INDEX_PATH; print('config OK')"` |
| **Full suite command** | `python build_index.py && ls faiss_index/` |
| **Estimated runtime** | ~30 seconds (appel API Mistral) |

---

## Sampling Rate

- **After every task commit:** Run `python -c "from config import EMBEDDING_MODEL, FAISS_INDEX_PATH; print('config OK')"`
- **After every plan wave:** Run `python build_index.py && ls faiss_index/`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 2-01-01 | 01 | 1 | INDEX-01 | smoke | `python -c "from langchain_community.document_loaders import PyPDFDirectoryLoader; d=PyPDFDirectoryLoader('assets/', recursive=True); print(len(d.load()), 'pages')"` | ✅ | ⬜ pending |
| 2-01-02 | 01 | 1 | INDEX-02 | smoke | `python build_index.py && ls faiss_index/` | ❌ W0 | ⬜ pending |
| 2-01-03 | 01 | 1 | INDEX-03 | smoke | `git check-ignore faiss_index/ 2>&1 \| grep -v "faiss_index" && echo "OK: not ignored"` | ✅ | ⬜ pending |
| 2-01-04 | 01 | 1 | INDEX-04 | smoke | `python build_index.py 2>&1 \| grep "chunks"` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `build_index.py` — couvre INDEX-01, INDEX-02, INDEX-04
- [ ] `MISTRAL_API_KEY` définie dans l'environnement — prérequis pour lancer le script

*(`.gitignore`, `config.py`, et `requirements.txt` existent déjà depuis Phase 1)*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Logs affichent texte lisible et bien découpé | INDEX-04 | Qualité subjective — l'humain doit lire les aperçus de chunks | Lancer `python build_index.py`, lire l'output "=== Validation des chunks ===" et vérifier que les 3 premiers chunks sont cohérents et lisibles |
| `faiss_index/` visible dans `git status` | INDEX-03 | Vérification git visuelle | Après `python build_index.py`, lancer `git status` et confirmer que `faiss_index/index.faiss` et `faiss_index/index.pkl` apparaissent comme untracked |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
