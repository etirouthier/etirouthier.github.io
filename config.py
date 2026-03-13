# config.py
# Constantes partagées entre build_index.py et app.py
# IMPORTANT: Importer depuis ce module — ne jamais dupliquer ces valeurs dans d'autres scripts
# Toute divergence du modèle d'embedding entre build et query rend l'index inutilisable

# Modèle d'embedding — DOIT être identique entre build_index.py et app.py
# Si ces valeurs diffèrent, FAISS retourne des résultats silencieusement invalides
EMBEDDING_MODEL = "mistral-embed"

# Modèle de génération
LLM_MODEL = "mistral-small-latest"

# Paramètres de chunking (calibrés pour un document court et dense)
# Ajustable en Phase 2 selon qualité des chunks observée dans les logs
CHUNK_SIZE = 500       # caractères
CHUNK_OVERLAP = 50     # caractères — chevauchement pour continuité du contexte

# Nombre de chunks récupérés par requête
# Compromis précision/contexte pour Mistral free tier
K_RETRIEVED = 4

# Chemin de l'index FAISS (relatif à la racine du repo)
FAISS_INDEX_PATH = "faiss_index"
