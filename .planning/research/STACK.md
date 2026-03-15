# Stack Research: Streamlit UX Polish — Branding, Welcome Message, Suggestion Chips

**Domain:** Streamlit UI customization (theming, CSS injection, chat UX patterns)
**Researched:** 2026-03-15
**Confidence:** HIGH — verified against Streamlit 1.55.0 official docs (the version already in production)

---

## Context

This is a **subsequent milestone** (v1.1) on an existing app. The validated stack
(Streamlit 1.55.0 · LangChain · FAISS-cpu · Mistral API) is frozen. This document
covers only what's needed for the three new UX features:

1. Professional header (name, title, freelance positioning)
2. Contextual welcome message
3. Recruiter-targeted suggestion chips

**No new Python packages are required.** Every technique below uses capabilities
already present in Streamlit 1.55.0.

---

## Core Technologies (unchanged)

| Technology | Version | Status |
|------------|---------|--------|
| `streamlit` | 1.55.0 | Already in `requirements-app.txt` — no upgrade needed |
| Python | 3.11 | Already in production |

---

## Techniques for New Features

### 1. Page-level Branding — `st.set_page_config`

**Purpose:** Sets browser tab title and favicon. First impression before the page renders.

```python
st.set_page_config(
    page_title="Etienne Routhier — Consultant Freelance",
    page_icon="💼",   # emoji or URL to .ico / .png
    layout="centered",
)
```

**Why this first:** `set_page_config` must be the first Streamlit call in the script.
In Streamlit 1.46+ it can be called multiple times additively, but placing it first
is still the correct pattern for a single-page app.

**Confidence:** HIGH — official docs, available since Streamlit 1.0.

---

### 2. In-page Header — `st.markdown` with `unsafe_allow_html=True`

**Purpose:** Renders a custom HTML/CSS block as the visual header: name, title, tagline.

**Why `st.markdown` over `st.html`:** `st.html` (added April 2024, updated in 1.55.0)
is DOMPurify-sanitized, meaning it strips `<style>` tags. `st.markdown` with
`unsafe_allow_html=True` injects raw HTML directly into the page without sanitization,
which is required to embed inline `<style>` blocks. For a static, developer-controlled
string this is safe.

**Pattern:**
```python
st.markdown("""
<style>
.profile-header {
    text-align: center;
    padding: 1.5rem 0 1rem 0;
    border-bottom: 1px solid #e0e0e0;
    margin-bottom: 1rem;
}
.profile-header h1 { margin: 0; font-size: 1.8rem; }
.profile-header p  { margin: 0.25rem 0 0 0; color: #666; font-size: 1rem; }
</style>
<div class="profile-header">
    <h1>Etienne Routhier</h1>
    <p>Consultant Freelance — Architecture & Développement Logiciel</p>
</div>
""", unsafe_allow_html=True)
```

**Streamlit 1.55.0 note:** In 1.55.0, `st.markdown` supports arbitrary CSS colors for
text foreground/background in Markdown syntax (`$\color{red}{text}$` style). However,
inline HTML remains the most reliable pattern for a structured header layout.

**Confidence:** HIGH — documented pattern, works on Streamlit Community Cloud.

---

### 3. Global Theming — `.streamlit/config.toml`

**Purpose:** Controls primary color, font, border radius, background colors globally
without per-element CSS overrides.

**Why config.toml over inline CSS:** Changes propagate to all elements automatically
(buttons, chat bubbles, inputs). CSS overrides can fight with Streamlit's internal
styles across version updates. config.toml is the supported, stable API.

**Available keys relevant to this project (verified in 1.44–1.55 docs):**

```toml
[theme]
base = "light"

# Colors
primaryColor     = "#1a73e8"      # buttons, links, active elements
backgroundColor  = "#ffffff"      # page background
secondaryBackgroundColor = "#f8f9fa"  # widget backgrounds, sidebar
textColor        = "#1c1c1e"      # body text

# Typography (added in 1.44+)
font             = "sans serif"   # "sans serif", "serif", "monospace", or Google Fonts URL
baseFontSize     = 16             # pixels (added 1.47)
headingFont      = "sans serif"   # can differ from body font

# Shapes (added in 1.44+)
baseRadius       = "medium"       # "none", "small", "medium", "large", "full"
buttonRadius     = "medium"       # can override independently (added 1.46)

# Borders
showWidgetBorder = false          # hides borders around inputs for cleaner look
```

**Google Fonts example (if a custom typeface is desired):**
```toml
[theme]
font = "Inter:https://fonts.googleapis.com/css2?family=Inter&display=swap"
```

**Warning:** Google Fonts transmits visitor IP to Google servers. For a public
professional portfolio this is generally acceptable, but it must be noted.

**Confidence:** HIGH — config keys verified against Streamlit 1.44–1.55 release notes
and official theming docs.

---

### 4. Welcome Message — `st.chat_message` + `st.markdown`

**Purpose:** Displays a first assistant message before the user types anything,
explaining what the chatbot can do.

**Pattern:** Render a static assistant bubble when `messages` session state is empty.
This uses the existing `st.chat_message` pattern already in the app.

```python
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        st.markdown(
            "Bonjour ! Je suis l'assistant d'Etienne Routhier. "
            "Posez-moi vos questions sur son profil, ses compétences, "
            "ou ses expériences."
        )
```

**Why not `st.info` or a custom div:** `st.chat_message` is already styled consistently
with the conversation thread. A custom div would break visual continuity. No new API
needed.

**Confidence:** HIGH — uses existing `st.chat_message` API, no new features required.

---

### 5. Suggestion Chips — `st.button` in `st.columns`

**Purpose:** Displays clickable question chips before the first user message.

**Current implementation (v1.0):** 2 buttons in 2 columns. The v1.1 goal is to
replace generic questions with recruiter-targeted ones and potentially add a third.

**Pattern (existing, to be updated with new labels):**
```python
if len(st.session_state.messages) == 0:
    col1, col2 = st.columns(2)
    with col1:
        st.button("Question recruteur 1", on_click=inject_question,
                  args=("Question recruteur 1",))
    with col2:
        st.button("Question recruteur 2", on_click=inject_question,
                  args=("Question recruteur 2",))
```

**For 3 chips:** Use `st.columns(3)` or wrap in 2 rows of 2.

**CSS styling for chip-like appearance** (optional, via config.toml `buttonRadius`):
Setting `buttonRadius = "full"` in `config.toml` gives all buttons a pill shape,
resembling standard suggestion chips. This is a global setting — acceptable if all
buttons in this app should look this way.

**Why NOT a custom component:** `streamlit-pills`, `streamlit-extras` suggestion_chip,
or custom JS chips add dependencies and potential Streamlit Cloud compatibility issues.
Native `st.button` in columns achieves the same UX without new packages.

**Confidence:** HIGH — native API, already validated in production.

---

## What NOT to Add

| Avoid | Why | Instead |
|-------|-----|---------|
| `streamlit-extras` / `streamlit-pills` | Extra dependency, potential version conflicts with Streamlit 1.55.0, adds `requirements-app.txt` weight | Native `st.button` in columns |
| `streamlit-option-menu` | Heavy component for navigation that isn't needed here | Not applicable |
| Bootstrap / Tailwind CSS CDN | Conflicts with Streamlit's internal CSS specificity; also loads ~300KB external JS | Inline CSS via `st.markdown` |
| `st.components.v1.html` iframes | Creates sandboxed iframe — CSS in iframes does NOT apply to main app; wrong tool for global styling | `st.markdown(unsafe_allow_html=True)` for global CSS |
| `st.html` for `<style>` injection | DOMPurify strips `<style>` tags — does not work for injecting CSS rules | `st.markdown(unsafe_allow_html=True)` |
| Hiding Streamlit header/footer via CSS hacks | `data-testid` selectors break on Streamlit version updates; Streamlit ToS discourages it | Leave default header; use `menu_items` in `set_page_config` to customize the menu |
| Google Fonts if GDPR is a concern | External font CDN transmits visitor IP; minor for this use case but worth noting | Use `font = "sans serif"` (bundled Source Sans) if no custom typeface is needed |

---

## No New Packages Required

The `requirements-app.txt` stays unchanged:

```
streamlit==1.55.0
langchain-mistralai==1.1.1
langchain-community==0.4.1
langchain-core==1.2.18
faiss-cpu==1.13.2
pypdf==6.8.0
python-dotenv==1.2.2
```

All three new features (header, welcome message, suggestion chips) are implemented
with Python code and a `.streamlit/config.toml` file. No pip installs needed.

---

## File Changes Summary

| File | Change |
|------|--------|
| `app.py` | Add `set_page_config`, header markdown block, welcome message in chat bubble, update button labels |
| `.streamlit/config.toml` | Create (or update) `[theme]` section with primaryColor, baseRadius, font |
| `requirements-app.txt` | No change |

---

## Version Compatibility Notes

| Feature | Min Streamlit Version | In Production (1.55.0) |
|---------|-----------------------|------------------------|
| `st.set_page_config` | 0.85.0 | Yes |
| `st.markdown(unsafe_allow_html=True)` | 0.50.0 | Yes |
| `config.toml [theme]` colors | 0.84.0 | Yes |
| `config.toml baseRadius`, `font` (advanced) | 1.44.0 (March 2025) | Yes |
| `config.toml buttonRadius` | 1.46.0 (June 2025) | Yes |
| `config.toml baseFontSize`, `headingFontWeights` | 1.47.0 (July 2025) | Yes |
| `st.chat_message` | 1.17.0 | Yes |
| `st.html` | 1.31.0 (April 2024) | Yes (but not used for CSS) |

All features are available in Streamlit 1.55.0. No version upgrade is required.

---

## Sources

- [Streamlit Theming docs](https://docs.streamlit.io/develop/concepts/configuration/theming) — config.toml keys verified HIGH confidence
- [Streamlit config.toml reference](https://docs.streamlit.io/develop/api-reference/configuration/config.toml) — full key list
- [Streamlit Customize fonts](https://docs.streamlit.io/develop/concepts/configuration/theming-customize-fonts) — Google Fonts syntax
- [Streamlit 2025 release notes](https://docs.streamlit.io/develop/quick-reference/release-notes/2025) — 1.44/1.46/1.47 theming features
- [Streamlit 2026 release notes](https://docs.streamlit.io/develop/quick-reference/release-notes/2026) — 1.55.0 Markdown CSS color support
- [st.html docs](https://docs.streamlit.io/develop/api-reference/text/st.html) — DOMPurify sanitization behavior
- [st.header docs](https://docs.streamlit.io/develop/api-reference/text/st.header) — text_alignment, divider params
- [st.set_page_config docs](https://docs.streamlit.io/develop/api-reference/configuration/st.set_page_config) — page_title, page_icon, menu_items

---

*Stack research for: Streamlit UX Polish v1.1 — Chatbot CV*
*Researched: 2026-03-15*
