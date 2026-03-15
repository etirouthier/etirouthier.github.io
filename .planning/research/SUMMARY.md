# Project Research Summary

**Project:** Chatbot CV — v1.1 UX Polish (Branding, Welcome Message, Suggestion Chips)
**Domain:** Streamlit single-page chatbot — professional portfolio for freelance consultant
**Researched:** 2026-03-15
**Confidence:** HIGH

## Executive Summary

This is a polish milestone on a working v1.0 production app. The RAG chatbot (Streamlit 1.55.0, LangChain, FAISS-cpu, Mistral API) is fully validated and deployed at https://etirouthierappio.streamlit.app/. The three features in scope — a professional branding header, a contextual welcome message, and recruiter-targeted suggestion chips — are all low-complexity, low-risk UI additions that require zero new dependencies. Every technique uses Streamlit capabilities already present in production and thoroughly documented.

The recommended approach is to implement the three features in a strictly ordered sequence that minimizes the blast radius of each change: page config first (isolated, zero-risk), recruiter suggestion text second (string-only replacement, lowest risk), welcome message third (new block inside existing guard), and the HTML branding header last (the only change that involves custom CSS and carries moderate regression risk). This ordering is dictated by both Streamlit's hard API constraints (`st.set_page_config` must be the first `st.*` call in the script) and the principle of validating simpler changes before more complex ones.

The primary risk for this milestone is not feature complexity but implementation hygiene: misplacing `st.set_page_config` crashes the app immediately; using unstable internal Streamlit CSS class names causes silent regressions on future deploys; and placing the welcome message outside the existing session-state guard causes it to reappear above every chat turn. All three risks have clear, documented prevention strategies. No architectural decisions are required — the single-file structure is correct at this scale (~130 lines post-v1.1).

---

## Key Findings

### Recommended Stack

The stack is frozen at Streamlit 1.55.0 with no new packages required. All three features are implemented through existing Streamlit APIs: `st.set_page_config()` for browser tab metadata, `st.markdown(unsafe_allow_html=True)` for the HTML/CSS header (not `st.html`, which strips `<style>` tags via DOMPurify), `st.chat_message` for the welcome bubble (reusing the existing chat pattern), and `st.button` in `st.columns` for suggestion chips (updating labels only, no structural change).

Theme customization via `.streamlit/config.toml` is available and uses stable, versioned keys (`primaryColor`, `baseRadius`, `buttonRadius`) verified against the 1.44–1.55 release notes. The `[theme]` section is the recommended path for global styling (pill-shaped buttons, brand color) rather than per-element CSS overrides, since it propagates automatically to all Streamlit UI elements.

**Core technologies:**
- `streamlit==1.55.0`: All three features use APIs available since Streamlit 1.17.0 or earlier — no upgrade needed
- `st.markdown(unsafe_allow_html=True)`: The correct injection path for `<style>` blocks and custom HTML; `st.html` is explicitly wrong for CSS injection (DOMPurify strips style tags)
- `.streamlit/config.toml [theme]`: Stable, version-resilient global styling via `primaryColor`, `baseRadius`, `buttonRadius`, `font`

### Expected Features

Research into the French freelance IT recruiter market confirms that all three features are table-stakes expectations for a candidate portfolio in 2026. Missing them makes the app feel unfinished or anonymous.

**Must have (table stakes for v1.1):**
- Professional header (name + freelance positioning) — recruiters expect immediate identity; a generic app title does not establish who the candidate is
- Contextual welcome message — removes "what is this?" ambiguity for cold visitors; must not restate the title but explain the chatbot's scope and limitations
- 4 recruiter-targeted suggestion chips — replaces 2 generic v1.0 buttons; must address the 4 mental questions recruiters ask in the first 60 seconds: technical skills, past project types, mission fit, and availability/TJM

**Should have (differentiators):**
- Pill-shaped buttons via `buttonRadius = "full"` in config.toml — signals professional design intent
- Welcome message that acknowledges chatbot limitations honestly — builds more trust than overclaiming

**Defer to v1.2+:**
- Contact links (email, LinkedIn) in header — requires a public disclosure decision on what to expose
- Dynamic post-response suggestions — requires LLM prompt engineering, out of scope
- Streamlit footer/branding suppression — not reliably achievable on Community Cloud; CSS hacks break on every Streamlit version update

### Architecture Approach

All v1.1 changes are contained within `app.py` (~130 lines post-change) and the optional `.streamlit/config.toml` file. No file splits, no new modules, no new imports. The execution flow is linear and fully mapped: `set_page_config` inserts before the first `st.*` render call; the HTML header replaces the existing `st.title()`; the welcome message inserts as the first statement inside the already-existing `if len(st.session_state.messages) == 0:` block; and the suggestion buttons are updated by changing string literals only.

**Major components and their v1.1 changes:**
1. `st.set_page_config()` — NEW: browser tab title and favicon; hard constraint: must precede all other `st.*` calls, including `@st.cache_resource` decorated functions
2. Header block — REPLACE: `st.title()` with `st.markdown(HEADER_HTML, unsafe_allow_html=True)` in an isolated call (not mixed with other markdown content)
3. Empty-state block — EXTEND: insert `st.chat_message("assistant")` welcome bubble as the first statement; update button string literals and `args` tuples for the 4 new recruiter chips

### Critical Pitfalls

1. **`st.set_page_config` called after any `st.*` call** — raises `StreamlitAPIException` and crashes the app on load. Place it as the absolute first `st.*` call after imports and before `load_vectorstore()`. The `@st.cache_resource` decorator registers with Streamlit's runtime and counts as a `st.*` call.

2. **CSS targeting unstable internal class names (`.css-*`, `.st-emotion-cache-*`)** — silently breaks after any Streamlit version bump on Community Cloud. Use only stable selectors or build self-contained HTML/CSS blocks via `st.markdown`. Never write CSS based on browser DevTools inspection of Streamlit internals.

3. **Welcome message rendered outside the `messages == 0` guard** — reappears above every chat turn on every Streamlit rerun because Streamlit re-executes the full script on every interaction. Must be inside `if len(st.session_state.messages) == 0:`, the same block already used for suggestion buttons.

4. **HTML header mixed into same `st.markdown` call as other markdown content** — since Streamlit 1.46.0, inline code blocks render incorrectly inside any `st.markdown` with `unsafe_allow_html=True`. Keep the HTML header in its own isolated `st.markdown` call; never combine with regular markdown text.

5. **Suggestion button `args` not updated to match new labels** — clicking a button injects the `args` tuple value, not the visible label string. When updating suggestion text, both `label` and `args=(question_string,)` must be updated together. Explicit `key=` parameters on each button prevent Streamlit deduplication bugs.

---

## Implications for Roadmap

The three features naturally form a single implementation phase with a well-defined internal build order. Dependencies and risk levels dictate the sequence.

### Phase 1: Page Config and Browser Identity

**Rationale:** `st.set_page_config()` has a hard Streamlit constraint that makes it the safest first change — it is entirely isolated, validates the deployment pipeline, and its failure mode is loud (immediate crash) rather than silent. It cannot be deferred once other `st.*` calls exist.

**Delivers:** Custom browser tab title ("Etienne Routhier — Dossier de Compétences") and favicon; confirms the app still loads cleanly on Streamlit Community Cloud after the first code change.

**Addresses:** Table-stakes identity feature; the recruiter's first impression is the browser tab, not the page.

**Avoids:** Pitfall 1 (`set_page_config` ordering crash).

### Phase 2: Recruiter Suggestion Chips

**Rationale:** The lowest-risk content change — only string literals are modified inside a structure that already works in production. Validating the core recruiter value (guided question flow) independently before any new UI structures are added reduces debugging surface area.

**Delivers:** 4 recruiter-targeted question chips replacing the 2 generic v1.0 buttons: technical skills, past project types, mission fit, and availability. Directly addresses the 4 mental questions French freelance IT recruiters ask in the first 60 seconds.

**Addresses:** Must-have table-stakes feature with the highest conversion value for recruiter experience.

**Avoids:** Pitfall 5 (suggestion button state corruption) by explicitly updating both `label` and `args` and adding `key=` parameters to each button.

### Phase 3: Welcome Message

**Rationale:** Logically paired with suggestion chips (both live in the `messages == 0` guard). Adding it after Phase 2 confirms the empty-state block is working correctly before a new element is inserted into it. Depends on Phase 1 (app loads cleanly).

**Delivers:** An `st.chat_message("assistant")` welcome bubble visible on first load, explaining the chatbot's purpose and scope. Disappears after the first question is sent, consistent with suggestion chips behavior.

**Addresses:** Must-have table-stakes feature; removes "what is this?" ambiguity for cold visitors.

**Avoids:** Pitfall 3 (welcome message redisplay on every rerun) by placing it inside the existing `if len(st.session_state.messages) == 0:` guard.

### Phase 4: Branding Header

**Rationale:** The most complex of the four changes — custom HTML/CSS, replaces `st.title()`. Placed last because: (a) it is the only change with a moderate regression risk (dark/light theme color mismatch, HTML rendering quirks), (b) all other features are confirmed working before touching the primary visual element, and (c) it depends on Phase 1 being in place.

**Delivers:** A centered header with name ("Etienne Routhier") and subtitle ("Consultant Freelance — Data & IA"), replacing the generic app title. Establishes professional identity at first glance.

**Addresses:** Must-have table-stakes feature with the highest visual impact for recruiter first impression.

**Avoids:** Pitfall 2 (unstable CSS class names) via self-contained inline styles on semantic HTML elements only. Avoids Pitfall 4 by isolating the `st.markdown(HEADER_HTML, unsafe_allow_html=True)` call from any other markdown content.

### Phase Ordering Rationale

- **Constraint-driven ordering:** `st.set_page_config` must be first — this is a hard Streamlit API rule, not a preference. It cannot be moved after the fact without restructuring the file.
- **Risk-ascending ordering:** String changes before new UI blocks before custom HTML. Each phase validates the app is still deployable before the next phase introduces more complexity.
- **Dependency-aware ordering:** The welcome message and suggestion chips share the `messages == 0` guard — confirming the guard still works after Phase 2 before adding a second element into it in Phase 3.
- **Pitfall-mapped ordering:** The sequence directly matches the pitfall-to-phase mapping in PITFALLS.md, ensuring each critical pitfall is addressed at the earliest phase that introduces the relevant code.

### Research Flags

Phases with standard, well-documented patterns (research-phase not needed):

- **All 4 phases:** Every technique is verified against official Streamlit 1.55.0 docs with HIGH confidence. No novel integrations, no third-party APIs, no authentication, no data persistence. The implementation is deterministic and requires no exploratory research.

Areas requiring implementation-time verification (not research, just testing):

- **Phase 4 (Branding Header):** Test the header in both Streamlit light and dark themes on the live URL. The `color: #666` subtitle color may need adjustment for dark mode. Verify on the deployed app at https://etirouthierappio.streamlit.app/ — CSS can behave differently on first visit due to browser caching of the old version.
- **All phases:** Verify on the live Streamlit Community Cloud URL after each deploy, not just locally.

---

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Verified against Streamlit 1.55.0 official docs and 2025–2026 release notes; all APIs confirmed present in the production version; no new packages |
| Features | HIGH | App inspected directly from source; recruiter psychology grounded in French freelance IT market (Free-Work) and UX chatbot research from multiple sources |
| Architecture | HIGH | Execution flow mapped against the actual 102-line `app.py`; all integration points and ordering constraints verified in official Streamlit docs |
| Pitfalls | HIGH | Each pitfall backed by official docs, confirmed GitHub issues, or community forum threads with reproducible symptoms and known recovery steps |

**Overall confidence:** HIGH

### Gaps to Address

- **Dark mode header color:** The `color: #666` hardcoded hex in the subtitle HTML may be invisible or low-contrast in Streamlit dark mode. This is a known gap — validate visually after Phase 4 implementation and use CSS variables (`var(--text-color)`) if needed. Not a blocker, but must be verified before marking Phase 4 done.
- **Exact welcome message copy:** Research defines what the message must cover (chatbot purpose, what can be asked, limitations) and what it must not do (restate the page title). Final French copy is an implementation decision, not a research decision.
- **4-chip layout choice:** 4 buttons can be laid out as `st.columns(4)` (single row) or two rows of `st.columns(2)`. The current app uses `st.columns(2)`. Choice depends on label length. Validate on a 1080p viewport and on mobile before finalizing.

---

## Sources

### Primary (HIGH confidence)
- Streamlit official docs — `st.set_page_config`, theming, `st.chat_message`, `st.markdown`, `st.html`, session state, button behavior
- Streamlit 2025–2026 release notes — feature availability verified per version (1.44, 1.46, 1.47, 1.55)
- Direct inspection of `/workspaces/etienne.routhier/app.py` — ground truth on current structure, execution order, and session state shape
- Free-Work — French freelance IT TJM and recruiter psychology (2026 market data)

### Secondary (MEDIUM confidence)
- Streamlit community forum — custom header branding patterns, CSS class name instability behavior
- FlowHunt / Landbot / Knak Digital — chatbot welcome message UX best practices
- Streamlit community forum — portfolio chatbot UX patterns and recruiter conversion signals

### Tertiary (awareness only)
- GitHub `streamlit/streamlit#11888` — `unsafe_allow_html` inline code rendering bug since 1.46
- GitHub `streamlit/streamlit#6456` — `prefers-color-scheme` CSS misalignment with Streamlit theme toggle
- GitHub `streamlit/streamlit#4595` — button `on_click` callback timing behavior

---
*Research completed: 2026-03-15*
*Ready for roadmap: yes*
