---
phase: 05-suggestions-style
plan: "01"
subsystem: ui
tags: [streamlit, chips, pill-buttons, config-toml, set_page_config]

# Dependency graph
requires:
  - phase: 04-deploiement
    provides: App deployed on Streamlit Community Cloud at https://etirouthierappio.streamlit.app/
provides:
  - "4 recruiter suggestion chips visible on first load (stack, missions, TJM, fit)"
  - "Pill button style via .streamlit/config.toml buttonRadius = full"
  - "st.set_page_config with page title and icon, placed before @st.cache_resource"
affects:
  - 06-identite-visuelle

# Tech tracking
tech-stack:
  added: [".streamlit/config.toml (Streamlit theming)"]
  patterns: ["SUGGESTIONS constant with args=(question,) variable reference — no string duplication", "st.columns(4) loop with key=f'suggestion_{i}' for deduplication"]

key-files:
  created: [".streamlit/config.toml"]
  modified: ["app.py"]

key-decisions:
  - "st.set_page_config placed between load_dotenv() and SYSTEM_PROMPT — before @st.cache_resource decorator (Streamlit ordering constraint)"
  - "SUGGESTIONS constant as module-level list — single source of truth for label and args=(question,)"
  - "key=f'suggestion_{i}' mandatory on each button — prevents Streamlit deduplication bug on same render pass"
  - "buttonRadius = 'full' in [theme] section only — no other theme keys added (Phase 6 will add colors)"

patterns-established:
  - "Pattern 1: Streamlit button args pattern — args=(question,) references loop variable, never duplicates string literal"
  - "Pattern 2: config.toml committed to repo — only secrets.toml is git-ignored, not the full .streamlit/ directory"

requirements-completed: [ACCU-02, BRAND-02]

# Metrics
duration: multi-session
completed: 2026-03-15
---

# Phase 05 Plan 01: Suggestions & Style Summary

**4 pill-style recruiter chips (stack/missions/TJM/fit) added to app.py via st.columns(4) loop + .streamlit/config.toml with buttonRadius="full", deployed and verified live**

## Performance

- **Duration:** multi-session (2 executor sessions)
- **Started:** 2026-03-15
- **Completed:** 2026-03-15T17:13:09Z
- **Tasks:** 3 (2 auto + 1 checkpoint)
- **Files modified:** 2

## Accomplishments

- Added `st.set_page_config` with title "Etienne Routhier — Dossier de Competences" and briefcase icon, placed before `@st.cache_resource` to satisfy Streamlit ordering constraint
- Replaced 2-column chip layout with SUGGESTIONS constant + 4-column loop, each button referencing the same variable for label and args=(question,)
- Created `.streamlit/config.toml` with `buttonRadius = "full"` producing full pill-style rounded buttons; confirmed committed and not git-ignored
- Visual validation approved on live URL: 4 chips visible, pill style active, each chip triggers correct RAG question, browser tab shows correct title

## Task Commits

Each task was committed atomically:

1. **Task 1: Modifier app.py — set_page_config et 4 chips recruteur** - `60ef19a` (feat)
2. **Task 2: Creer .streamlit/config.toml — style pill buttons** - `951754d` (feat)
3. **Task 3: Validation visuelle sur l'URL live** - checkpoint approved (no code commit — visual verification only)

## Files Created/Modified

- `app.py` - Added st.set_page_config (line 11), SUGGESTIONS constant (line 54), 4-column chip loop replacing 2-column layout
- `.streamlit/config.toml` - Created with [theme] section, buttonRadius = "full"

## Decisions Made

- Used `key=f"suggestion_{i}"` on each button to prevent Streamlit deduplication of identical-label buttons in the same render pass
- Placed `st.set_page_config` between `load_dotenv()` and `SYSTEM_PROMPT` definition — this is the only safe position before the `@st.cache_resource` decorator
- Kept `config.toml` minimal (buttonRadius only) — colors deferred to Phase 6 to avoid scope creep

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 6 (Identite Visuelle) can proceed: `app.py` structure is stable, `.streamlit/config.toml` exists and is committed
- Phase 6 will add header HTML block and welcome message — two new UI blocks, higher risk than string/config changes
- Known concern: CSS `color: #666` for subtitle may be low-contrast in dark mode — validate visually after Phase 6 deploy

---
*Phase: 05-suggestions-style*
*Completed: 2026-03-15*
