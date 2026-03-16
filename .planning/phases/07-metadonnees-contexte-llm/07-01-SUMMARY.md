---
phase: 07-metadonnees-contexte-llm
plan: 01
subsystem: database
tags: [faiss, langchain, mistral, embeddings, metadata, rag]

# Dependency graph
requires:
  - phase: 06-identite-visuelle
    provides: app.py with working RAG pipeline and SYSTEM_PROMPT
provides:
  - EXPERIENCE_MAP dict in build_index.py enriching doc.metadata['experience'] per chunk
  - Labelled LLM context "[Expérience]\n<chunk>" format in app.py
  - SYSTEM_PROMPT instructing LLM to cite experience source
  - FAISS index rebuilt with experience metadata (pending Task 3 human rebuild)
affects: [llm-responses, rag-context, faiss-index]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Post-split metadata enrichment loop: iterate chunks after split_documents(), set doc.metadata['experience'] from EXPERIENCE_MAP dict keyed on basename"
    - "Labelled RAG context: f'[{experience}]\n{chunk}' prefix per retrieved doc"

key-files:
  created: []
  modified:
    - build_index.py
    - app.py

key-decisions:
  - "EXPERIENCE_MAP uses basename (not full path) as key — robust to different working directories"
  - "Fallback EXPERIENCE_MAP.get(basename, basename) uses basename itself when unmapped — avoids silent '?' failures"
  - "SYSTEM_PROMPT explicitly instructs LLM to mention source experience when relevant"

patterns-established:
  - "Metadata enrichment: apply post-split loop before FAISS.from_documents() to guarantee all chunks carry experience field"

requirements-completed: [META-01, META-02, GEN-01, GEN-02]

# Metrics
duration: 1min
completed: 2026-03-16
---

# Phase 7 Plan 01: Métadonnées & Contexte LLM Summary

**EXPERIENCE_MAP metadata enrichment in build_index.py + labelled `[Expérience]\n<chunk>` context assembly in app.py — FAISS rebuild pending human action**

## Performance

- **Duration:** 1 min
- **Started:** 2026-03-16T17:25:31Z
- **Completed:** 2026-03-16T17:26:37Z
- **Tasks:** 2/3 automated (Task 3 requires human rebuild with MISTRAL_API_KEY)
- **Files modified:** 2

## Accomplishments
- Added `EXPERIENCE_MAP` dict (8 keys: 7 md + 1 pdf) to `build_index.py` with post-split enrichment loop setting `doc.metadata['experience']` on every chunk
- Updated `app.py` context assembly to prefix each retrieved chunk with `[NomExpérience]` label
- Extended `SYSTEM_PROMPT` to inform LLM about per-extrait labelling and invite source citation

## Task Commits

Each task was committed atomically:

1. **Task 1: Ajouter EXPERIENCE_MAP et enrichissement metadata dans build_index.py** - `12758a2` (feat)
2. **Task 2: Mettre a jour app.py — context labellise et SYSTEM_PROMPT** - `76df3ed` (feat)
3. **Task 3: Rebuilter l'index FAISS** - pending (checkpoint:human-action — requires MISTRAL_API_KEY)

## Files Created/Modified
- `build_index.py` - Added EXPERIENCE_MAP dict, post-split enrichment loop, updated validation log line
- `app.py` - Updated SYSTEM_PROMPT with [NomExpérience] instructions, replaced context assembly with labelled f-string format

## Decisions Made
- EXPERIENCE_MAP uses `os.path.basename(source)` as key — works regardless of absolute path prefix stored by LangChain
- Fallback `EXPERIENCE_MAP.get(basename, basename)` avoids silent "?" — unmapped files show their filename so they're identifiable
- SYSTEM_PROMPT addition placed as final sentence to preserve existing prompt structure

## Deviations from Plan

None - plan executed exactly as written. `import os` was already present on line 7 so step 1 of Task 1 was a no-op.

## Issues Encountered

None.

## User Setup Required

**Task 3 requires manual FAISS rebuild.** Steps:

1. Ensure `MISTRAL_API_KEY` is set in the environment
2. Run `python build_index.py` from the project root
3. Validate logs: validation section must show `experience: Decathlon` (not `experience: 01_decathlon.md`)
4. Run pickle validation then commit:
```bash
python -c "
import pickle
data = pickle.load(open('faiss_index/index.pkl', 'rb'))
docs = list(data[0]._dict.values())
missing = [d.metadata.get('source') for d in docs if 'experience' not in d.metadata]
print('Missing experience:', missing or 'NONE')
experiences = sorted({d.metadata.get('experience') for d in docs})
print('Experiences presentes:', experiences)
"
git add faiss_index/index.faiss faiss_index/index.pkl
git commit -m "feat(07): rebuild FAISS index with experience metadata"
```

## Next Phase Readiness
- Code changes complete and syntactically valid (ast.parse verified)
- FAISS index rebuild required before full META-01 verification passes
- Once rebuilt: LLM will receive `[Decathlon]\n<chunk>\n\n[Veolia]\n<chunk>` context with 7-8 distinct experience labels

---
*Phase: 07-metadonnees-contexte-llm*
*Completed: 2026-03-16*
