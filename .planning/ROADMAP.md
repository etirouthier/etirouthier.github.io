# Roadmap: Chatbot CV — Dossier de Compétences

## Milestones

- ✅ **v1.0 MVP** — Phases 1-4 (shipped 2026-03-15)
- **v1.1 Polish & First Impression** — Phases 5-6 (current)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-4) — SHIPPED 2026-03-15</summary>

- [x] Phase 1: Setup & Configuration (1/1 plan) — completed 2026-03-13
- [x] Phase 2: Build de l'index FAISS (1/1 plan) — completed 2026-03-13
- [x] Phase 3: Application Streamlit complète (2/2 plans) — completed 2026-03-13
- [x] Phase 4: Déploiement (1/1 plan) — completed 2026-03-15

Full archive: `.planning/milestones/v1.0-ROADMAP.md`

</details>

### v1.1 Polish & First Impression

- [x] **Phase 5: Suggestions & Style** - Chips recruteur (4 questions), style pill, et page config (completed 2026-03-15)
- [x] **Phase 6: Identité Visuelle** - Message d'accueil et header professionnel (completed 2026-03-15)

## Phase Details

### Phase 5: Suggestions & Style
**Goal**: Un recruteur voit des suggestions ciblées et une interface aux boutons arrondis dès le premier chargement
**Depends on**: Phase 4 (app déployée)
**Requirements**: ACCU-02, BRAND-02
**Success Criteria** (what must be TRUE):
  1. Les 4 boutons de suggestion affichent des questions spécifiques recruteur (stack technique, types de missions, fit mission, disponibilité/TJM)
  2. Cliquer sur un bouton de suggestion déclenche le pipeline RAG avec la question correspondante
  3. Les boutons s'affichent avec un style pill (bords arrondis) via config.toml
  4. L'app se charge sans erreur (st.set_page_config en première position dans app.py)
**Plans**: 1 plan

Plans:
- [ ] 05-01-PLAN.md — Modifier app.py (set_page_config + 4 chips) et créer .streamlit/config.toml (pill buttons)

### Phase 6: Identité Visuelle
**Goal**: Un visiteur comprend immédiatement qui est Étienne et ce que le chatbot peut faire pour lui
**Depends on**: Phase 5
**Requirements**: ACCU-01, BRAND-01
**Success Criteria** (what must be TRUE):
  1. Le header affiche le nom "Etienne Routhier" et le titre "Consultant Freelance — Data & IA" en haut de page
  2. Un message d'accueil de l'assistant est visible au premier chargement, expliquant le périmètre du chatbot
  3. Le message d'accueil disparaît après l'envoi du premier message (ne réapparaît pas à chaque interaction)
  4. Le header est lisible en thème clair et en thème sombre
**Plans**: 1 plan

Plans:
- [ ] 06-01-PLAN.md — Modifier app.py (HEADER_HTML constant + st.markdown isolé + welcome bubble dans guard messages == 0)

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Setup & Configuration | v1.0 | 1/1 | Complete | 2026-03-13 |
| 2. Build de l'index FAISS | v1.0 | 1/1 | Complete | 2026-03-13 |
| 3. Application Streamlit complète | v1.0 | 2/2 | Complete | 2026-03-13 |
| 4. Déploiement | v1.0 | 1/1 | Complete | 2026-03-15 |
| 5. Suggestions & Style | v1.1 | 1/1 | Complete | 2026-03-15 |
| 6. Identité Visuelle | 1/1 | Complete   | 2026-03-15 | - |
