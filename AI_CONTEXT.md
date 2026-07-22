# AI Context - Démo RAG avec Mistral AI

Ce fichier est destiné à fournir un contexte technique rapide à tout assistant IA ou agent intervenant sur cette base de code.

## 🎯 Objectif du Projet
Application web de démonstration (Proof of Concept) illustrant le fonctionnement d'une architecture RAG (Retrieval-Augmented Generation). Elle permet d'uploader des documents PDF, de les indexer localement et de discuter avec leur contenu via un LLM.

## 🛠️ Stack Technique Principale
- **Interface Web** : Streamlit (`streamlit`)
- **Orchestration IA** : LangChain (`langchain`, `langchain-core`, `langchain-text-splitters`)
- **Modèle de Langage (LLM)** : Mistral AI via `langchain-mistralai` (`ChatMistralAI`)
- **Modèle d'Embedding** : HuggingFace `all-MiniLM-L6-v2` via `langchain-huggingface`
- **Base Vectorielle** : FAISS (`faiss-cpu`) pour un stockage en mémoire locale.
- **Extraction PDF** : `pypdf`
- **Conteneurisation** : Docker, Docker Compose, avec le gestionnaire de paquets ultra-rapide `uv`.

## 📂 Structure et Architecture du Code
- **`app.py`** : C'est le point d'entrée unique et le cœur de l'application Streamlit.
  - La logique s'exécute de haut en bas à chaque interaction de l'utilisateur (comportement par défaut de Streamlit).
  - L'état de l'application (l'historique du chat et la base vectorielle) est persisté dans `st.session_state` (`messages` et `vector_store`).
  - L'upload et le traitement des PDFs (Chunking + Vectorisation) se font dans la sidebar (`st.sidebar`).
  - La fonction clé `generate_response()` gère la récupération de contexte depuis FAISS, la concaténation de l'historique conversationnel (les 4 derniers messages), et l'appel à l'API Mistral avec un `PromptTemplate`. Elle retourne maintenant la réponse et la liste des sources (nom du fichier et page) extraites des métadonnées des documents.
- **`Dockerfile` & `docker-compose.yml`** : Permettent de déployer l'application sur le port 8501. L'installation des dépendances se fait via `uv pip install` pour accélérer le processus de build. Le répertoire local est monté en tant que volume (`.:/app`) pour permettre le "hot-reload" en développement.
- **`requirements.txt`** : Contient toutes les dépendances. Les versions (comme `sentence-transformers>=2.7.0`) sont fixées pour éviter les incompatibilités récentes entre `huggingface_hub` et les anciennes versions de LangChain.

## ⚠️ Pièges Connus & Directives pour l'IA
1. **Écosystème LangChain** : Le code utilise les imports modernes de LangChain (`langchain_core`, `langchain_huggingface`, `langchain_mistralai`) pour éviter les avertissements de dépréciation de l'ancien module `langchain_community`. Ne réintroduisez pas d'imports depuis `langchain_community` pour les modèles d'embedding ou de chat.
2. **Streamlit & Hot-Reloading** : Le `File Watcher` de Streamlit soulèvera parfois des `ModuleNotFoundError` inoffensives (ex: `torchvision`) dans la console en scannant la bibliothèque `transformers`. N'essayez pas de corriger ces erreurs en installant `torchvision` (cela alourdirait l'image de plusieurs Go pour rien).
3. **Gestion du `chat_history`** : Le LLM de base est "stateless". La mémoire est gérée artificiellement en injectant manuellement les 4 derniers messages dans le template du prompt.
4. **Affichage des sources** : Les sources sont extraites des métadonnées des `Document` LangChain (`source` et `page`). Elles sont stockées dans l'historique de chat (`st.session_state.messages`) pour chaque message de l'assistant et affichées dans l'interface via un `st.expander`.
5. **Dépendances** : Si de nouveaux paquets sont ajoutés, conseillez toujours à l'utilisateur de reconstruire l'image avec `docker compose up --build`.

## 🔑 Variables d'Environnement Requises (`.env`)
- `MISTRAL_API_KEY` : Clé API valide pour interroger les modèles de Mistral.
- `MAX_UPLOAD_SIZE` : (Entier, ex: 200) Limite la taille en Mo des PDFs acceptés par l'interface.
