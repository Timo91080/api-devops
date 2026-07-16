from pydantic import BaseModel
#MODEL POKEMON
class Pokemon(BaseModel):
    id: int
    name: str
    type_1: str
    type_2: str | None = None
    level: int = 50