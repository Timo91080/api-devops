from fastapi import FastAPI

# Initialisation de l'application
app = FastAPI()

# Définition d'une route GET simple
@app.get("/")
def read_root():
    return {"message": "Hello World, le pipeline commence ici."}