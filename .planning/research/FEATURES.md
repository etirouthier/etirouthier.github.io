# Feature Research

**Domain:** Chatbot CV / portfolio interactif — ciblage recruteurs freelance, marché français
**Researched:** 2026-03-15
**Confidence:** HIGH (app existante inspectable + recherches marché confirmées par sources multiples)

---

## Context: Milestone Scope

This is a polish milestone on an existing working app. V1.0 shipped with:
- RAG chatbot fonctionnel (dossier_competence.pdf → Mistral API)
- 2 boutons de suggestions génériques au démarrage
- `st.title("Assistant — Dossier de Compétences")` comme seul élément d'en-tête
- Aucun message d'accueil explicite
- Aucune indication sur l'identité du candidat ou son positionnement

The three active requirements in PROJECT.md define the full scope for v1.1:
1. Header professionnel (nom, titre freelance)
2. Message d'accueil contextualisé
3. Suggestions recruteur freelance

Research below maps these to user expectations, complexity, and recruiter psychology.

---

## Feature Landscape

### Table Stakes (Recruteur s'attend à trouver ça)

Features that a recruiter/client visiting a candidate's chatbot CV in 2026 expects to exist.
Missing these = the app feels amateurish or confusing.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Nom du candidat visible immédiatement | Tout portfolio commence par une identité — le visiteur ne doit pas deviner qui il consulte | LOW | `st.markdown()` avec HTML suffit, pas de logique d'état |
| Titre professionnel et positionnement freelance | Le recruteur doit comprendre en 3 secondes ce que le candidat vend (ex: "Développeur Python · Freelance") | LOW | Texte statique dans le header |
| Explication de la nature de l'outil | Un chatbot inconnu peut dérouter — une phrase "Posez vos questions sur mon profil" lève l'ambiguïté | LOW | Message d'accueil avant la première interaction |
| Questions suggérées orientées recruteur | Le recruteur en découverte ne sait pas quoi demander — les suggestions l'aiguillent vers la valeur clé | LOW | Remplacement des 2 questions génériques actuelles par 4 questions recruteur-ciblées |
| Ton professionnel cohérent | Un chatbot CV qui répond de façon désinvolte casse la confiance | LOW | Déjà assuré par SYSTEM_PROMPT existant, rien à changer |

### Differentiators (Avantage compétitif pour ce type d'app)

Features that transform "yet another chatbot" into a memorable candidate presentation.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Suggestions qui révèlent la valeur métier (pas juste les skills) | Un recruteur freelance veut savoir "quels problèmes résout-il ?" — pas seulement "quelles technos connaît-il ?" | LOW | Choix de formulation des 4 suggestions : orienter vers problèmes résolus, livrables, disponibilité |
| Message d'accueil qui pose le contexte recrutement | Distingue "je lis un CV" de "je parle à un assistant IA qui me fait gagner du temps" — valeur perçue immédiate | LOW | Formulation soignée du message initial affiché dans la fenêtre de chat |
| Identité visuelle sobre mais distincte | Un header HTML/CSS propre sur fond Streamlit générique marque l'effort professionnel | MEDIUM | CSS inline via `st.markdown unsafe_allow_html` ; risque de régression sur mobile à tester |

### Anti-Features (Tentant mais problématique)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Retirer le footer/branding Streamlit | Paraît plus "professionnel" sans watermark | Impossible à supprimer proprement sur Streamlit Community Cloud — les CSS hacks ciblant `data-testid` cassent au moindre update de Streamlit | Investir le budget visuel dans le header custom, pas dans masquer le footer |
| Formulaire de contact intégré | Un recruteur qui aime le profil veut contacter directement | Streamlit ne persiste rien — pas de backend pour recevoir/stocker les messages ; intégration email (SendGrid, etc.) hors scope | Afficher l'adresse email ou le lien LinkedIn dans le header ou message d'accueil |
| Avatar ou photo du candidat | Humanise davantage | Images dans les headers custom nécessitent Base64 ou hébergement externe ; bénéfice marginal vs effort | Nom bien visible + titre clair suffisent |
| Suggestions contextuelles après chaque réponse | UX chatbot avancée | Nécessite de parser la réponse LLM pour générer des suggestions dynamiques — complexité de prompt engineering significative | Les 4 suggestions au démarrage couvrent le besoin de guidage initial |

---

## Recruiter Psychology: What They Actually Want to Know First

Based on research into the French freelance IT market (Free-Work, Silkhom) and portfolio chatbot UX analysis:

### Les 4 questions qu'un recruteur freelance pose mentalement dans les 60 premières secondes

1. **"Qui est-il / qu'est-ce qu'il fait ?"** — Identité + positionnement en un coup d'oeil (adressé par le header)
2. **"A-t-il les compétences techniques pour ma mission ?"** — Stack, niveau, années d'expérience
3. **"A-t-il déjà fait ça ?"** — Références concrètes, projets livrés, secteurs
4. **"Est-il disponible et à quel TJM ?"** — Informations pratiques pour engager le recrutement

### Mapping vers les suggestions à proposer

Les 4 boutons de suggestion v1.1 doivent adresser ces 4 besoins dans cet ordre de priorité :

| Suggestion recommandée | Question recruteur adressée | Pourquoi cette formulation |
|------------------------|----------------------------|---------------------------|
| "Quelles sont vos compétences techniques principales ?" | Stack / niveau | Directe, universelle, point d'entrée naturel |
| "Quels types de projets avez-vous réalisés ?" | Références / preuves | "Types de projets" est plus ouvert — invite à des réponses riches |
| "Sur quel type de mission pouvez-vous intervenir ?" | Adéquation besoin/profil | Cadre l'entretien depuis la perspective du recruteur |
| "Quelle est votre disponibilité ?" | Disponibilité / TJM | Signal d'intérêt concret — forte valeur de conversion |

Note: Si `dossier_competence.pdf` ne contient pas d'information sur le TJM ou la disponibilité, le chatbot répondra honnêtement qu'il ne dispose pas de cette information (comportement déjà géré par SYSTEM_PROMPT). La suggestion reste valide — elle aide le recruteur à savoir qu'il doit contacter directement pour ces points.

---

## Feature Dependencies

```
[Header professionnel]
    (aucune dépendance — HTML statique, premier appel dans le script)

[Message d'accueil]
    requires --> [len(messages) == 0 check]  (déjà en place dans app.py ligne 49)

[Suggestions recruteur]
    requires --> [Mêmes conditions que suggestions actuelles]  (déjà en place)
    enhances --> [Message d'accueil]  (les suggestions prolongent le message d'accueil)

[Header] enhances --> [Message d'accueil]
    (identité etablie dans le header rend le message d'accueil cohérent)
```

### Dependency Notes

- **Header sans dépendance :** Peut être implémenté en isolation avec `st.markdown(html, unsafe_allow_html=True)` avant toute logique de session state. `st.set_page_config()` doit être le premier appel Streamlit du script.
- **Message d'accueil extends existing pattern :** La condition `if len(st.session_state.messages) == 0` est déjà utilisée pour les boutons — le message s'intègre naturellement dans ce bloc.
- **Suggestions remplacent l'existant :** Les 2 boutons actuels sont remplacés par 4 boutons. Même mécanique `inject_question` / `on_click`. Passer de 2 colonnes à 4 colonnes ou 2x2.

---

## MVP Definition

### v1.1 Scope (c'est le milestone entier)

- [ ] Header professionnel — nom, titre, positionnement freelance — indispensable: premier point de contact, coût minimal, impact maximum sur la perception
- [ ] Message d'accueil contextualisé — explication de l'outil + invitation à interagir — indispensable: lève l'ambiguïté "qu'est-ce que c'est ?", nécessaire pour un visiteur froid
- [ ] 4 suggestions ciblées recruteur — remplacement des 2 questions génériques — indispensable: guide le recruteur vers la valeur, réduit la friction de démarrage

### Defer to v1.2+

- Informations de contact (email, LinkedIn) dans le header — utile mais nécessite décision sur ce qu'on expose publiquement
- Suggestions dynamiques post-réponse — complexité LLM hors scope
- Personnalisation thème Streamlit — non fiable sur Community Cloud

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Header professionnel (nom + titre) | HIGH | LOW | P1 |
| Message d'accueil | HIGH | LOW | P1 |
| 4 suggestions recruteur ciblées | HIGH | LOW | P1 |
| Lien contact dans header | MEDIUM | LOW | P2 |
| Suggestions post-réponse | MEDIUM | HIGH | P3 |
| Suppression branding Streamlit | LOW | HIGH | P3 (déconseillé) |

**Priority key:**
- P1: Must have for v1.1 launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

---

## Streamlit Implementation Constraints (Confidence: HIGH)

Verified via official Streamlit docs and community forums:

- `st.markdown(html, unsafe_allow_html=True)` — méthode principale pour HTML/CSS custom, fonctionne sur Community Cloud
- `st.set_page_config(page_title=..., page_icon=...)` — contrôle le titre de l'onglet et le favicon ; doit être le **premier appel Streamlit** dans le script (actuellement absent de app.py)
- CSS via `st.markdown` avec `<style>` tag — fonctionne mais les sélecteurs `data-testid` sont fragiles entre versions Streamlit
- Streamlit 1.55 (version du projet) : le paramètre `text_alignment` sur `st.markdown` n'est pas disponible (feature des versions 2025 ultérieures)
- Les `st.columns()` existants pour les boutons fonctionnent bien — passer à 4 boutons : soit 2 colonnes de 2, soit 4 colonnes d'1

---

## Sources

- [Personal Portfolio with AI-Powered Chatbot — Streamlit Community](https://discuss.streamlit.io/t/personal-portfolio-with-ai-powered-chatbot-lucy/73140) — MEDIUM confidence (thread communautaire)
- [Why Your 2026 Job Search Needs an Interactive Portfolio Chatbot — Knak Digital](https://knakdigital.com/job-seeker-advice/why-your-2026-job-search-needs-an-interactive-portfolio-chatbot/) — MEDIUM confidence (analyse marché)
- [30+ Chatbot Welcome Messages — FlowHunt](https://www.flowhunt.io/blog/30-chatbot-welcome-messages-to-make-a-great-first-impression/) — MEDIUM confidence (best practices généraux)
- [Chatbot Resume: Step-by-Step Tutorial — Landbot](https://landbot.io/blog/chatbot-resume) — MEDIUM confidence (UX patterns CV chatbot)
- [TJM freelance IT 2026 — Free-Work](https://www.free-work.com/fr/tech-it/blog/guide-du-freelance/freelance-it-comment-fixer-son-tjm-en-2026-sans-se-sous-evaluer) — HIGH confidence (marché freelance France)
- [Custom CSS Header Streamlit — Community](https://discuss.streamlit.io/t/custom-header-right-at-the-top-of-the-page-styled-with-custom-css/20612) — HIGH confidence (pattern technique confirmé)
- [st.markdown — Streamlit official docs](https://docs.streamlit.io/develop/api-reference/text/st.markdown) — HIGH confidence
- Inspection directe de `/workspaces/etienne.routhier/app.py` — HIGH confidence (source de vérité sur l'état actuel)

---

*Feature research for: Chatbot CV — v1.1 Polish & First Impression*
*Researched: 2026-03-15*
