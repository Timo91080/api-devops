# 1. Image de base allégée
FROM python:3.11-slim

# 2. Sécurité : Création d'un utilisateur non-root
RUN adduser --disabled-password --gecos '' api-user

# 3. Dossier de travail dans le conteneur
WORKDIR /app

# 4. Cache Docker : Copie des dépendances d'abord
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copie du code source
COPY . .

# 6. Sécurité : Changement de propriétaire et bascule
RUN chown -R api-user:api-user /app
USER api-user

# 7. Documentation du port
EXPOSE 8000

# 8. Commande de démarrage
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]