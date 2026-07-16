from fastapi import FastAPI, HTTPException
from models import Pokemon
# Initialisation de l'application
app = FastAPI()
team_db = []

# Définition d'une route GET simple
@app.get("/")
def read_root():
    return {"message": "Hello World, le pipeline commence ici."}

@app.get("/test/{element_id}")
def read_element(element_id: int, q: str | None = None):
    return {"element_id": element_id, "requete": q}

# Définition d'une route GET pour compter les Pokémon par type
@app.get("/team/count/{pokemon_type}")
def count_pokemon_by_type(pokemon_type:str) :
    count = 0
    for p in team_db:
        if p.type_1 == pokemon_type or p.type_2 == pokemon_type:
            count += 1
    return {"count": count, "type": pokemon_type}


# Définition d'une route POST simple
@app.post("/pokemon/")
def add_pokemon(pokemon: Pokemon):
    if len(team_db) >= 6:
        raise HTTPException(status_code=400, detail="Une équipe stratégique ne peut pas dépasser 6 Pokémon.")
    team_db.append(pokemon)
    return {"message": f"{pokemon.name} ajouté à l'équipe !", "team_size": len(team_db)}