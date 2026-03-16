import streamlit as st
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from config import EMBEDDING_MODEL, LLM_MODEL, K_RETRIEVED, FAISS_INDEX_PATH

# Charger .env si présent (dev local) — no-op en production Streamlit Cloud
load_dotenv()

st.set_page_config(
    page_title="Etienne Routhier — Dossier de Compétences",
    page_icon="💼",
    layout="centered",
)

SYSTEM_PROMPT = (
    "Tu es un assistant professionnel qui répond aux questions sur le profil "
    "et les compétences d'Etienne Routhier, basé uniquement sur les documents fournis.\n"
    "Tu réponds toujours en français, avec un ton professionnel et bienveillant.\n"
    "Si la question dépasse le contenu des documents fournis, réponds explicitement "
    "que tu ne disposes pas de cette information — ne génère pas de contenu inventé."
)

HEADER_HTML = """
<div style="text-align: center; padding: 1rem 0 0.5rem 0;">
    <h1 style="margin: 0; font-size: 1.8rem; font-weight: 700;">Etienne Routhier</h1>
    <p style="margin: 0.25rem 0 0 0; font-size: 1rem;
              color: var(--text-color); opacity: 0.65;">
        Consultant Freelance — Data &amp; IA
    </p>
</div>
"""


@st.cache_resource(show_spinner="Chargement de la base de connaissances...")
def load_vectorstore():
    embeddings = MistralAIEmbeddings(model=EMBEDDING_MODEL)
    return FAISS.load_local(
        FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
    )


# Initialisation session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


def inject_question(q: str):
    st.session_state.pending_question = q


vectorstore = load_vectorstore()

# Sidebar
with st.sidebar:
    if st.button("Vider le cache"):
        st.cache_resource.clear()
        st.rerun()

st.markdown(HEADER_HTML, unsafe_allow_html=True)

# Affichage de l'historique
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

SUGGESTIONS = [
    "Quelle est votre stack technique principale ?",
    "Quels types de missions avez-vous réalisés ?",
    "Etes-vous disponible et quel est votre TJM ?",
    "Seriez-vous un bon fit pour ma mission ?",
]

# Boutons suggérés — affichés uniquement avant le premier message
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

# Résolution de la question active
user_input = st.chat_input("Posez votre question sur le profil...")
active_question = st.session_state.pending_question or user_input
if st.session_state.pending_question:
    st.session_state.pending_question = None  # Consommer avant traitement

if active_question:
    # Afficher et enregistrer le message utilisateur
    with st.chat_message("user"):
        st.markdown(active_question)
    st.session_state.messages.append({"role": "user", "content": active_question})

    # Récupérer les chunks pertinents
    docs = vectorstore.similarity_search(active_question, k=K_RETRIEVED)
    context = "\n\n".join(doc.page_content for doc in docs)

    # Construire les messages LangChain : [SystemMessage, ..., HumanMessage]
    lc_messages = [SystemMessage(content=SYSTEM_PROMPT + f"\n\nContexte:\n{context}")]
    for msg in st.session_state.messages[:-1]:
        if msg["role"] == "user":
            lc_messages.append(HumanMessage(content=msg["content"]))
        else:
            lc_messages.append(AIMessage(content=msg["content"]))
    lc_messages.append(HumanMessage(content=active_question))

    # Générer et afficher la réponse
    with st.chat_message("assistant"):
        with st.spinner("Génération de la réponse..."):
            try:
                answer = ChatMistralAI(model=LLM_MODEL).invoke(lc_messages).content
            except Exception as e:
                err = str(e)
                if "429" in err or "rate limit" in err.lower() or "too many requests" in err.lower():
                    answer = "La limite de requêtes de l'API Mistral a été atteinte. Veuillez réessayer dans quelques instants."
                else:
                    answer = f"Une erreur est survenue : {err}"
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
