# Phase 4: Déploiement — Research

**Written:** 2026-03-13
**Confidence:** HIGH

---

## What We're Deploying

- **App:** `app.py` (102 lines, Streamlit RAG chatbot)
- **Deps:** `requirements.txt` (pinned, includes streamlit, langchain-mistralai, faiss-cpu)
- **Index:** `faiss_index/` committed to git (intentionally — `.gitignore` explicitly excludes it from exclusions)
- **Secret:** `MISTRAL_API_KEY` — must live in Streamlit Cloud dashboard secrets, NOT in code

---

## Streamlit Community Cloud Deployment

### How It Works

1. Streamlit Cloud pulls from a public GitHub repo at a specified branch + file path
2. It installs dependencies from `requirements.txt` automatically
3. Secrets set in the dashboard are injected as `st.secrets` (same interface as `secrets.toml` locally)
4. The app runs on Streamlit's infrastructure — no server to manage

### What `app.py` Already Does Right

- `MISTRAL_API_KEY = st.secrets["MISTRAL_API_KEY"]` — correct pattern for both local and cloud
- `faiss_index/` is committed → available post-clone → `FAISS.load_local()` will find it
- `requirements.txt` is pinned → reproducible builds

### Key Constraint: `requirements.txt` Size

The current `requirements.txt` is the full codespace environment (jupyter, nbdime, etc.) — **Streamlit Cloud will try to install all of it**, which will:
- Be very slow (200+ packages)
- Risk install failures on packages that require system libs not present on Streamlit Cloud
- Potentially exceed memory limits

**Mitigation:** Create a minimal `requirements.txt` with only what the app needs:
```
streamlit
langchain-mistralai
langchain-community
faiss-cpu
pypdf
```
Keep the full env in a separate file (e.g., `requirements-dev.txt`) for local use.

### Deployment Steps (Manual — Streamlit Cloud has no CLI)

Streamlit Community Cloud deployment is done via the web UI at share.streamlit.io:
1. Connect GitHub account
2. Select repo + branch + `app.py`
3. Click Deploy
4. Add `MISTRAL_API_KEY` secret in Advanced Settings

This is a **checkpoint:human-action** — there is no CLI for Streamlit Cloud deployment.

### Post-Deploy Verification

After deployment, Claude can:
- `curl -I https://share.streamlit.io/...` to check HTTP 200
- But cannot interact with the UI (browser-only)

The URL is known only after deployment — it follows the pattern:
`https://{username}-{repo-name}-{hash}.streamlit.app`

Or via custom slug if configured.

---

## Pitfalls

1. **`faiss-cpu` on Linux:** Streamlit Cloud runs Linux — `faiss-cpu` PyPI wheel supports Linux x86_64 ✓
2. **`allow_dangerous_deserialization=True`** in `FAISS.load_local()` — required since LangChain 0.2, already in `app.py`
3. **Cold start time:** `@st.cache_resource` runs once per session lifecycle — first load may take 5-10s loading the index
4. **`MISTRAL_API_KEY` secret name:** Must match exactly — `app.py` uses `st.secrets["MISTRAL_API_KEY"]`

---

## Validation Architecture

### Automated (what Claude can verify before and after deploy)
- `requirements.txt` contains only necessary packages (no jupyter, no nbdime)
- `faiss_index/` is tracked in git (`git ls-files faiss_index/`)
- `MISTRAL_API_KEY` not present in any committed file (`git grep -r "MISTRAL_API_KEY" -- '*.py' '*.toml'`)
- HTTP 200 from deployed URL after human deploys

### Manual-Only (requires human + browser)
- Streamlit Cloud dashboard: connect repo, set secret, click Deploy
- Visual verification: UI loads, chat works, API key not exposed

---

## Plan Structure Recommendation

**1 plan, 2 tasks:**
- **Task 1 (auto):** Créer `requirements-app.txt` minimal + vérifier git readiness (index commité, secret non commité)
- **Task 2 (checkpoint:human-action):** Déployer sur Streamlit Cloud via le dashboard + configurer secret + vérifier URL

No wave parallelization needed — sequential.
