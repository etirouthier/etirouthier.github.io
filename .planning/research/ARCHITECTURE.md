# Architecture Research

**Domain:** Streamlit single-file chatbot — v1.1 UX integration points
**Researched:** 2026-03-15
**Confidence:** HIGH

## Standard Architecture

### System Overview — Existing app.py Execution Flow

Streamlit re-executes `app.py` top-to-bottom on every user interaction. The current 102-line file has a clear linear execution order that constrains where each new feature must be inserted.

```
app.py execution order (v1.0 — annotated)
─────────────────────────────────────────────────────
Lines  1-9    IMPORTS + load_dotenv()
Lines 11-17   SYSTEM_PROMPT constant
Lines 20-25   load_vectorstore() — @st.cache_resource definition
Lines 29-32   SESSION STATE INIT — messages[], pending_question
Lines 35-37   inject_question() function definition
Line  39      vectorstore = load_vectorstore()     ← cached call
Line  41      st.title(...)                        ← RENDERS title
Lines 44-46   HISTORY LOOP — renders past turns
Lines 49-62   EMPTY-STATE BLOCK (if messages == 0)
              └─ 2 suggestion buttons in 2 columns
Lines 65-68   chat_input resolution + pending_question consume
Lines 70-102  ACTIVE QUESTION HANDLER — RAG + LLM + append
─────────────────────────────────────────────────────
```

### v1.1 Integration Map — Where Each Feature Goes

```
app.py execution order (v1.1 — with changes annotated)
─────────────────────────────────────────────────────
Lines  1-9    IMPORTS + load_dotenv()              (unchanged)
Lines 11-17   SYSTEM_PROMPT constant               (unchanged)

              ┌────────────────────────────────────┐
              │  [NEW] HEADER_HTML constant        │
              │  [NEW] WELCOME_MESSAGE constant    │ ← define at top
              └────────────────────────────────────┘

Lines 20-25   load_vectorstore() definition        (unchanged)
Lines 29-32   SESSION STATE INIT                   (unchanged)
Lines 35-37   inject_question() definition         (unchanged)

              ┌────────────────────────────────────┐
              │  [NEW] st.set_page_config(...)     │ ← FEATURE 1 (part)
              └────────────────────────────────────┘
              CONSTRAINT: must be first st.* call,
              after all function defs, before
              vectorstore = load_vectorstore()

Line  39      vectorstore = load_vectorstore()     (unchanged)

              ┌────────────────────────────────────┐
              │  [REPLACE] st.title(...)           │
              │  → st.markdown(HEADER_HTML,        │ ← FEATURE 1 (part)
              │      unsafe_allow_html=True)       │   Branding header
              └────────────────────────────────────┘

Lines 44-46   HISTORY LOOP                         (unchanged)

Lines 49-62   EMPTY-STATE BLOCK (if messages == 0)
              ┌────────────────────────────────────┐
              │  [NEW — first line of block]       │
              │  with st.chat_message("assistant"):│ ← FEATURE 2
              │      st.markdown(WELCOME_MESSAGE)  │   Welcome message
              └────────────────────────────────────┘
              └─ [MODIFY] button text strings only │ ← FEATURE 3
                 columns layout + callback unchanged   Recruiter suggestions

Lines 65-102  CHAT INPUT + RAG HANDLER             (unchanged)
─────────────────────────────────────────────────────
```

### Component Responsibilities

| Component | Responsibility | v1.1 Change |
|-----------|----------------|-------------|
| `SYSTEM_PROMPT` constant | LLM instruction set | No change |
| `load_vectorstore()` | FAISS + embeddings, cached | No change |
| Session state init block | Init `messages[]` + `pending_question` | No change |
| `st.set_page_config()` | Browser tab title, favicon | NEW — insert before first `st.*` render call |
| Header block | Page heading, visual identity | REPLACE `st.title()` with `st.markdown(HTML)` |
| History loop | Replay previous conversation turns | No change |
| Empty-state block `(messages == 0)` | Welcome content + suggestion buttons | EXTEND — add welcome bubble; replace button strings |
| `inject_question()` | Button callback routing | No change |
| Chat input + RAG handler | User turn processing, LLM call | No change |

## Recommended Project Structure

No file splits required. All v1.1 changes are contained within `app.py`. The single-file structure is correct at this scale (~130 lines post-v1.1).

```
etienne.routhier/
├── app.py                  ← 3 targeted edit zones
├── config.py               ← No change
├── build_index.py          ← No change
├── .streamlit/
│   └── secrets.toml        ← No change
├── faiss_index/            ← No change
└── requirements-app.txt    ← No change
```

### Structure Rationale

- **No new files:** The three features are UI strings and one new API call. Extracting them to a `ui.py` or `components.py` adds indirection with no benefit at this scale.
- **Constants in app.py, not config.py:** `HEADER_HTML` and `WELCOME_MESSAGE` are presentation strings, not shared configuration. `config.py` is reserved for values shared between `app.py` and `build_index.py` — mixing concerns there would obscure the critical `EMBEDDING_MODEL` constant.

## Architectural Patterns

### Pattern 1: st.set_page_config() — Mandatory First Position

**What:** `st.set_page_config()` configures the browser tab title and favicon. Streamlit enforces it as the first `st.*` call in the script; any earlier `st.*` call raises `StreamlitAPIException`.

**When to use:** Any time you want a custom tab title or favicon. Currently absent from v1.0 (tab shows the filename).

**Trade-offs:** Hard constraint with no workaround. Must precede `vectorstore = load_vectorstore()` even though that call is cached and produces no visible output — because `@st.cache_resource` registers with Streamlit's runtime.

**Placement:** After the `inject_question()` function definition, before `vectorstore = load_vectorstore()`.

```python
st.set_page_config(
    page_title="Etienne Routhier — Dossier de Compétences",
    page_icon="💼",
    layout="centered",
)
```

### Pattern 2: HTML Branding Header via st.markdown

**What:** Replace `st.title()` with `st.markdown(HTML, unsafe_allow_html=True)` to render a name + subtitle block with custom styling.

**When to use:** When native Streamlit text components lack the styling control needed (font-size hierarchy, subtitle line, color differentiation).

**Trade-offs:** `unsafe_allow_html=True` is sandboxed inside Streamlit's React iframe — no XSS risk for static content. Known regression: since Streamlit 1.46.0, inline code blocks inside the same `st.markdown` call render incorrectly when `unsafe_allow_html=True`. Mitigation: isolate the HTML header in its own dedicated `st.markdown` call, separate from any content with backtick code.

**Placement:** Replace line 41 (`st.title(...)`).

```python
HEADER_HTML = """
<div style="text-align: center; padding: 1rem 0 0.5rem 0;">
    <h1 style="margin: 0; font-size: 2rem;">Etienne Routhier</h1>
    <p style="margin: 0.25rem 0 0 0; color: #666; font-size: 1.1rem;">
        Consultant Freelance — Data &amp; IA
    </p>
</div>
"""

st.markdown(HEADER_HTML, unsafe_allow_html=True)
```

### Pattern 3: Welcome Message Inside the Existing Empty-State Guard

**What:** Render a `st.chat_message("assistant")` welcome bubble as the first statement inside the already-existing `if len(st.session_state.messages) == 0:` block, before the suggestion buttons.

**When to use:** Any time you want content visible only before the conversation starts, using the chat bubble visual style for consistency.

**Trade-offs:** Reusing the existing guard is correct — no new state variable needed. The alternative of placing the welcome message unconditionally above the history loop is wrong: it would persist throughout the entire conversation, re-rendering above every turn.

**Placement:** First line of the `if len(st.session_state.messages) == 0:` block (currently line 49), before `col1, col2 = st.columns(2)`.

```python
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        st.markdown(WELCOME_MESSAGE)
    col1, col2 = st.columns(2)
    # ... existing button code follows ...
```

### Pattern 4: Recruiter Suggestion Buttons — String-Only Replacement

**What:** The existing 2-column, 2-button layout with `on_click=inject_question` callback is the correct mechanism. Only the string literals passed to `st.button()` and `args=(...)` need updating.

**When to use:** When the interaction mechanic is already correct and only the content needs updating — the lowest-risk change.

**Trade-offs:** No structural change. The columns layout, `inject_question` callback, and `pending_question` session state mechanism are all preserved. Focus purely on replacing generic question strings with recruiter-oriented ones (availability, TJM, past projects, remote work).

**Placement:** Lines 52-62 — replace string literals in `st.button()` calls.

## Data Flow

### Rendering Flow (Every Rerun)

```
Script start
    ↓
set_page_config()          ← browser tab metadata (no visible output)
    ↓
load_vectorstore()         ← cache hit after first load (no visible output)
    ↓
st.markdown(HEADER_HTML)   ← renders branding header
    ↓
History loop               ← renders 0..N past chat bubbles
    ↓
[if messages == 0]
  chat_message("assistant") ← renders welcome bubble
  st.columns + st.button x2 ← renders suggestion buttons
    ↓
st.chat_input()            ← renders input bar (always pinned to bottom)
    ↓
[if active_question]
  render user bubble
  RAG: similarity_search → context chunks
  LLM: ChatMistralAI.invoke → answer
  render assistant bubble
  append to session_state.messages
    ↓
End of script (Streamlit waits for next interaction)
```

### State Management

```
st.session_state
├── messages[]           ← list of {role, content} dicts
│   drives: history loop render, empty-state guard, LangChain message build
└── pending_question     ← str | None
    drives: button-click → chat pipeline bridge (inject_question callback)
```

The branding header and welcome message have no state — they are pure render-time string outputs. The suggestion button text changes do not affect state shape or the callback mechanism.

## Integration Points

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Header HTML → Streamlit renderer | `st.markdown(..., unsafe_allow_html=True)` | Isolated call — do not mix with other markdown content to avoid Streamlit 1.46+ inline-code bug |
| Welcome message → empty-state guard | Nested inside `if len(messages) == 0` | Reuses existing condition; no new state key needed |
| Suggestion buttons → RAG pipeline | `inject_question()` callback + `pending_question` | Mechanic entirely unchanged; only string literals updated |
| `st.set_page_config()` → script runtime | Must precede all other `st.*` calls | Insert after function defs, before `vectorstore = load_vectorstore()` |

### Build Order (Implementation Sequence)

Build in this order to minimize revert surface area:

1. **`st.set_page_config()`** — Zero risk. Isolated call. Validates tab title on first deploy. No interaction with any other component.
2. **Recruiter suggestion text** — Lowest risk. String-only change inside existing structure. Immediately verifiable visually on first load.
3. **Welcome message** — Low risk. New `st.chat_message` block inside existing guard. Obvious on first load; disappears after first message confirming guard works correctly.
4. **Branding header** — Moderate risk (HTML). Replace `st.title()` last, after confirming the rest renders correctly. Test in both Streamlit light and dark themes — the `color: #666` in the subtitle may need a CSS variable or `prefers-color-scheme` consideration for dark mode.

## Anti-Patterns

### Anti-Pattern 1: Welcome Message Outside the Empty-State Guard

**What people do:** Place `st.chat_message("assistant")` with the welcome text unconditionally, above the history loop, so it "always shows at the top."

**Why it's wrong:** It re-renders permanently above every conversation turn on every rerun. A recruiter sees the welcome message re-appear after every message they send — visually broken.

**Do this instead:** Place it inside `if len(st.session_state.messages) == 0:` — the existing guard already handles this correctly.

### Anti-Pattern 2: st.set_page_config() After Any st.* Call

**What people do:** Add `st.set_page_config()` after `vectorstore = load_vectorstore()` or after the header render, assuming "it just sets metadata."

**Why it's wrong:** Streamlit raises `StreamlitAPIException: set_page_config() can only be called once per app, and must be called as the first Streamlit command in your script.` The `@st.cache_resource` decorator triggers Streamlit's runtime before producing any visible output — it still counts as a Streamlit command.

**Do this instead:** Place `st.set_page_config()` as the very first `st.*` call in the file, after all function definitions, before `vectorstore = load_vectorstore()`.

### Anti-Pattern 3: Moving HEADER_HTML and WELCOME_MESSAGE to config.py

**What people do:** Add the new string constants to `config.py` to "centralize all constants."

**Why it's wrong:** `config.py` documents its own purpose as sharing values between `app.py` and `build_index.py` — specifically to prevent embedding model drift. Presentation strings have no role in `build_index.py`. Mixing concerns makes the critical `EMBEDDING_MODEL` constant harder to locate.

**Do this instead:** Define `HEADER_HTML` and `WELCOME_MESSAGE` as module-level constants at the top of `app.py`, after imports and before `SYSTEM_PROMPT`.

### Anti-Pattern 4: Combining HTML Header in Same st.markdown as Other Markdown Content

**What people do:** Write one large `st.markdown()` call mixing the HTML header block with regular markdown text, passing `unsafe_allow_html=True`.

**Why it's wrong:** Since Streamlit 1.46.0, inline code blocks (backtick syntax) render incorrectly inside any `st.markdown` call that uses `unsafe_allow_html=True`. The current app stack uses Streamlit 1.55 — this bug is present.

**Do this instead:** Keep the HTML header in its own isolated `st.markdown(HEADER_HTML, unsafe_allow_html=True)` call. Subsequent content using regular markdown should use separate `st.markdown()` calls without the flag.

## Sources

- Streamlit official docs — `st.set_page_config` (first-call constraint): https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config
- Streamlit official docs — `st.chat_message` API reference: https://docs.streamlit.io/develop/api-reference/chat/st.chat_message
- Streamlit official docs — build a basic LLM chat app (empty-state pattern): https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps
- Streamlit 2025 release notes (st.html enhancements, text_alignment): https://docs.streamlit.io/develop/quick-reference/release-notes/2025
- Streamlit GitHub issue — inline code blocks broken with unsafe_allow_html >= 1.46.0: https://github.com/streamlit/streamlit/issues/11888
- Streamlit community — custom header branding patterns: https://discuss.streamlit.io/t/add-branding-to-my-header/81223

---
*Architecture research for: Streamlit UX improvements — branding header, welcome message, recruiter suggestions*
*Researched: 2026-03-15*
