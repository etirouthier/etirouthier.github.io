---
phase: 1
slug: setup-configuration
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-13
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Aucun framework de test — phase de configuration pure |
| **Config file** | none — Wave 0 crée les fichiers |
| **Quick run command** | `python -c "from config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, K_RETRIEVED, FAISS_INDEX_PATH; print('OK')"` |
| **Full suite command** | `pip install -r requirements.txt && python -c "from config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, K_RETRIEVED, FAISS_INDEX_PATH; print('All constants OK')"` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -c "from config import EMBEDDING_MODEL; print(EMBEDDING_MODEL)"`
- **After every plan wave:** Run `pip install -r requirements.txt && python -c "from config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, K_RETRIEVED; print('All constants OK')"`
- **Before `/gsd:verify-work`:** Full suite must be green + manual checklist passed
- **Max feedback latency:** ~10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 1 | SETUP-01 | smoke | `git check-ignore -v .streamlit/secrets.toml` | ❌ W0 | ⬜ pending |
| 1-01-02 | 01 | 1 | SETUP-02 | smoke | `python -c "from config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, K_RETRIEVED, FAISS_INDEX_PATH; print('OK')"` | ❌ W0 | ⬜ pending |
| 1-01-03 | 01 | 1 | SETUP-03 | smoke | `pip install -r requirements.txt` (dans venv propre) | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `.gitignore` — couvre SETUP-01
- [ ] `config.py` — couvre SETUP-02
- [ ] `requirements.txt` — couvre SETUP-03
- [ ] `.streamlit/secrets.toml` (local, jamais commité) — pour valider l'exclusion SETUP-01

*Tous les livrables sont des créations from scratch — aucune infrastructure de test préexistante.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `secrets.toml` n'apparaît pas dans `git status` | SETUP-01 | Vérification visuelle Git | 1. Créer `.streamlit/secrets.toml` 2. Lancer `git status` 3. Confirmer que le fichier N'apparaît PAS |
| `faiss_index/` apparaît dans `git status` | SETUP-01 (contre-vérification) | Valider que l'index n'est pas exclu à tort | 1. Créer `faiss_index/` vide 2. `git status` 3. Confirmer que le dossier APPARAÎT |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
