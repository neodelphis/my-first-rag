import streamlit as st
import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()
MAX_UPLOAD_SIZE = int(os.environ.get("MAX_UPLOAD_SIZE", 200))

st.set_page_config(page_title="RAG", page_icon="📄")
st.title("📄 Une IA pour interagir avec vos documents")

# --- Initialisation de l'état de la session ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

# --- Fonctions utilitaires ---
def get_pdf_documents(pdf_docs):
    documents = []
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for i, page in enumerate(pdf_reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                documents.append(Document(page_content=text, metadata={"source": pdf.name, "page": i + 1}))
    return documents

def get_text_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

def get_vectorstore(documents):
    # Utilisation de HuggingFace pour l'embedding gratuit et efficace
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(documents=documents, embedding=embeddings)
    return vectorstore

def generate_response(question, vector_store, chat_history):
    # Trouver les chunks pertinents
    docs = vector_store.similarity_search(question, k=4)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Extraire les sources uniques
    sources = set()
    for doc in docs:
        source_name = doc.metadata.get("source", "Inconnu")
        page = doc.metadata.get("page", "Inconnue")
        sources.add(f"Fichier : {source_name}, Page : {page}")
    
    # Formater l'historique (les 4 derniers messages pour ne pas surcharger)
    history_str = ""
    for msg in chat_history[-4:]:
        role = "Utilisateur" if msg["role"] == "user" else "Assistant"
        history_str += f"{role} : {msg['content']}\n"
    
    # Préparer le prompt
    template = """
    Tu es un assistant expert qui répond aux questions en se basant uniquement sur le contexte fourni.
    Prends en compte l'historique récent de la conversation pour comprendre le contexte de la question.
    Si l'information n'est pas dans le contexte, dis "Je ne trouve pas l'information dans les documents."

    **Historique récent :**
    {history}

    **Contexte :**
    {context}

    **Question :**
    {question}

    **Réponse :**
    """
    prompt = PromptTemplate(template=template, input_variables=["history", "context", "question"])
    
    # Appeler le modèle Mistral
    llm = ChatMistralAI(model="mistral-large-latest", temperature=0)
    chain = prompt | llm
    
    response = chain.invoke({"history": history_str, "context": context, "question": question})
    return response.content, list(sources)

# --- Interface Sidebar (Upload) ---
with st.sidebar:
    st.subheader("Vos Documents")
    pdf_docs = st.file_uploader(
        "Téléchargez vos PDFs ici et cliquez sur 'Traiter les documents'", accept_multiple_files=True
    )
    
    # Message d'accueil initial si aucun document n'est traité
    if st.session_state.vector_store is None and not st.session_state.messages:
        st.session_state.messages.append({"role": "assistant", "content": "Bonjour ! Pour commencer, veuillez télécharger un ou plusieurs documents PDF et cliquer sur 'Traiter les documents'."})

    if st.button("Traiter les documents"):
        if not os.environ.get("MISTRAL_API_KEY") or os.environ.get("MISTRAL_API_KEY") == "votre_cle_api_mistral_ici":
             st.error("Veuillez configurer votre MISTRAL_API_KEY dans le fichier .env d'abord.")
        elif not pdf_docs:
             st.warning("Veuillez télécharger au moins un document PDF.")
        else:
            # Vérifier la taille de chaque fichier
            size_exceeded = False
            for pdf in pdf_docs:
                if pdf.size > MAX_UPLOAD_SIZE * 1024 * 1024:
                    st.error(f"Le fichier {pdf.name} dépasse la taille maximale autorisée de {MAX_UPLOAD_SIZE} MB.")
                    size_exceeded = True
                    break
            
            if not size_exceeded:
                with st.spinner("Traitement en cours..."):
                    # 1. Extraire les documents avec métadonnées
                    docs = get_pdf_documents(pdf_docs)
                    
                    # 2. Découper les documents
                    text_chunks = get_text_chunks(docs)
                    
                    # 3. Créer le vector store
                    vector_store = get_vectorstore(text_chunks)
                    
                    # Sauvegarder dans la session
                    st.session_state.vector_store = vector_store
                    st.success(f"{len(text_chunks)} morceaux de texte vectorisés avec succès !")
                    # Vider l'historique et afficher le message de succès
                    st.session_state.messages = []
                    st.session_state.messages.append({"role": "assistant", "content": "Bonjour ! Vos documents sont prêts, posez-moi une question."})

# --- Interface Chat Principale ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Afficher les sources si elles existent pour ce message
        if message["role"] == "assistant" and "sources" in message and message["sources"]:
            with st.expander("Sources utilisées"):
                for source in message["sources"]:
                    st.markdown(f"- {source}")

if prompt_user := st.chat_input("Posez une question sur vos documents"):
    # Afficher le message de l'utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt_user})
    with st.chat_message("user"):
        st.markdown(prompt_user)
        
    # Vérifier que le vector store est prêt
    if st.session_state.vector_store is None:
        with st.chat_message("assistant"):
             st.error("Veuillez d'abord télécharger et traiter des documents dans la barre latérale.")
    else:
        # Générer et afficher la réponse
        with st.chat_message("assistant"):
            with st.spinner("Je cherche la réponse..."):
                # On passe l'historique (sans la question actuelle qui vient d'être ajoutée)
                history = st.session_state.messages[:-1]
                response_text, sources = generate_response(prompt_user, st.session_state.vector_store, history)                
                st.markdown(response_text)
                if sources:
                    with st.expander("Sources utilisées"):
                        for source in sources:
                            st.markdown(f"- {source}")
                # Ajouter la réponse complète (avec sources) à l'historique
                st.session_state.messages.append({"role": "assistant", "content": response_text, "sources": sources})
