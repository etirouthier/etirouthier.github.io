# Phase 5: Suggestions & Style — Research

**Researched:** 2026-03-15
**Domain:** Streamlit UI — suggestion chips, config.toml theming, set_page_config ordering
**Confidence:** HIGH

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| ACCU-02 | L'utilisateur voit 4 suggestions de questions ciblées pour un recruteur freelance (stack technique, types de missions, fit mission, disponibilité/TJM) | Verified: existing `st.button` + `st.columns` pattern in production; only string literals change. 4-chip layout decision documented in Open Questions. |
| BRAND-02 | Les boutons de suggestion s'affichent avec un style pill (arrondi) via config.toml | Verified: `[theme]` section with `buttonRadius = "full"` in `.streamlit/config.toml`; stable key confirmed in Streamlit 1.44–1.55 release notes. |
</phase_requirements>

---

## Summary

Phase 5 is a low-risk, two-requirement change on a working production app (Streamlit 1.55.0 at https://etirouthierappio.streamlit.app/). It touches exactly two files: `app.py` (string literal replacement for 4 recruiter chips + `st.set_page_config` insertion) and `.streamlit/config.toml` (new file, adds `buttonRadius = "full"` for pill-shaped buttons).

No new dependencies are required. Every API used (st.set_page_config, st.button, st.columns, config.toml theming) is stable, versioned, and available in the deployed production build. The only structural change to `app.py` is inserting `st.set_page_config()` as the absolute first `st.*` call — a hard Streamlit API constraint. Everything else is string replacement inside existing structures.

The implementation is fully deterministic. The planner can create concrete tasks without any exploratory work. The two critical constraints are: (1) `st.set_page_config` must precede all other `st.*` calls, including the `@st.cache_resource` decorated `load_vectorstore()` call; and (2) both `label` and `args` must be updated together on each button or clicking a chip will inject the old question text.

**Primary recommendation:** Add `st.set_page_config()` first, then replace 2-button layout with 4-chip layout in the existing `messages == 0` guard, then create `.streamlit/config.toml` with `[theme]` block. Deploy and verify on the live URL.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| streamlit | 1.55.0 (pinned in requirements-app.txt) | All UI rendering, config.toml theming | Already in production — no upgrade needed |

### Supporting

No new packages needed for this phase.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `config.toml [theme] buttonRadius` | Per-button CSS via `st.markdown` | config.toml is stable and propagates globally; per-button CSS risks using unstable internal class names that break on version bump |
| `st.columns(4)` (single row) | `st.columns(2)` x2 (two rows) | Single row is cleaner on desktop but may overflow on mobile; two rows match current 2-button layout exactly. Choice depends on label character count — see Open Questions. |

**Installation:**

No new packages. Stack is frozen.

---

## Architecture Patterns

### Current File Structure (relevant to this phase)

```
app.py                          # 103 lines — all changes land here
.streamlit/
    secrets.toml                # Exists — not modified in this phase
    config.toml                 # DOES NOT EXIST YET — created in this phase
config.py                       # Not touched in this phase
requirements-app.txt            # Not touched in this phase
```

### Pattern 1: st.set_page_config Placement

**What:** `st.set_page_config()` must be the very first Streamlit API call in the script — before imports trigger Streamlit runtime registration, before `@st.cache_resource` functions are defined, and before any `st.*` render calls.

**When to use:** Any time you add `st.set_page_config` to an existing app.

**Current app.py structure (line numbers):**
```
line 1-6:   imports (including `import streamlit as st`)
line 20:    @st.cache_resource decorator — this COUNTS as a st.* call
line 29-33: st.session_state init
line 39:    vectorstore = load_vectorstore()
line 41:    st.title(...)
```

**Correct placement after change:**
```python
# Source: Streamlit official docs — st.set_page_config
import streamlit as st
# ... other imports ...

st.set_page_config(
    page_title="Etienne Routhier — Dossier de Compétences",
    page_icon="💼",
    layout="centered",
)

@st.cache_resource(show_spinner="Chargement de la base de connaissances...")
def load_vectorstore():
    ...
```

The `st.set_page_config` call must appear **between the import block and the `@st.cache_resource` decorator**.

### Pattern 2: 4-Chip Suggestion Layout

**What:** Replace existing 2-column button layout with 4-chip layout inside the `messages == 0` guard.

**When to use:** First load only — already gated by existing session state check.

**Current structure (lines 49-62 in app.py):**
```python
if len(st.session_state.messages) == 0:
    col1, col2 = st.columns(2)
    with col1:
        st.button(
            "Quelles sont vos principales compétences ?",
            on_click=inject_question,
            args=("Quelles sont vos principales compétences ?",),
        )
    with col2:
        st.button(
            "En quoi pouvez-vous m'aider sur mon projet ?",
            on_click=inject_question,
            args=("En quoi pouvez-vous m'aider sur mon projet ?",),
        )
```

**Target structure — 4 chips covering the 4 recruiter mental questions:**
```python
# Source: Streamlit docs — st.button, st.columns
SUGGESTIONS = [
    "Quelle est votre stack technique principale ?",
    "Quels types de missions avez-vous réalisés ?",
    "Êtes-vous disponible et quel est votre TJM ?",
    "Seriez-vous un bon fit pour ma mission ?",
]

if len(st.session_state.messages) == 0:
    cols = st.columns(4)  # or st.columns(2) x2 — see Open Questions
    for i, (col, question) in enumerate(zip(cols, SUGGESTIONS)):
        with col:
            st.button(
                question,
                key=f"suggestion_{i}",
                on_click=inject_question,
                args=(question,),
            )
```

**Critical:** `key=f"suggestion_{i}"` prevents Streamlit button deduplication bugs when multiple buttons exist in the same render pass.

### Pattern 3: config.toml Pill Button Theming

**What:** Create `.streamlit/config.toml` with `[theme]` section to apply pill-shaped (fully rounded) style to all Streamlit buttons globally.

**When to use:** Global button style — no per-element override needed.

```toml
# Source: Streamlit theming docs — config.toml reference
[theme]
buttonRadius = "full"
```

The `buttonRadius` key accepts values: `"none"`, `"small"`, `"medium"`, `"large"`, `"full"`. `"full"` produces pill-shaped buttons (fully rounded corners). This key is stable in Streamlit 1.44–1.55 and does not use internal CSS class names.

### Anti-Patterns to Avoid

- **st.set_page_config after any st.* call:** Raises `StreamlitAPIException` immediately on load. No warning — immediate crash.
- **CSS targeting `.css-*` or `.st-emotion-cache-*` classes:** These are Streamlit internals that change on every version bump deployed to Community Cloud. Never use them.
- **Updating button `label` without updating `args`:** The chip injects `args[0]` when clicked, not the visible label. Out-of-sync label/args causes the wrong question to be sent to the RAG pipeline.
- **Placing buttons outside the `messages == 0` guard:** Chips reappear on every Streamlit rerun (every keypress, every widget interaction) because the full script re-executes on each interaction.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Pill-shaped buttons | Custom per-button CSS via `st.markdown` injecting `.stButton button { border-radius: ... }` | `config.toml [theme] buttonRadius = "full"` | CSS approach uses unstable internal class names; config.toml key is stable and version-tested |
| Button deduplication | Manual key management logic | `key=f"suggestion_{i}"` on each `st.button` | Streamlit handles deduplication when explicit keys are given |

**Key insight:** Streamlit's config.toml theming system was designed specifically to avoid the CSS hack anti-pattern. Use it.

---

## Common Pitfalls

### Pitfall 1: st.set_page_config Called After @st.cache_resource

**What goes wrong:** App raises `StreamlitAPIException: set_page_config() can only be called once per app page, and must be called as the first Streamlit command in your script.` — app is completely broken on load.

**Why it happens:** The `@st.cache_resource` decorator registers with Streamlit's runtime at module load time. Any `st.*` call above the decorator counts as "before set_page_config" — including the decorator itself.

**How to avoid:** Place `st.set_page_config(...)` immediately after the import block, before the `@st.cache_resource` decorator on line 20 of the current app.py.

**Warning signs:** Immediate crash on `streamlit run app.py` with `StreamlitAPIException`.

### Pitfall 2: Button args Not Updated with Label

**What goes wrong:** User clicks "Quelle est votre stack technique ?" chip but the RAG pipeline receives "Quelles sont vos principales compétences ?" — the old question from v1.0.

**Why it happens:** `st.button` injects `args[0]` via `inject_question`, not the visible label string. If label is updated but `args` is not, the old question string is injected.

**How to avoid:** Use a single constant `SUGGESTIONS` list and reference `question` for both `label` and `args=(question,)`. Never duplicate the string.

**Warning signs:** Clicking a chip triggers RAG but the question displayed in the chat does not match the button label.

### Pitfall 3: 4 Chips Overflowing on Mobile

**What goes wrong:** `st.columns(4)` in a single row makes each chip very narrow on mobile viewports, causing button text to wrap or overflow.

**Why it happens:** Streamlit columns divide the full page width equally; on narrow viewports, 4 equal columns leave ~80px per button.

**How to avoid:** Test on a mobile viewport width (375px) before finalizing layout. Alternative: 2 rows of `st.columns(2)`. See Open Questions for the decision.

**Warning signs:** Button text wraps or button is too small to tap on mobile.

### Pitfall 4: config.toml Not Committed

**What goes wrong:** Pill styling works locally but not on Streamlit Community Cloud after deploy.

**Why it happens:** `.streamlit/config.toml` must be committed to the repo. It is not a secret (unlike secrets.toml). The `.gitignore` correctly excludes only `secrets.toml`, not `config.toml`.

**How to avoid:** Confirm `.gitignore` excludes `secrets.toml` specifically, not the entire `.streamlit/` directory. Then commit `config.toml` alongside `app.py` changes.

**Warning signs:** Buttons look standard (square corners) on the live URL but pill-shaped locally.

---

## Code Examples

Verified patterns from official sources and direct codebase inspection:

### st.set_page_config (correct position in app.py)

```python
# Source: Streamlit official docs — st.set_page_config
import streamlit as st
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from config import EMBEDDING_MODEL, LLM_MODEL, K_RETRIEVED, FAISS_INDEX_PATH

load_dotenv()

st.set_page_config(
    page_title="Etienne Routhier — Dossier de Compétences",
    page_icon="💼",
    layout="centered",
)

SYSTEM_PROMPT = ...

@st.cache_resource(show_spinner="Chargement de la base de connaissances...")
def load_vectorstore():
    ...
```

### 4-Chip Suggestion Layout

```python
# Source: direct inspection of app.py + Streamlit docs — st.button, st.columns
SUGGESTIONS = [
    "Quelle est votre stack technique principale ?",
    "Quels types de missions avez-vous réalisés ?",
    "Êtes-vous disponible et quel est votre TJM ?",
    "Seriez-vous un bon fit pour ma mission ?",
]

if len(st.session_state.messages) == 0:
    cols = st.columns(4)
    for i, (col, question) in enumerate(zip(cols, SUGGESTIONS)):
        with col:
            st.button(
                question,
                key=f"suggestion_{i}",
                on_click=inject_question,
                args=(question,),
            )
```

### config.toml Pill Buttons

```toml
# Source: Streamlit theming docs — config.toml reference
# File: .streamlit/config.toml
[theme]
buttonRadius = "full"
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| 2 generic question buttons | 4 recruiter-targeted chips | Phase 5 (this phase) | Guides recruiter to highest-value questions in first 60 seconds |
| No config.toml | config.toml with `[theme]` block | Phase 5 (this phase) | Pill buttons signal professional design intent; stable across Streamlit versions |
| No st.set_page_config | st.set_page_config with page title | Phase 5 (this phase) | Browser tab shows candidate name instead of generic "streamlit" |

**Deprecated/outdated:**
- `st.beta_columns`: Use `st.columns` (stable API since Streamlit 1.0)
- Per-element CSS hacks targeting `.stButton button`: Replaced by config.toml `buttonRadius`

---

## Open Questions

1. **4-chip layout: `st.columns(4)` vs two rows of `st.columns(2)`**
   - What we know: Current app uses `st.columns(2)`. Label lengths for 4 recruiter questions are ~40-55 chars each. Streamlit Community Cloud deployment has no guaranteed mobile breakpoint.
   - What's unclear: Whether 4 columns on mobile (375px) will render button text legibly without wrapping.
   - Recommendation: Default to `st.columns(4)` (single row, cleaner). If labels wrap badly after deploy, switch to two rows of `st.columns(2)`. Validate on live URL at 375px viewport width.

2. **Exact wording of the 4 recruiter question chips**
   - What we know: The 4 mental questions are: technical stack, past project types, mission fit, availability/TJM. Research confirms these are the correct topics.
   - What's unclear: Exact French phrasing — formal "vous" vs informal, question length, natural recruiter phrasing.
   - Recommendation: Use the SUGGESTIONS constant defined in the Code Examples section. Can be adjusted at implementation time without structural change.

3. **Page icon for st.set_page_config**
   - What we know: `page_icon` accepts an emoji string or a PIL Image. Emoji is simplest.
   - What's unclear: Whether a specific emoji better fits the professional profile (briefcase vs document vs person).
   - Recommendation: Use `"💼"` (briefcase) as default. Implementation decision, not a blocker.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None detected — no pytest.ini, no test/ directory, no *.test.py files in repo |
| Config file | None |
| Quick run command | `streamlit run app.py --server.headless true` (smoke test: app loads without error) |
| Full suite command | Manual: open https://etirouthierappio.streamlit.app/ and click each chip |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| ACCU-02 | 4 recruiter chips visible on first load; clicking each triggers RAG with correct question | manual-smoke | `streamlit run app.py` — verify no crash on startup | ❌ Wave 0 |
| BRAND-02 | Buttons render with pill style (rounded corners) | manual-visual | Deploy and inspect on live URL | ❌ Wave 0 |

**Manual-only justification:** Streamlit UI rendering and visual styling require a running browser. There is no headless Streamlit testing framework in this project. The appropriate validation gate is: (1) `streamlit run app.py` completes without `StreamlitAPIException`, and (2) visual inspection on the live Community Cloud URL after deploy.

### Sampling Rate

- **Per task commit:** `python -c "import app"` — verifies no Python syntax errors (import without running Streamlit)
- **Per wave merge:** `streamlit run app.py` locally, verify chips display and pill style renders
- **Phase gate:** All 4 chips visible on live URL, each chip triggers RAG correctly, buttons show pill shape — before marking phase done

### Wave 0 Gaps

- [ ] No test infrastructure exists in the project — this is expected and acceptable for a single-file Streamlit app at this scale
- [ ] Smoke test: `python -c "import app"` will fail because `app.py` triggers `st.*` calls at module level — not a Wave 0 gap to fix, just means import-based smoke testing is not applicable; use `streamlit run` instead

*(No automated test files to create — manual validation is the appropriate strategy for this phase)*

---

## Sources

### Primary (HIGH confidence)

- Streamlit official docs — `st.set_page_config`, `st.button`, `st.columns`, config.toml `[theme]` theming keys
- Streamlit 2025–2026 release notes — `buttonRadius` key confirmed stable in versions 1.44–1.55
- Direct inspection of `/workspaces/etienne.routhier/app.py` (103 lines) — ground truth on current structure, execution order, session state shape, and exact lines to modify
- `.planning/research/SUMMARY.md` — milestone-level research with HIGH confidence ratings, all findings verified against official sources

### Secondary (MEDIUM confidence)

- STATE.md accumulated decisions — confirms `st.set_page_config` ordering constraint is a known project decision for Phase 5
- Streamlit community forum — config.toml `buttonRadius` theming patterns and CSS class name instability behavior

### Tertiary (LOW confidence)

- GitHub `streamlit/streamlit#4595` — button `on_click` callback timing behavior (relevant to `inject_question` pattern already in production)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — pinned to Streamlit 1.55.0 already in production; all APIs verified
- Architecture: HIGH — exact insertion points identified from direct code inspection; no ambiguity
- Pitfalls: HIGH — each pitfall backed by official docs or confirmed GitHub issues, mapped to specific lines in app.py
- 4-chip layout choice: MEDIUM — column count is an open question pending viewport validation

**Research date:** 2026-03-15
**Valid until:** 2026-06-15 (stable Streamlit APIs; config.toml theming keys are versioned)
