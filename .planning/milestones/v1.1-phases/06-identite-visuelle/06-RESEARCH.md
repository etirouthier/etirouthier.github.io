# Phase 6: Identité Visuelle — Research

**Researched:** 2026-03-15
**Domain:** Streamlit UI — HTML/CSS branding header, welcome message, dark/light theme compatibility
**Confidence:** HIGH

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| BRAND-01 | L'utilisateur voit un header avec le nom et le titre freelance d'Étienne en haut de page | Verified: `st.markdown(HEADER_HTML, unsafe_allow_html=True)` is the correct and only reliable approach for custom HTML headers in Streamlit 1.55.0. `st.html` strips `<style>` blocks via DOMPurify. Self-contained inline styles on semantic elements are immune to Streamlit internal CSS class churn. |
| ACCU-01 | L'utilisateur voit un message d'accueil expliquant ce que le chatbot peut faire au premier chargement | Verified: `st.chat_message("assistant")` inside the existing `if len(st.session_state.messages) == 0:` guard is the exact pattern. The guard already gates the 4 suggestion chips — adding the welcome bubble as the first statement in that block requires zero structural change. |
</phase_requirements>

---

## Summary

Phase 6 implements two remaining v1.1 requirements on a production app (Streamlit 1.55.0 at https://etirouthierappio.streamlit.app/). Phase 5 is already complete: `st.set_page_config` is at line 11, the 4 recruiter suggestion chips with `SUGGESTIONS` constant are at lines 54–71, and `config.toml` has `buttonRadius = "full"`. The current `app.py` is 112 lines.

This phase adds exactly two new UI elements. First, the HTML branding header replaces the existing `st.title("Assistant — Dossier de Compétences")` at line 47 with a `st.markdown(HEADER_HTML, unsafe_allow_html=True)` call that renders "Etienne Routhier" as an H1 and "Consultant Freelance — Data & IA" as a styled subtitle. Second, a welcome message is inserted as an `st.chat_message("assistant")` block at the start of the existing `if len(st.session_state.messages) == 0:` guard at line 62, making it visible only on first load and invisible after the first message is sent.

No new dependencies are required. No file is created or deleted. The only risk of moderate complexity is ensuring the header subtitle color is legible in both Streamlit light and dark themes — the known gap identified in STATE.md. The prevention strategy (CSS variables or theme-neutral color choice) is documented below. The welcome message is zero-risk: it reuses the `st.chat_message` pattern already in production throughout the chat history rendering loop.

**Primary recommendation:** Replace `st.title` with an isolated `st.markdown(HEADER_HTML, unsafe_allow_html=True)` call using inline styles on semantic HTML only, then insert a `st.chat_message("assistant")` welcome block as the first statement in the `messages == 0` guard. Deploy and validate both elements in light and dark theme on the live URL before marking phase done.

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| streamlit | 1.55.0 (pinned in requirements-app.txt) | All UI rendering, HTML injection, chat messages | Already in production — no upgrade needed |

### Supporting

No new packages needed for this phase. Zero new dependencies.

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `st.markdown(html, unsafe_allow_html=True)` for the header | `st.html(html)` | `st.html` strips all `<style>` tags via DOMPurify as of Streamlit 1.38+. `st.markdown` with `unsafe_allow_html=True` is the only path that preserves inline styles and embedded CSS blocks. |
| Inline styles on semantic HTML elements (`<h1 style="...">`) | CSS targeting `.css-*` or `.st-emotion-cache-*` internal classes | Inline styles on `<h1>`, `<p>`, `<div>` are immune to Streamlit version bumps. Internal class names change on every Community Cloud deploy that bumps Streamlit. |
| `st.chat_message("assistant")` for the welcome bubble | `st.info(...)` or `st.markdown(...)` box | `st.chat_message` renders the assistant avatar and matches the chat history visual pattern exactly. Using a different component creates a visual discontinuity between the welcome message and the conversation. |

**Installation:**

No new packages. Stack is frozen.

---

## Architecture Patterns

### Current File Structure (Phase 5 post-state)

```
app.py                          # 112 lines — both changes land here
.streamlit/
    secrets.toml                # Not modified
    config.toml                 # Exists: [theme] buttonRadius = "full" — not modified
config.py                       # Not modified
requirements-app.txt            # Not modified
```

### Pattern 1: HTML Branding Header

**What:** Replace `st.title(...)` at line 47 with an isolated `st.markdown(HEADER_HTML, unsafe_allow_html=True)` call. Define `HEADER_HTML` as a module-level constant (similar to `SYSTEM_PROMPT` and `SUGGESTIONS` already in the file).

**When to use:** Any time custom typographic control beyond Streamlit's default title is needed.

**Current line to replace:**
```python
# line 47 — REMOVE this:
st.title("Assistant — Dossier de Compétences")
```

**Target pattern:**
```python
# Source: Streamlit official docs — st.markdown with unsafe_allow_html
HEADER_HTML = """
<div style="text-align: center; padding: 1rem 0 0.5rem 0;">
    <h1 style="margin: 0; font-size: 1.8rem; font-weight: 700;">Etienne Routhier</h1>
    <p style="margin: 0.25rem 0 0 0; font-size: 1rem; color: var(--text-color); opacity: 0.65;">
        Consultant Freelance — Data &amp; IA
    </p>
</div>
"""

# Isolated call — never combine with other markdown content (Streamlit 1.46+ rendering bug)
st.markdown(HEADER_HTML, unsafe_allow_html=True)
```

**Dark mode compatibility:** Use `var(--text-color)` with `opacity` rather than a hardcoded hex like `#666`. Streamlit exposes `--text-color` as a CSS variable that resolves to the theme-correct text color in both light and dark modes. `opacity: 0.65` produces a visually muted subtitle in both themes without hardcoding a color value that can fail in dark mode.

**Critical:** This `st.markdown` call must be isolated — never concatenate `HEADER_HTML` with other markdown text in the same call. Since Streamlit 1.46.0, `st.markdown` with `unsafe_allow_html=True` renders inline code blocks incorrectly when the string contains both markdown and HTML (GitHub issue #11888).

### Pattern 2: Welcome Message in the messages == 0 Guard

**What:** Insert `st.chat_message("assistant")` as the first statement inside the existing `if len(st.session_state.messages) == 0:` block at line 62. The guard already exists and gates the 4 suggestion chips — no structural change is needed.

**When to use:** First load only, and only until the user sends their first message. This behavior is automatic: once `messages` is non-empty, the guard evaluates to False and neither the welcome bubble nor the chips render.

**Current structure (lines 62–71):**
```python
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

**Target structure — welcome message inserted first:**
```python
# Source: Streamlit docs — st.chat_message
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        st.markdown(
            "Bonjour ! Je suis l'assistant d'Etienne Routhier. "
            "Je peux répondre à toutes vos questions sur son profil professionnel, "
            "ses compétences techniques, ses missions passées et ses disponibilités — "
            "uniquement à partir de son dossier de compétences. "
            "Posez votre question ou choisissez une suggestion ci-dessous."
        )
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

**Welcome message content requirements (from ACCU-01 success criteria):**
- Must explain what the chatbot can do (answer questions about the profile)
- Must implicitly define scope/limitations (only from the dossier de compétences)
- Must NOT restate the page title (no "Je suis Etienne Routhier" — that is the header's job)
- Must disappear after first message — this is guaranteed by the guard, not by additional logic

### Anti-Patterns to Avoid

- **`st.html` for the header:** Strips `<style>` tags. Has no effect on embedded CSS. Only `st.markdown(unsafe_allow_html=True)` preserves inline styles.
- **Hardcoded `color: #666` for the subtitle:** Invisible or very low contrast in Streamlit dark mode. Use `var(--text-color)` with `opacity` instead.
- **Mixing `HEADER_HTML` into a larger `st.markdown` call:** Triggers the Streamlit 1.46+ inline code rendering bug. Keep it in its own isolated call.
- **Welcome message placed outside the `messages == 0` guard:** It re-renders above every chat turn on every Streamlit rerun. Must be inside the guard.
- **Welcome message placed after the chips in the guard:** The chips appear before the welcome message visually. Insert the `st.chat_message` block first so the welcome bubble renders above the chips.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Theme-aware subtitle color | Hardcoded light/dark hex values with `st.get_option("theme.base")` | `var(--text-color)` CSS variable with `opacity` | Streamlit exposes CSS variables for theme colors; querying theme at runtime adds complexity and lag with no benefit |
| Welcome message visibility toggle | Manual session state flag (`welcome_shown`) | Existing `messages == 0` guard | The guard already provides this behavior; adding a second session state variable creates redundant state that can diverge |
| Custom "chat bubble" HTML/CSS for the welcome message | Bespoke HTML mimicking Streamlit's chat bubbles | `st.chat_message("assistant")` | Streamlit's built-in component auto-adapts to light/dark theme and matches the visual language of the conversation history |

**Key insight:** Both features are additive: the header replaces one existing line, and the welcome message is one new block inserted into an existing guard. Neither requires new state, new helpers, nor new file structure.

---

## Common Pitfalls

### Pitfall 1: Hardcoded Subtitle Color Fails in Dark Mode

**What goes wrong:** The subtitle "Consultant Freelance — Data & IA" renders as near-invisible in Streamlit dark mode. Symptom: visitor on dark theme sees the name but not the title, creating an incomplete first impression.

**Why it happens:** A color like `#666` or `#888` is designed against a light background (~250 brightness). Streamlit dark mode uses a dark background (~15 brightness); `#666` on that background passes WCAG contrast checks but `#888` and lighter values do not. The browser's `prefers-color-scheme` CSS feature does not synchronize with Streamlit's theme toggle (GitHub issue #6456).

**How to avoid:** Use `var(--text-color)` with `opacity: 0.65` instead of any hardcoded hex. This resolves to the correct themed text color in both modes. Validate visually on the live URL by toggling Settings > Theme in the Streamlit menu.

**Warning signs:** After deploy, open the app, toggle to dark mode in Streamlit settings, and check if the subtitle is legible.

### Pitfall 2: st.markdown with unsafe_allow_html Mixing HTML and Markdown

**What goes wrong:** If `HEADER_HTML` is concatenated with other markdown content in the same `st.markdown` call, inline code blocks elsewhere in the string render with broken formatting.

**Why it happens:** Streamlit 1.46.0 introduced a change in how `st.markdown` processes mixed HTML+markdown content (GitHub issue #11888). The rendering pipeline treats the entire string differently when `unsafe_allow_html=True` and markdown syntax coexists with raw HTML tags.

**How to avoid:** Use a dedicated, isolated `st.markdown(HEADER_HTML, unsafe_allow_html=True)` call for the header. Never append other markdown text to `HEADER_HTML`.

**Warning signs:** Code snippets or backtick-wrapped text elsewhere on the page renders incorrectly after adding the HTML header.

### Pitfall 3: Welcome Message Inserted After the Chips Visually

**What goes wrong:** The chips appear above the welcome message, meaning the visitor reads the action buttons before understanding what the chatbot is. The welcome message loses its contextual function.

**Why it happens:** Streamlit renders elements in the order they appear in the script. If the `cols = st.columns(4)` loop comes before the `st.chat_message` block, the chips render first.

**How to avoid:** Insert the `with st.chat_message("assistant"):` block as the very first statement inside the `messages == 0` guard, before `cols = st.columns(4)`.

**Warning signs:** On first load, chips are visible above the welcome bubble.

### Pitfall 4: HTML Entity Not Escaped in Header

**What goes wrong:** "Data & IA" renders as "Data " if the ampersand is not HTML-escaped. Some browsers may strip or misparse an unescaped `&` in an HTML string passed through `st.markdown`.

**Why it happens:** In HTML, `&` must be written as `&amp;` inside element content. The Python string `"Data & IA"` works in plain text but not inside an HTML block.

**How to avoid:** Write `Data &amp; IA` in `HEADER_HTML`. This is the only HTML entity needed.

**Warning signs:** The subtitle reads "Data  IA" (with extra space or missing character) on the live page.

---

## Code Examples

Verified patterns from official sources and direct codebase inspection:

### HEADER_HTML Constant (correct placement in app.py)

```python
# Source: Streamlit official docs — st.markdown with unsafe_allow_html
# Place after SUGGESTIONS constant, before vectorstore = load_vectorstore()

HEADER_HTML = """
<div style="text-align: center; padding: 1rem 0 0.5rem 0;">
    <h1 style="margin: 0; font-size: 1.8rem; font-weight: 700;">Etienne Routhier</h1>
    <p style="margin: 0.25rem 0 0 0; font-size: 1rem;
              color: var(--text-color); opacity: 0.65;">
        Consultant Freelance — Data &amp; IA
    </p>
</div>
"""
```

### Replace st.title with Isolated st.markdown

```python
# REMOVE: st.title("Assistant — Dossier de Compétences")
# ADD (isolated call — not combined with other markdown):
st.markdown(HEADER_HTML, unsafe_allow_html=True)
```

### Welcome Message in the messages == 0 Guard

```python
# Source: Streamlit docs — st.chat_message
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant"):
        st.markdown(
            "Bonjour ! Je suis l'assistant d'Etienne Routhier, "
            "consultant freelance Data & IA. "
            "Je peux répondre à vos questions sur ses compétences techniques, "
            "ses missions passées et ses disponibilités, "
            "à partir de son dossier de compétences. "
            "Posez votre question ou choisissez une suggestion ci-dessous."
        )
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

### Expected app.py Structure After Phase 6 (key lines)

```
line 1-9:   imports + load_dotenv()
line 11-15: st.set_page_config(...)                   ← Phase 5
line 17-23: SYSTEM_PROMPT = ...
line 25-32: HEADER_HTML = ...                          ← Phase 6 NEW constant
line 34-38: SUGGESTIONS = [...]                        ← Phase 5
line 40-44: @st.cache_resource load_vectorstore()
line 46-50: session state init
line 52-53: inject_question()
line 55:    vectorstore = load_vectorstore()
line 57:    st.markdown(HEADER_HTML, ...)              ← Phase 6 REPLACES st.title
line 59-62: chat history loop
line 64-73: if messages == 0:                          ← Phase 6 inserts welcome bubble first
                st.chat_message("assistant") welcome
                cols = st.columns(4) chips...
line 75+:   chat input + RAG pipeline (unchanged)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `st.title("Assistant — Dossier de Compétences")` | `st.markdown(HEADER_HTML, unsafe_allow_html=True)` with name + subtitle | Phase 6 | Visitor immediately sees who the chatbot represents; professional identity established before reading content |
| No welcome message | `st.chat_message("assistant")` welcome bubble on first load | Phase 6 | Removes "what is this?" ambiguity; scopes the chatbot for cold visitors; disappears cleanly after first use |

**Deprecated/outdated:**
- `st.title()` for the main header: Replaced by the HTML header in this phase. The Streamlit default title style gives no control over font weight, size hierarchy, or subtitle positioning.
- `st.html()` for custom HTML blocks: Do not use — strips `<style>` tags. `st.markdown(unsafe_allow_html=True)` is the correct path.

---

## Open Questions

1. **Exact welcome message copy**
   - What we know: The message must cover: purpose (answer questions about the profile), scope (only from the dossier de compétences), action prompt (choose a suggestion or type a question). Must NOT restate the header (no "Je suis Etienne Routhier" — that is the header's job).
   - What's unclear: Final French phrasing — tone calibration, sentence length, whether to acknowledge chatbot limitations explicitly ("je ne suis pas Etienne en personne") or implicitly via scope.
   - Recommendation: The example in Code Examples above is a working default. Adjustable at implementation time without structural change.

2. **Header font size / visual balance with existing chat content**
   - What we know: Streamlit's default `st.title` renders at ~2rem with the page's default font. The proposed H1 at 1.8rem is slightly smaller to avoid competing visually with message content.
   - What's unclear: Whether the centered layout looks balanced at 1080p and mobile after replacing the left-aligned `st.title`. Depends on content width with `layout="centered"` (already set in Phase 5).
   - Recommendation: Implement and validate on the live URL. Adjust font size or padding values at implementation time — these are aesthetic constants, not structural decisions.

3. **Dark mode validation procedure**
   - What we know: The `var(--text-color)` CSS variable strategy is the correct prevention. The live URL must be tested in both themes.
   - What's unclear: Whether Streamlit 1.55.0 on Community Cloud exposes `--text-color` reliably (confirmed in official Streamlit theming docs, HIGH confidence), but real-device testing is the only definitive check.
   - Recommendation: After deploy, open Settings gear in the Streamlit app, switch to dark theme, verify subtitle legibility. If `var(--text-color)` does not resolve correctly (LOW probability given docs confirmation), fall back to `color: inherit` with `opacity: 0.65`.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None — no pytest.ini, no test/ directory (same as Phase 5) |
| Config file | None |
| Quick run command | `streamlit run app.py --server.headless true` (smoke: no crash on startup) |
| Full suite command | Manual: open https://etirouthierappio.streamlit.app/, verify header + welcome message in both themes |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| BRAND-01 | Header displays "Etienne Routhier" + "Consultant Freelance — Data & IA" at top of page; legible in light and dark theme | manual-visual | `streamlit run app.py` — verifies no crash; visual inspection required for theme check | ❌ Wave 0 |
| ACCU-01 | Welcome message visible on first load; disappears after first message sent; does not reappear on subsequent interactions | manual-smoke | `streamlit run app.py` — verify no crash on startup | ❌ Wave 0 |

**Manual-only justification:** Streamlit UI rendering, HTML injection, and visual theme behavior require a running browser session. No headless testing framework is present or needed at this project scale.

### Sampling Rate

- **Per task commit:** `python -c "import ast; ast.parse(open('app.py').read()); print('syntax OK')"` — verifies no Python syntax errors without triggering Streamlit runtime
- **Per wave merge:** `streamlit run app.py` locally, verify header renders and welcome message appears/disappears correctly
- **Phase gate:** Header visible + correct text, welcome message visible on first load, welcome message absent after first question, both elements legible in dark theme — before marking phase done

### Wave 0 Gaps

- [ ] No automated test infrastructure exists or is needed — manual validation on the live URL is the appropriate strategy for a single-file Streamlit visual app

*(No automated test files to create — same baseline as Phase 5)*

---

## Sources

### Primary (HIGH confidence)

- Streamlit official docs — `st.markdown` with `unsafe_allow_html`, `st.chat_message`, `st.html` (DOMPurify behavior), CSS variables in theming
- Streamlit 2025–2026 release notes — `st.html` DOMPurify behavior confirmed in 1.38+ release notes; `unsafe_allow_html` HTML+markdown mixing issue in 1.46 release notes
- Direct inspection of `/workspaces/etienne.routhier/app.py` (112 lines, Phase 5 complete) — ground truth on exact lines to modify, current structure, and session state shape
- `.planning/research/SUMMARY.md` — milestone-level research confirming all patterns with HIGH confidence

### Secondary (MEDIUM confidence)

- STATE.md accumulated decisions — confirms `color: #666` dark mode concern as a known project blocker; confirms header grouped with welcome message for Phase 6
- Phase 5 RESEARCH.md — confirmed working `inject_question` pattern, `SUGGESTIONS` constant, `messages == 0` guard — Phase 6 builds directly on these

### Tertiary (LOW confidence — awareness only)

- GitHub `streamlit/streamlit#11888` — `unsafe_allow_html` inline code rendering bug since 1.46 (motivates the isolated `st.markdown` call pattern)
- GitHub `streamlit/streamlit#6456` — `prefers-color-scheme` CSS misalignment with Streamlit theme toggle (motivates `var(--text-color)` over hardcoded hex colors)

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new packages; all APIs verified in production version
- Architecture: HIGH — exact insertion points and replacement lines identified from direct code inspection of Phase 5 output
- Pitfalls: HIGH — each pitfall backed by official docs or confirmed GitHub issues, with specific prevention strategy
- Welcome message copy: MEDIUM — structure is locked, exact French phrasing is an implementation decision

**Research date:** 2026-03-15
**Valid until:** 2026-06-15 (stable Streamlit APIs; CSS variable behavior versioned)
