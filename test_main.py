from fastapi.testclient import TestClient
from main import app, team_db

# TestClient simule un navigateur ou un client HTTP
client = TestClient(app)

def setup_function():
    # Fonction exécutée avant chaque test pour vider l'équipe
    # Cela garantit que les tests sont indépendants les uns des autres
    team_db.clear()

def test_add_pokemon_success():
    payload = { #payload c'est un dictionnaire qui contient les informations du Pokémon à ajouter
        "id": 130,
        "name": "Léviator",
        "type_1": "Eau",
        "type_2": "Vol",
        "level": 50
    }
    response = client.post("/pokemon/", json=payload)
    
    # On vérifie que le serveur répond 200 OK
    assert response.status_code == 200
    # On vérifie le format de la réponse
    assert response.json() == {"message": "Léviator ajouté à l'équipe !", "team_size": 1}

def test_team_limit():
    payload = {"id": 1, "name": "Bulbizarre", "type_1": "Plante", "level": 5}
    
    # On remplit l'équipe avec 6 Pokémon
    for _ in range(6): # for _ in range(6) signifie que l'on va répéter l'action 6 fois, mais on ne se soucie pas de la valeur de l'itérateur
        client.post("/pokemon/", json=payload)
    
    # Le 7ème doit déclencher notre erreur 400
    response = client.post("/pokemon/", json=payload)
    assert response.status_code == 400 
    assert response.json()["detail"] == "Une équipe stratégique ne peut pas dépasser 6 Pokémon." 

def test_count_pokemon_by_type():
    # 1. Préparation (Arrange) : On remplit l'équipe avec des données connues
    client.post("/pokemon/", json={"id": 1, "name": "Bulbizarre", "type_1": "Plante", "type_2": "Poison", "level": 5})
    client.post("/pokemon/", json={"id": 4, "name": "Salamèche", "type_1": "Feu", "level": 5})
    client.post("/pokemon/", json={"id": 43, "name": "Mystherbe", "type_1": "Plante", "type_2": "Poison", "level": 5})

    # 2. Exécution (Act) : On appelle ta nouvelle route
    response_plante = client.get("/team/count/Plante")

    # 3. Vérification (Assert) : On s'attend à trouver 2 types Plante et un code 200
    assert response_plante.status_code == 200
    assert response_plante.json() == {"count": 2, "type": "Plante"}
    
    # 4. Vérification d'un cas vide (Edge case)
    response_eau = client.get("/team/count/Eau")
    assert response_eau.json() == {"count": 0, "type": "Eau"}