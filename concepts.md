# Les Concepts Clés du RAG (Retrieval-Augmented Generation)

Le **RAG** est une technique de l'intelligence artificielle qui permet à un modèle de langage (LLM) de répondre à des questions en se basant sur une base de données de connaissances privées (comme vos documents PDF). Au lieu de compter uniquement sur les connaissances générales apprises lors de son entraînement, le LLM va chercher (Retrieve) les bonnes informations pour générer (Generate) sa réponse.

Voici en détail comment fonctionne l'application étape par étape :

---

## 1. L'Extraction du Texte (Pypdf)
Lorsque vous chargez un document PDF, l'ordinateur ne "lit" pas visuellement la page. Il utilise une bibliothèque (ici `pypdf`) pour extraire tout le texte brut contenu dans le document.
* **Le problème :** Un PDF de 100 pages contient beaucoup trop de texte pour être envoyé d'un coup à un modèle d'IA (qui a une limite de contexte, c'est-à-dire un nombre maximum de mots qu'il peut lire à la fois).

## 2. Le Découpage ou "Chunking" (LangChain Text Splitter)
Puisque le texte est trop long, nous allons le découper en petits morceaux appelés **chunks** (par exemple, des blocs de 1000 caractères).
* **L'astuce :** Pour ne pas couper une phrase ou une idée en plein milieu, on configure un "chevauchement" (overlap). Par exemple, la fin du chunk 1 sera identique au début du chunk 2. Cela permet de préserver le sens.

## 3. La Vectorisation (Embeddings avec HuggingFace)
L'ordinateur ne comprend pas les mots, il ne comprend que les mathématiques. Nous allons donc transformer chaque chunk de texte en une suite de nombres, appelée **Vecteur** (ou *Embedding*).
* Dans notre application, nous utilisons le modèle `all-MiniLM-L6-v2` fourni gratuitement par HuggingFace.
* **Pourquoi faire ça ?** Les vecteurs ont une propriété magique : deux textes qui parlent de la même chose auront des vecteurs très proches mathématiquement, même s'ils n'utilisent pas exactement les mêmes mots. Le concept de "chien" et "chiot" seront très proches dans cet espace mathématique.

## 4. La Base de Données Vectorielle (FAISS)
Une fois que nous avons tous ces vecteurs, il faut les ranger quelque part pour pouvoir les chercher rapidement. Nous utilisons **FAISS** (Facebook AI Similarity Search), une bibliothèque optimisée pour faire de la recherche de vecteurs.
* FAISS stocke l'ensemble de nos chunks sous forme mathématique. 

## 5. La Recherche (Retrieval)
Lorsque vous posez une question dans le chat (ex: "Quel est le chiffre d'affaires ?") :
1. La question est **vectorisée** avec le même modèle (HuggingFace).
2. Nous demandons à FAISS : *"Trouve-moi les 4 vecteurs les plus proches du vecteur de cette question"*.
3. FAISS nous renvoie instantanément les 4 chunks de texte qui sont sémantiquement liés à la question.

## 6. La Génération de la Réponse (Mistral AI)
Maintenant que nous avons les passages pertinents du PDF, nous allons utiliser l'IA de Mistral. Nous ne lui posons pas simplement la question, nous construisons un **Prompt** (une consigne) intelligent :

> *"Tu es un assistant expert. Voici des extraits de documents : [Texte du chunk 1, chunk 2, etc.]. Et voici la question de l'utilisateur : [Question]. Réponds en utilisant UNIQUEMENT les informations des extraits."*

Le LLM lit cette consigne, analyse les passages qu'on lui a fournis (le contexte) et rédige une réponse claire et synthétique.

## 7. La Mémoire Conversationnelle
Dans un simple RAG, l'IA oublie tout après chaque question. 
Pour pouvoir avoir une vraie discussion (ex: "Combien ça coûte ?", puis "Et pour le modèle supérieur ?"), nous injectons les derniers messages échangés directement dans le Prompt. Le LLM a donc le contexte des documents, **ET** l'historique de votre discussion.
