# Démo RAG (Retrieval-Augmented Generation)

Ce projet est une application de démonstration permettant aux utilisateurs de télécharger leurs propres documents PDF et d'interagir avec eux via une interface de chat. L'application extrait les informations des documents fournis pour répondre aux questions, tout en gardant en mémoire l'historique de la conversation.

## 🧠 Comprendre le RAG

Si vous souhaitez comprendre en détail le fonctionnement technique de cette application (Chunking, Vectorisation, FAISS, Prompts...), consultez le fichier d'explications :
👉 **[Lire les concepts du RAG (concepts.md)](./concepts.md)**

## ✨ Fonctionnalités

- **Upload de PDF** : Chargez vos fichiers pour constituer une base de connaissances privée.
- **Vérification de taille** : Limite paramétrable pour la taille des fichiers uploadés.
- **Mémoire conversationnelle** : Posez des questions de suivi naturellement, l'assistant se souvient des messages précédents !
- **Vectorisation locale** : Les embeddings sont calculés rapidement et localement (HuggingFace `all-MiniLM-L6-v2`).
- **LLM Puissant** : Utilise l'API de Mistral AI pour générer des réponses précises (Gratuit pour les développeurs).
- **Déploiement Docker optimisé** : Utilisation du gestionnaire de paquets `uv`.

## 🛠️ Stack Technique

- **Frontend** : [Streamlit](https://streamlit.io/)
- **Backend** : Python 3.12
- **Orchestration RAG** : [LangChain](https://www.langchain.com/)
- **Modèle de Langage (LLM)** : [Mistral AI API](https://mistral.ai/)
- **Embeddings** : `sentence-transformers` (Hugging Face)
- **Base de données vectorielle** : FAISS (en mémoire locale)
- **Conteneurisation** : Docker & Docker Compose

## 🚀 Comment Lancer le Projet

Pour lancer cette application localement, assurez-vous d'avoir installé Docker et Docker Compose.

1. **Préparez votre environnement :**
   Créez un fichier `.env` à la racine du projet, et ajoutez-y votre clé d'API Mistral (vous pouvez modifier la limite d'upload si besoin) :
   ```env
   MISTRAL_API_KEY="votre_cle_api_mistral_ici"
   MAX_UPLOAD_SIZE=200
   ```

2. **Construisez et lancez l'application :**
   ```bash
   docker compose up --build -d
   ```

3. **Accédez à l'application :**
   Ouvrez votre navigateur sur **http://localhost:8501**.
   *(Note : Ignorez les adresses IP internes affichées dans les logs de Docker)*.

4. **Utilisation :**
   - Téléchargez un fichier PDF via la barre latérale.
   - Cliquez sur **Traiter les documents**.
   - Commencez à discuter avec l'assistant !

## Exemple d'utilisation

Pour tester l'application avec des documents concrets, vous pouvez par exemple utiliser les fichiers suivants que vous trouverez dans le répertoire `data` :

*   `Hisoire des Sables d Olonne.pdf`
*   `Compte personnel de formation.pdf`

Une fois que vous avez lancé l'application et téléchargé ces deux fichiers via l'interface, voici quelques questions que vous pourriez poser pour voir comment l'assistant extrait les informations :

#### Questions sur le Compte Personnel de Formation (CPF)

*   C'est quoi le CPF?
*   Combien on cumule de droits par an?
*   Quand un salarié doit-il demander l'accord de son employeur pour une formation sur son temps de travail?
*   Est-il possible de transférer ou donner les crédits de son CPF à un collègue?

#### Questions sur l'histoire des Sables-d'Olonne

*   Combien il y a de ports aux Sables d'olonne?
*   En quelle année et par qui la ville des Sables-d'Olonne a-t-elle été fondée ?
*   Quel célèbre pirate des Caraïbes est né aux Sables-d'Olonne ?
*   Comment s'appelle le réseau de transports en commun?

## Résolution des erreurs courantes

- Si vous voyez des erreurs `ModuleNotFoundError: No module named 'torchvision'` dans la console de votre terminal Docker, c'est un effet de bord inoffensif du système de rechargement automatique de Streamlit. **Vous pouvez l'ignorer.**
