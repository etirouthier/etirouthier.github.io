# Requirements: Chatbot CV — Dossier de Compétences

**Defined:** 2026-03-16
**Core Value:** Un client potentiel peut poser n'importe quelle question sur le profil professionnel et obtenir une réponse précise et contextuelle directement depuis le document.

## v1.2 Requirements

### Indexation

- [ ] **META-01**: Chaque chunk possède un champ `experience` dans ses métadonnées, dérivé du nom de fichier source (ex: `01_decathlon.md` → `"Decathlon"`)
- [ ] **META-02**: Le mapping filename → nom d'expérience est défini explicitement dans `build_index.py` (pas d'inférence fragile sur le nom de fichier)

### Génération

- [ ] **GEN-01**: Le contexte injecté dans le LLM préfixe chaque chunk avec `[Expérience]` (ex: `[Decathlon]\n<texte du chunk>`)
- [ ] **GEN-02**: Le prompt système indique au LLM de mentionner l'expérience source dans ses réponses quand c'est pertinent

## Out of Scope

| Feature | Reason |
|---------|--------|
| Filtrage par expérience | Complexité supplémentaire, hors périmètre v1.2 |
| Métadonnées période/dates | Non demandé pour v1.2 |
| Affichage des sources dans l'UI | Déjà exclu en v1.0 — interface épurée |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| META-01 | Phase 7 | Pending |
| META-02 | Phase 7 | Pending |
| GEN-01 | Phase 7 | Pending |
| GEN-02 | Phase 7 | Pending |

**Coverage:**
- v1.2 requirements: 4 total
- Mapped to phases: 4
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-16*
*Last updated: 2026-03-16 after initial definition*
