# Feature Landscape: RAG Chatbot CV Portfolio

**Domain:** RAG chatbot portfolio/CV app (showcase professionnel)
**Researched:** 2026-03-13
**Confidence:** MEDIUM

---

## Table Stakes

Fonctionnalités attendues — leur absence casse l'expérience.

| Feature | Pourquoi attendu | Complexité | Notes |
|---------|-----------------|------------|-------|
| Réponses basées sur le contenu du PDF | Promesse core du produit | Haute | FAISS + appel Mistral avec chunks récupérés |
| Réponses en français | Attente de l'audience B2B | Faible | Enforced via system prompt |
| Champ de saisie conversationnel | Primitive UI de base | Faible | `st.chat_input` |
| Historique de la conversation visible | L'utilisateur doit voir l'échange | Faible | `st.chat_message` + session state |
| Questions de démarrage suggérées | Réduit l'angoisse de la page blanche | Faible | Boutons affichés au premier message |
| Fallback gracieux hors-scope | Ne pas halluciner sur des questions sans réponse dans le doc | Moyen | System prompt — "je ne trouve pas cette info dans le document" |
| App publique sans login | Les clients potentiels ne créeront pas de compte | Nul | Décision déjà prise |

---

## Différenciateurs

Fonctionnalités mémorables, non attendues.

| Feature | Valeur | Complexité | Notes |
|---------|--------|------------|-------|
| Suivi multi-tour | "Dis-m'en plus sur ce projet" sans reformuler | Moyen | Passer l'historique dans le prompt Mistral |
| Ton persona-consistent | Les réponses sonnent comme le professionnel, pas comme un AI générique | Faible-Moyen | System prompt engineering — définir la voix |
| Réponse rapide (< 3s) | Les chatbots lents paraissent cassés | Moyen | Minimiser le nombre de chunks passés au modèle |
| "Je ne sais pas" honnête | Plus de confiance qu'un AI qui invente | Faible | System prompt uniquement |
| Layout mobile-friendly | Le client peut visiter depuis son téléphone | Faible | Streamlit est responsive par défaut |

---

## Anti-Features

À explicitement ne PAS construire.

| Anti-Feature | Pourquoi éviter | Alternative |
|--------------|----------------|-------------|
| Affichage des sources/extraits | Décision explicite dans PROJECT.md — ajoute du bruit pour l'audience B2B | Récupération silencieuse |
| Authentification | Tue la conversion — un client qui voit un login repart | App publique |
| Multi-langue | Double la complexité du prompt et des tests | Français uniquement, un seul system prompt |
| Rebuild FAISS automatique | Complexité infra pour un PDF qui change rarement | Script manuel |
| Historique persistant cross-sessions | Requiert une BDD, crée des problèmes de privacy | Session-scoped uniquement (défaut Streamlit) |
| Viewer PDF intégré | La page HTML existante le fait déjà | Garder la page HTML comme "option PDF brut" |
| Streaming token | Complexité supplémentaire, Mistral free tier moins fiable en streaming | Réponse complète, puis affichage |

---

## Dépendances entre features

```
Index FAISS buildé depuis le PDF
  → Récupération RAG au moment de la query
    → Appel Mistral avec chunks récupérés
      → Réponse affichée dans le chat UI
        → Historique conversation (suivi multi-tour)

Questions suggérées
  → Affichées uniquement au premier chargement (session state: aucun message)
  → Chaque clic pré-remplit st.chat_input → déclenche le même pipeline
```

**Risque clé :** Si l'index FAISS n'est pas présent au démarrage sur Streamlit Community Cloud, l'app plante entièrement. L'index doit être commité dans le repo.

---

## Recommandation MVP

**Priorité 1 (bloquant tout):**
1. Script build_index.py qui traite `dossier_competence.pdf`
2. Core RAG : charger index, accepter question, récupérer chunks, appeler Mistral, afficher réponse
3. Historique de conversation en session state

**Priorité 2 (polish):**
4. System prompt : langue FR, ton persona, fallback hors-scope
5. Questions suggérées au démarrage

**Différer:**
- Historique multi-tour passé au LLM (commencer sans, ajouter après)
- Fallback rebuild FAISS au démarrage

---

## Estimation de complexité

| Feature | Effort | Bloquant ? |
|---------|--------|-----------|
| Script build FAISS index | 2–4h | Oui |
| UI chat Streamlit basique | 1–2h | Oui |
| Intégration Mistral API avec contexte | 2–3h | Oui |
| System prompt FR + persona | 30min | Non (mais ratio valeur/effort excellent) |
| Fallback hors-scope | 1h | Non |
| Session state historique | 1h | Non |
| Questions suggérées | 1h | Non |
| Historique multi-tour passé au LLM | 2h | Non |

**Total MVP : 8–12h de travail focalisé**
