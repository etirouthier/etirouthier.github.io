# build_index.py
# Script offline — à exécuter une fois pour construire l'index FAISS
# Prérequis : MISTRAL_API_KEY définie dans l'environnement
#   export MISTRAL_API_KEY=sk-...
# Usage : python build_index.py

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_mistralai import MistralAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP, FAISS_INDEX_PATH

# Charger .env si présent (dev local) — no-op si absent
load_dotenv()

# Étape 1 : Charger tous les PDFs depuis assets/
print("[1/4] Chargement des documents depuis assets/...")
loader = PyPDFDirectoryLoader("assets/", recursive=True)
raw_docs = loader.load()
if not raw_docs:
    raise ValueError("Aucun document trouvé dans assets/ — vérifier que le PDF est présent.")
print(f"[1/4] OK — {len(raw_docs)} page(s) chargée(s)")

# Étape 2 : Découper en chunks
print(f"[2/4] Découpage en chunks (taille={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
)
chunks = splitter.split_documents(raw_docs)
print(f"[2/4] OK — {len(chunks)} chunks générés")

# Étape 3 : Générer les embeddings et construire l'index FAISS
# MistralAIEmbeddings lit MISTRAL_API_KEY depuis l'environnement automatiquement
print(f"[3/4] Génération des embeddings ({EMBEDDING_MODEL}) et construction de l'index FAISS...")
print("      (appel API Mistral — ~20-30 secondes)")
embeddings = MistralAIEmbeddings(model=EMBEDDING_MODEL)
vectorstore = FAISS.from_documents(chunks, embeddings)
print(f"[3/4] OK — index FAISS construit ({len(chunks)} vecteurs)")

# Étape 4 : Sauvegarder l'index
print(f"[4/4] Sauvegarde de l'index dans {FAISS_INDEX_PATH}/...")
vectorstore.save_local(FAISS_INDEX_PATH)
print(f"[4/4] OK — fichiers créés : {FAISS_INDEX_PATH}/index.faiss, {FAISS_INDEX_PATH}/index.pkl")

# Logs de validation (INDEX-04) — lire attentivement avant de commiter l'index
print("\n=== Validation des chunks ===")
print(f"Nombre total de chunks : {len(chunks)}")
n_preview = min(3, len(chunks))
for i in range(n_preview):
    print(f"\n--- Chunk {i+1} ({len(chunks[i].page_content)} chars, source: {chunks[i].metadata.get('source', '?')}) ---")
    print(chunks[i].page_content[:200])

print("\n[IMPORTANT] Vérifier que les chunks ci-dessus sont lisibles et cohérents.")
print("[IMPORTANT] Si le texte semble mélangé ou illisible, NE PAS commiter l'index.")
print("[IMPORTANT] Index prêt à être commité : git add faiss_index/ && git commit -m 'feat(02): add FAISS index'")

# Note pour Phase 3 (app.py) :
# Charger l'index avec allow_dangerous_deserialization=True :
# vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
