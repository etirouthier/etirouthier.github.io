# Roadmap: Chatbot CV — Dossier de Compétences

## Milestones

- ✅ **v1.0 MVP** — Phases 1-4 (shipped 2026-03-15)
- ✅ **v1.1 Polish & First Impression** — Phases 5-6 (shipped 2026-03-15)
- 🔄 **v1.2 Métadonnées d'expérience** — Phase 7 (in progress)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-4) — SHIPPED 2026-03-15</summary>

- [x] Phase 1: Setup & Configuration (1/1 plan) — completed 2026-03-13
- [x] Phase 2: Build de l'index FAISS (1/1 plan) — completed 2026-03-13
- [x] Phase 3: Application Streamlit complète (2/2 plans) — completed 2026-03-13
- [x] Phase 4: Déploiement (1/1 plan) — completed 2026-03-15

Full archive: `.planning/milestones/v1.0-ROADMAP.md`

</details>

<details>
<summary>✅ v1.1 Polish & First Impression (Phases 5-6) — SHIPPED 2026-03-15</summary>

- [x] Phase 5: Suggestions & Style (1/1 plan) — completed 2026-03-15
- [x] Phase 6: Identité Visuelle (1/1 plan) — completed 2026-03-15

Full archive: `.planning/milestones/v1.1-ROADMAP.md`

</details>

## v1.2 Métadonnées d'expérience

### Phase 7: Métadonnées & Contexte LLM

**Goal:** Enrichir les chunks FAISS avec le nom de l'expérience source et labelliser le contexte injecté dans le LLM pour éliminer les mélanges de missions dans les réponses.

**Requirements:** META-01, META-02, GEN-01, GEN-02

**Plans:** 1 plan

Plans:
- [ ] 07-01-PLAN.md — Enrichissement metadata EXPERIENCE_MAP + context LLM labellisé + rebuild index

**Success criteria:**
1. `build_index.py` ajoute `experience` dans `doc.metadata` pour chaque chunk
2. Un dict de mapping explicite `filename → nom` couvre les 8 sources (7 md + 1 PDF)
3. Le contexte envoyé au LLM affiche `[Decathlon]\n<chunk>` pour chaque extrait
4. Le prompt système mentionne que chaque extrait est labellisé par expérience
5. L'index rebuilté et commité reflète les nouvelles métadonnées

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Setup & Configuration | v1.0 | 1/1 | Complete | 2026-03-13 |
| 2. Build de l'index FAISS | v1.0 | 1/1 | Complete | 2026-03-13 |
| 3. Application Streamlit complète | v1.0 | 2/2 | Complete | 2026-03-13 |
| 4. Déploiement | v1.0 | 1/1 | Complete | 2026-03-15 |
| 5. Suggestions & Style | v1.1 | 1/1 | Complete | 2026-03-15 |
| 6. Identité Visuelle | v1.1 | 1/1 | Complete | 2026-03-15 |
| 7. Métadonnées & Contexte LLM | v1.2 | 0/1 | Pending | — |
