# API Team Builder Pokémon - Infrastructure & CI/CD

> **Projet d'apprentissage DevOps** : Transition d'un profil Full-Stack (React/Node) vers l'ingénierie DevOps. L'objectif est de mettre en place un pipeline CI/CD complet, de la conteneurisation au déploiement cloud automatisé, en s'appuyant sur des bases backend Python robustes.

## Table des matières

1. [Contexte et Objectifs](#contexte-et-objectifs)
2. [Stack Technique](#stack-technique)
3. [Structure du Projet](#structure-du-projet)
4. [Documentation de l'API](#documentation-de-lapi)
5. [Développement Local (Sans Docker)](#développement-local-sans-docker)
6. [Conteneurisation (Avec Docker)](#conteneurisation-avec-docker)
7. [Roadmap DevOps](#roadmap-devops)

---

## Contexte et Objectifs

Cette application est une API légère permettant de gérer une équipe stratégique de Pokémon (règles de composition, comptage par type, etc.).  
Le code métier est volontairement simple afin de concentrer les efforts sur l'**infrastructure et l'automatisation** :

- Écriture de tests automatisés comme premier filet de sécurité.
- Isoler l'application pour résoudre le problème d'environnement ("Ça marche sur ma machine").
- Mettre en place les principes du moindre privilège (sécurité non-root).

---

## Stack Technique

| Outil | Rôle |
|---|---|
| Python 3.11+ | Langage |
| FastAPI | Framework web performant avec auto-documentation |
| Uvicorn | Serveur ASGI |
| Pydantic | Validation des données en temps réel |
| pytest | Suite de tests unitaires |
| Docker | Conteneurisation |

---

## Structure du Projet

```text
api-devops/
├── .dockerignore       # Exclut les fichiers locaux du conteneur (ex: venv)
├── .gitignore          # Exclut les fichiers inutiles du dépôt Git
├── Dockerfile          # Recette de construction de l'image isolée
├── main.py             # Point d'entrée de l'API, routes et logique métier
├── models.py           # Définition des schémas de données (Pydantic)
├── requirements.txt    # Liste figée des dépendances (équivalent package.json)
└── test_main.py        # Suite de tests unitaires automatisés
```

---

## Documentation de l'API

Une fois l'application lancée, une documentation interactive (Swagger UI) est auto-générée sur `/docs`.

| Méthode | Route | Description | Règle métier |
|---|---|---|---|
| `GET` | `/` | Vérification de l'état du serveur | N/A |
| `POST` | `/pokemon/` | Ajoute un Pokémon à l'équipe | Rejeté (400) si l'équipe a déjà 6 membres |
| `GET` | `/team/` | Récupère la liste de l'équipe | N/A |
| `GET` | `/team/count/{type}` | Compte les Pokémon d'un type précis | Vérifie `type_1` et `type_2` |

### Modèle Pokemon

```json
{
  "id": 130,
  "name": "Léviator",
  "type_1": "Eau",
  "type_2": "Vol",
  "level": 50
}
```

| Champ | Type | Requis | Défaut |
|---|---|---|---|
| `id` | int | oui | — |
| `name` | str | oui | — |
| `type_1` | str | oui | — |
| `type_2` | str \| null | non | `null` |
| `level` | int | non | `50` |

---

## Développement Local (Sans Docker)

Pour tester ou modifier le code directement sur votre machine physique.

**Prérequis :** Python 3.11 ou supérieur installé.

**1. Créer et activer l'environnement virtuel**

```bash
python -m venv venv

# Linux / Mac
source venv/bin/activate

# Windows
.\venv\Scripts\activate
```

**2. Installer les dépendances**

```bash
pip install -r requirements.txt
```

**3. Lancer le serveur**

```bash
uvicorn main:app --reload
```

L'API est accessible sur `http://127.0.0.1:8000`.  
La documentation Swagger est disponible sur `http://127.0.0.1:8000/docs`.

**4. Lancer les tests**

```bash
pytest
```

Les tests couvrent :
- Ajout d'un Pokémon avec succès
- Limite de 6 Pokémon par équipe (erreur 400)
- Comptage par type

---

## Conteneurisation (Avec Docker)

L'API est packagée dans un conteneur Linux allégé pour garantir un comportement identique sur n'importe quelle machine ou serveur Cloud.

**Choix d'architecture et de sécurité :**

- **Optimisation du cache** : Le fichier `requirements.txt` est copié et installé avant le code source. Docker mettant en cache chaque instruction, cette séparation évite de réinstaller toutes les dépendances à chaque modification du code.
- **Sécurité (Moindre privilège)** : L'image crée et utilise un utilisateur restreint (`api-user`). Par défaut, un conteneur s'exécute en `root` ; cette bonne pratique évite qu'une faille applicative ne compromette tout le conteneur.
- **Configuration réseau** : Uvicorn est configuré sur `--host 0.0.0.0` pour accepter les requêtes provenant du pont réseau Docker.

**Le Dockerfile expliqué ligne par ligne :**

```dockerfile
# 1. Image de base allégée
FROM python:3.11-slim
```
On part d'une image Linux minimale avec Python déjà installé. La variante `-slim` pèse ~50 Mo contre ~900 Mo pour l'image complète — idéal pour un déploiement rapide.

```dockerfile
# 2. Sécurité : Création d'un utilisateur non-root
RUN adduser --disabled-password --gecos '' api-user
```
Par défaut Docker exécute tout en `root`, ce qui est dangereux. On crée un utilisateur sans mot de passe ni droits système. Si l'API est compromise, l'attaquant est bloqué dans un compte restreint.

```dockerfile
# 3. Dossier de travail dans le conteneur
WORKDIR /app
```
Définit `/app` comme répertoire courant dans le conteneur. Toutes les commandes suivantes s'exécutent depuis cet emplacement.

```dockerfile
# 4. Cache Docker : Copie des dépendances d'abord
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
Docker construit l'image couche par couche et met chaque couche en cache. En copiant `requirements.txt` **avant** le code source, on évite de réinstaller toutes les dépendances à chaque fois qu'on modifie `main.py`. Le flag `--no-cache-dir` évite que pip stocke des fichiers temporaires inutiles dans l'image.

```dockerfile
# 5. Copie du code source
COPY . .
```
Copie tout le projet dans `/app`. Le fichier `.dockerignore` empêche le dossier `venv` local d'être copié (il serait incompatible avec l'OS du conteneur).

```dockerfile
# 6. Sécurité : Changement de propriétaire et bascule
RUN chown -R api-user:api-user /app
USER api-user
```
On donne la propriété des fichiers à `api-user`, puis on bascule sur ce compte. À partir d'ici, tout s'exécute sans privilèges root.

```dockerfile
# 7. Documentation du port
EXPOSE 8000
```
Indique que le conteneur écoute sur le port 8000. C'est documentaire — le port n'est pas ouvert automatiquement, c'est le `-p 8000:8000` du `docker run` qui fait le pont.

```dockerfile
# 8. Commande de démarrage
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```
Commande lancée au démarrage du conteneur. `--host 0.0.0.0` est indispensable : sans ça, Uvicorn n'écoute que sur `localhost` à l'intérieur du conteneur, et aucune requête extérieure ne peut l'atteindre.

**Commandes :**

```bash
# Construire l'image Docker
docker build -t api-pokemon .

# Démarrer le conteneur sur le port 8000
docker run -p 8000:8000 api-pokemon
```

---

## Roadmap DevOps

| Semaine | Thème | Statut |
|---|---|---|
| 1 | Fondation Python + FastAPI | Terminé |
| 2 | Tests unitaires avec pytest | Terminé |
| 3 | Conteneurisation Docker | Terminé |
| 4 | CI/CD avec GitHub Actions | À venir |
| 5 | Déploiement Cloud automatisé | À venir |
