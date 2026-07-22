# Feuille de Route : Démo RAG avec API LLM

Ce document décrit les étapes pour créer une application de démonstration de RAG (Retrieval-Augmented Generation) utilisant une interface web simple, une API pour le modèle de langage (LLM), et déployée via Docker.

**Utiliser les versions les plus récentes de langchain et uv pour que l'image docker soit rapide à construire (uniquement sur CPU pour l'instant)**

## Phase 1 : Préparation et Architecture

**Objectif :** Mettre en place la structure du projet et choisir les outils.

*   **1.1. Définir la Stack Technique :**
    *   **Langage :** Python 3.12
    *   **Interface Web :** **Streamlit** (Idéal pour un PoC rapide et interactif).
    *   **API LLM :** Un service externe comme **Mistral AI API**, **OpenAI API**, ou **Groq API**.
    *   **Vectorisation (Embeddings) :** Bibliothèque `sentence-transformers` (modèle `all-MiniLM-L6-v2` ou mieux s'il y a maintenant).
    *   **Base de Données Vectorielle :**
        *   **Option A (Simple) :** **FAISS** (bibliothèque de Facebook AI). Fonctionne en mémoire ou sur disque, pas de service séparé.
        *   **Option B (Robuste, dans un second temps) :** **ChromaDB** (base de données vectorielle open-source). Nécessite un conteneur Docker dédié mais gère mieux la persistance.
    *   **Déploiement :** **Docker** & **Docker Compose**.

*   **1.2. Structurer le Projet :**
    ```
    /rag-demo-app
    |-- app.py             # Le code principal de l'application Streamlit
    |-- requirements.txt   # Les dépendances Python
    |-- Dockerfile         # Instructions pour construire l'image de l'app
    |-- docker-compose.yml # Pour orchestrer les conteneurs
    |-- .env               # Pour stocker les clés d'API (NE PAS COMMIT)
    |-- .gitignore         # Pour ignorer .env, __pycache__, etc.
    |-- data/              # Dossier pour stocker la base vectorielle (si FAISS)
    ```

*   **1.3. Gérer les Secrets :**
    *   Créer un fichier `.env` pour y stocker votre clé d'API (ex: `MISTRAL_API_KEY="votre_cle"`).
    *   Utiliser la bibliothèque `python-dotenv` pour charger cette clé dans votre application.

## Phase 2 : Pipeline d'Ingestion des Documents

**Objectif :** Créer la logique pour uploader, traiter et vectoriser les documents. Cette logique sera dans `app.py`.

*   **2.1. Créer l'Interface d'Upload :**
    *   Utiliser le composant `st.sidebar` et `st.file_uploader` de Streamlit pour permettre à l'utilisateur de charger un ou plusieurs fichiers PDF.

*   **2.2. Extraire le Texte :**
    *   Pour chaque PDF uploadé, utiliser la bibliothèque `pypdf` pour extraire le contenu textuel page par page.
    *   *Note : Pour cette démo, on ignore l'OCR pour garder les choses simples.*

*   **2.3. Découper le Texte (Chunking) :**
    *   Le texte extrait doit être découpé en petits morceaux (chunks) pour que la recherche soit efficace.
    *   Utiliser `RecursiveCharacterTextSplitter` de la bibliothèque `LangChain` pour découper le texte en morceaux de taille fixe avec un chevauchement (ex: 1000 caractères par chunk, 200 de chevauchement).

*   **2.4. Vectoriser et Stocker :**
    *   Charger le modèle d'embedding (`SentenceTransformer`).
    *   Pour chaque "chunk" de texte, générer son vecteur (embedding).
    *   Stocker les chunks de texte et leurs vecteurs correspondants dans la base de données vectorielle (FAISS (ou ChromaDBplus tard)).
    *   Cette action doit être déclenchée par un bouton "Traiter les documents" dans l'interface.

## Phase 3 : Cœur du RAG - Interface de Chat

**Objectif :** Implémenter la logique de conversation qui interroge les documents.

*   **3.1. Créer l'Interface de Chat :**
    *   Utiliser `st.chat_input` pour la zone de saisie de l'utilisateur.
    *   Utiliser `st.chat_message` pour afficher les messages de l'utilisateur et de l'assistant.
    *   Gérer l'historique de la conversation avec `st.session_state`.

*   **3.2. Logique de Récupération (Retrieval) :**
    *   Quand l'utilisateur pose une question :
        1.  Vectoriser la question de l'utilisateur avec le **même** modèle d'embedding.
        2.  Interroger la base de données vectorielle pour trouver les `k` chunks de texte les plus pertinents (ex: les 4 chunks les plus similaires).

*   **3.3. Logique de Génération (Generation) :**
    *   Construire un **prompt** pour l'API LLM en combinant le contexte et la question.
        ```markdown
        **Prompt Template:**

        Tu es un assistant expert qui répond aux questions en se basant uniquement sur le contexte fourni. Si l'information n'est pas dans le contexte, dis "Je ne trouve pas l'information dans les documents."

        **Contexte :**
        {contexte_des_chunks_retrouvés}

        **Question :**
        {question_de_l_utilisateur}

        **Réponse :**
        ```
    *   Appeler l'API LLM (Mistral, Gemini...) avec ce prompt.
    *   Afficher la réponse générée dans l'interface de chat.

## Phase 4 : Déploiement sur le VPS

**Objectif :** "Conteneuriser" l'application pour un déploiement simple et reproductible.

*   **4.1. Écrire le `Dockerfile` :**
    *   Partir d'une image de base Python (ex: `python:3.10-slim`).
    *   Copier `requirements.txt` et installer les dépendances et .
    *   Copier le reste du code de l'application (`app.py`, etc.).
    *   Exposer le port de Streamlit (`EXPOSE 8501`).
    *   Définir la commande de démarrage (`CMD ["streamlit", "run", "app.py"]`).

*   **4.2. Écrire le `docker-compose.yml` :**
    *   Définir un service `app` qui utilise le `Dockerfile` créé.
    *   Mapper les ports pour rendre l'application accessible depuis l'extérieur (ex: `ports: - "8501:8501"`).
    *   (Si vous utilisez ChromaDB) Ajouter un service `chromadb` basé sur l'image `chroma/chroma`.
    *   Utiliser les volumes pour rendre les données persistantes (la base vectorielle).

*   **4.3. Lancer l'Application :**
    *   Se connecter au VPS.
    *   Installer Docker et Docker Compose.
    *   Cloner votre projet.
    *   Lancer `docker-compose up --build -d` depuis la racine du projet.
    *   Votre application sera accessible via `http://<IP_de_votre_VPS>:8501`.
