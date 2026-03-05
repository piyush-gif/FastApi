from fastapi import FastAPI
import httpx
app = FastAPI()

@app.get("/")
def read_root():
  return {"Hello":"World"}


@app.get("/pokemon/{name}")
async def pokemon_info(name: str):
  async with httpx.AsyncClient() as client:
    response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{name}")
    data = response.json()

    return {
      "id" : data["id"],
      "sprite":data["sprites"]["front_default"],
      "name" : data["name"],
      "height" : data["height"],
    }
  

@app.get("/pokemon/")
async def pokemon_list(limit: int = 20, offset: int = 0):
  async with httpx.AsyncClient() as client:
    response = await client.get(f"https://pokeapi.co/api/v2/pokemon/?limit={limit}&offset={offset}")
    data = response.json()
    return data
  


@app.get("/pokemon/{name}/moves")
async def pokemon_moves(name : str):
  async with httpx.AsyncClient() as client:
    response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{name}")
    data = response.json()
    return {"moves" : [m["move"]["name"] for m in data["moves"]]}