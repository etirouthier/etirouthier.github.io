# Pitfalls Research

**Domain:** Streamlit UX Polish — CSS branding, welcome message, suggestion buttons
**Researched:** 2026-03-15
**Confidence:** HIGH (verified against Streamlit docs and community reports)

---

## Critical Pitfalls

### Pitfall 1: st.set_page_config Not Called First

**What goes wrong:**
Adding `st.set_page_config()` (for page title, favicon, or layout) anywhere other than the very first line of the script raises `StreamlitAPIException: set_page_config() can only be called once per app, and must be called as the first Streamlit command in your script`. The app crashes immediately on load.

**Why it happens:**
Developers add `st.set_page_config()` after existing imports and `load_dotenv()` calls, or discover the call is missing and insert it mid-file near the other page setup code. Any `st.*` call before it — including inside imported modules — triggers the error.

**How to avoid:**
Place `st.set_page_config()` as the first Streamlit call, immediately after Python imports and before any other `st.*` call. In the current `app.py`, insert it directly after `load_dotenv()` and before `SYSTEM_PROMPT` or `@st.cache_resource`. Verify no imported module calls a Streamlit function at import time.

**Warning signs:**
- `StreamlitAPIException: set_page_config() can only be called once` in logs
- App shows blank white screen or crash page immediately on load
- Works locally after recent refactor but fails on Streamlit Cloud redeployment

**Phase to address:** Phase 1 (Header & Branding) — the moment `st.set_page_config` is introduced

---

### Pitfall 2: CSS Targeting Unstable Internal Streamlit Class Names

**What goes wrong:**
Streamlit generates internal CSS class names (e.g., `.css-1d391kg`, `.st-emotion-cache-xyz`) that change between Streamlit versions. CSS written against these class names silently breaks after a Streamlit version bump on Community Cloud, reverting the UI to unstyled defaults without any error.

**Why it happens:**
The official Streamlit API does not expose stable CSS class hooks for most elements. Developers inspect the browser DevTools and write CSS targeting the observed class names, which are implementation details and not part of the public API.

**How to avoid:**
Use only stable, element-level selectors (`[data-testid="stChatMessage"]`, `h1`, `h2`, `header`) or inject CSS via `st.markdown()` using broad semantic selectors. For the branding header, build the entire component in HTML/CSS injected via `st.markdown(unsafe_allow_html=True)` or `st.html()` so it is self-contained and does not depend on Streamlit's internal structure. Never target `.css-*` or `.st-emotion-cache-*` classes.

**Warning signs:**
- Branding looks correct locally but appears unstyled on Cloud
- Streamlit version in `requirements-app.txt` differs from local dev version
- CSS was written by inspecting browser DevTools (not official docs)

**Phase to address:** Phase 1 (Header & Branding) — establish the CSS approach before writing any selectors

---

### Pitfall 3: Welcome Message Redisplaying on Every Rerun

**What goes wrong:**
A welcome message rendered unconditionally (e.g., `st.info("Bienvenue...")` at the top of the script) reappears above the chat history on every user interaction because Streamlit reruns the entire script top-to-bottom on every event. The message appears both before and after the first question, creating a broken visual experience.

**Why it happens:**
Streamlit's execution model reruns the full script on every widget interaction. Without a session_state guard, code that "should only run once" runs on every rerun. The existing `messages` list check (`if len(st.session_state.messages) == 0`) already uses this pattern for buttons — the welcome message must follow the same logic.

**How to avoid:**
Wrap the welcome message render in the same condition already used for suggestion buttons:
```python
if len(st.session_state.messages) == 0:
    # render welcome message
    # render suggestion buttons
```
This is consistent with the existing app pattern and ensures both disappear together once the first message is sent.

**Warning signs:**
- Welcome message appears above the first assistant response after a question is asked
- Welcome message and chat history both visible simultaneously
- Message appears on page refresh even when `st.session_state.messages` is non-empty (if guard is wrong)

**Phase to address:** Phase 2 (Welcome Message) — enforce the session_state guard from the first line of welcome message code

---

### Pitfall 4: Suggestion Button State Corruption After Replacement

**What goes wrong:**
When replacing the existing two suggestion buttons with new recruiter-focused ones, the `pending_question` pattern breaks if button keys are not unique or if the `on_click` callback consumes the state before the question is processed. Symptom: clicking a suggestion button has no visible effect, or the wrong question is injected.

**Why it happens:**
The existing pattern (`inject_question` callback sets `pending_question`, which is read and cleared at render time) is correct but fragile. Two failure modes:
1. If the same question string appears in two buttons, Streamlit may deduplicate widget keys and the second button never fires.
2. If new buttons are added while `pending_question` is not properly initialized in `session_state`, the first click after a refresh raises `KeyError`.

**How to avoid:**
Ensure `pending_question` initialization remains in the session_state block at the top of the script. Give each button a unique `key=` parameter even if the label differs (e.g., `key="suggestion_1"`, `key="suggestion_2"`). When updating suggestion text, update both the `label` and the `args` passed to `inject_question` — never just the label.

**Warning signs:**
- Clicking a suggestion button does nothing (no rerun, no question injected)
- First click after page refresh fails, second click works
- Two buttons with near-identical labels share the same key implicitly

**Phase to address:** Phase 3 (Suggestion Buttons) — validate each button triggers the correct question in isolation before testing the full flow

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcoded hex colors in injected CSS | Quick visual result | Colors diverge from `config.toml` theme, manual sync required on theme changes | Acceptable for v1.1 since no custom theme is configured |
| `unsafe_allow_html=True` on `st.markdown` for CSS injection | No additional API needed | Flag warns it may be removed; `st.html()` is the forward-compatible API | Acceptable short-term; migrate to `st.html()` if available in installed version |
| Welcome message inside same `if messages == 0` block as buttons | Reuses existing pattern | Tightly couples welcome visibility to message count — cannot show welcome after reset | Never a problem for this app's use case |
| Inline `<style>` tag in `st.markdown` | Simple to write | Style applies globally to the page, not scoped — can affect Streamlit's own UI elements | Use only when scoping to a specific custom container |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| `st.markdown` with HTML | Using it for CSS injection alongside markdown text — the two interact unexpectedly since Streamlit 1.46.0, breaking inline code formatting | Use `st.markdown()` exclusively for CSS `<style>` blocks (no markdown text in same call), or use `st.html()` for pure HTML/CSS |
| `st.set_page_config` + `load_dotenv` | Calling `load_dotenv()` before `st.set_page_config()` — technically safe since `load_dotenv` is not a Streamlit call, but the pattern invites accidentally inserting an `st.*` call between them | Keep `st.set_page_config()` as line 1 after imports, explicitly before `load_dotenv()` |
| Streamlit Community Cloud + CSS files | Trying to load an external `.css` file via `open()` — filesystem paths differ on Cloud | Inject CSS inline via `st.markdown()` or `st.html()`, never via file read |
| Dark/light theme + hardcoded CSS colors | `prefers-color-scheme` CSS media query tracks the OS theme, not Streamlit's theme toggle — users who set Streamlit to dark mode but OS to light will see wrong colors | Use Streamlit CSS variables (`var(--text-color)`, `var(--background-color)`) or test in both Streamlit light and dark modes |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Large inline CSS string reprocessed on every rerun | Barely noticeable at small scale; accumulates with complex CSS | For v1.1, the CSS block is small — not a concern | Not a real threshold for this app's expected traffic |
| Welcome message triggering expensive computation | N/A for a static message | Keep welcome message as pure HTML/markdown — no API calls, no vectorstore access | Never, as long as welcome is static text |

---

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Injecting user-controlled content inside `st.markdown(unsafe_allow_html=True)` | XSS — user input rendered as HTML could execute scripts | The welcome message and header are static strings authored by the developer, not user input — safe. Never pass `st.session_state` values or chat input into an `unsafe_allow_html` block |
| Using `st.html()` with `unsafe_allow_javascript=True` | JavaScript execution in user's browser | Not needed for branding — use only HTML/CSS, never JavaScript in this context |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Welcome message that restates what the app title already says | Redundant, feels like filler — reduces trust | Welcome message should add information the title does not: what specifically can be asked, what the chatbot knows, what its limitations are |
| Suggestion buttons worded as instructions ("Cliquez pour savoir...") rather than actual questions | User has to mentally decode the button before clicking | Write buttons as literal questions the user would ask: "Quels sont vos domaines d'expertise ?" |
| Header too tall — pushes chat interface below the fold | Recruiter's first impression is a banner, not the chat | Limit header to 2-3 lines; use compact styling. Test on 1080p viewport |
| Generic suggestions not updated from v1.0 defaults | Recruiter sees generic "Quelles sont vos principales compétences ?" — not targeted | Suggestions must directly address recruiter concerns: availability, rates, tech stack, past projects |

---

## "Looks Done But Isn't" Checklist

- [ ] **Header:** Verify `st.set_page_config` is placed before all other `st.*` calls — not just visually first in the file but before any function that calls `st.*` implicitly
- [ ] **CSS injection:** Verify the injected CSS does not use `.css-*` or `.st-emotion-cache-*` class names — check by upgrading Streamlit locally and refreshing
- [ ] **Welcome message:** Verify the message disappears after the first question is submitted — test by asking a question and checking it is gone
- [ ] **Welcome message:** Verify the message does not reappear on page refresh when chat history exists in session_state
- [ ] **Suggestion buttons:** Verify each button injects the correct question (not a shared/wrong question) by testing each button independently in a fresh session
- [ ] **Suggestion buttons:** Verify buttons do not appear after the first message is sent (existing `messages == 0` guard still works after refactor)
- [ ] **Cloud deploy:** Test the deployed app at https://etirouthierappio.streamlit.app/ — CSS that works locally may not load on first visit on Cloud due to browser cache on the old version

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| `set_page_config` ordering error | LOW | Move `st.set_page_config()` to line 1 after imports, redeploy — 5 minute fix |
| CSS targeting unstable class names breaks after Streamlit upgrade | MEDIUM | Rewrite CSS using stable `data-testid` selectors or self-contained HTML containers; retest both light/dark modes |
| Welcome message reappears in chat | LOW | Add `if len(st.session_state.messages) == 0:` guard around the welcome message render |
| Suggestion button injects wrong question | LOW | Verify `args` tuple in `st.button(on_click=inject_question, args=(correct_question,))` matches the displayed label |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| `st.set_page_config` ordering | Phase 1 (Header & Branding) | App loads without `StreamlitAPIException` on first line |
| Unstable CSS class names | Phase 1 (Header & Branding) | CSS selectors reviewed — no `.css-*` or `.st-emotion-cache-*` in file |
| Welcome message redisplay | Phase 2 (Welcome Message) | Ask a question, verify welcome message is gone; refresh with messages, verify still gone |
| Suggestion button state corruption | Phase 3 (Suggestion Buttons) | Click each new button in isolation in a fresh browser tab, verify correct question is sent |
| Cloud-local CSS discrepancy | After any phase touching CSS | Verify on live https://etirouthierappio.streamlit.app/ after each deploy, not just locally |

---

## Sources

- Streamlit discuss: [set_page_config() can only be called once](https://discuss.streamlit.io/t/streamlitapiexception-set-page-config-can-only-be-called-once-per-app-error/38057)
- Streamlit discuss: [CSS class names are not consistent from one pageload to the next](https://discuss.streamlit.io/t/stremlits-dynamically-named-css-classes/1821)
- Streamlit docs: [Button behavior and examples](https://docs.streamlit.io/develop/concepts/design/buttons)
- Streamlit docs: [Session State](https://docs.streamlit.io/library/api-reference/session-state)
- GitHub issue: [Button's on_click callback fired on every re-run](https://github.com/streamlit/streamlit/issues/4595)
- GitHub issue: [Markdown inline code block broken with unsafe_allow_html since 1.46.0](https://github.com/streamlit/streamlit/issues/11888)
- Streamlit discuss: [CSS not loaded on startup but on reload](https://discuss.streamlit.io/t/css-not-loaded-on-startup-but-on-reload/72407)
- Streamlit discuss: [Button created within st.chat_message disappears after clicked](https://discuss.streamlit.io/t/button-created-within-st-chat-message-disappears-after-its-clicked/52591)
- GitHub issue: [prefers-color-scheme CSS misalignment with Streamlit theme](https://github.com/streamlit/streamlit/issues/6456)
- Streamlit docs: [2025 release notes](https://docs.streamlit.io/develop/quick-reference/release-notes/2025)

---

*Pitfalls research for: Streamlit UX Polish — v1.1 branding header, welcome message, suggestion buttons*
*Researched: 2026-03-15*
