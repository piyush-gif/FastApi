from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from database import get_db
from models.models import Pokemon, CaughtPokemon, EncounterLog, User
from auth.token import SECRET_KEY, ALGORITHM
from jose import jwt, JWTError
from datetime import date
import httpx
import random

router = APIRouter()

REGION_IDS = {
    "kanto": 1,
    "johto": 2,
    "hoenn": 3,
}

MAX_ENCOUNTERS_PER_DAY = 5

def get_current_user(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("id")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/explore/routes/{region_name}")
async def get_routes(region_name: str):
    region_id = REGION_IDS.get(region_name.lower())
    if not region_id:
        raise HTTPException(status_code=404, detail="Region not found")

    async with httpx.AsyncClient(timeout=10) as client:
        # 1. Get all locations in the region
        res = await client.get(f"https://pokeapi.co/api/v2/region/{region_id}")
        if res.status_code != 200:
            raise HTTPException(status_code=404, detail="Region not found in PokéAPI")
        locations = res.json().get("locations", [])

        # 2. For each location, fetch its areas and collect area names
        area_names = []
        for loc in locations:
            loc_res = await client.get(loc["url"])
            if loc_res.status_code != 200:
                continue
            areas = loc_res.json().get("areas", [])
            for area in areas:
                area_names.append(area["name"])

    return {"routes": area_names}

@router.get("/explore/encounter/{route_name}")
async def get_encounter(route_name: str, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)

    today = str(date.today())
    log = db.query(EncounterLog).filter(
        EncounterLog.user_id == user.id,
        EncounterLog.date == today
    ).first()

    if log and log.count >= MAX_ENCOUNTERS_PER_DAY:
        raise HTTPException(status_code=429, detail="Daily encounter limit reached. Come back tomorrow!")

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            res = await client.get(f"https://pokeapi.co/api/v2/location-area/{route_name}")
            if res.status_code != 200:
                raise HTTPException(status_code=404, detail="Route not found")
            data = res.json()
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to fetch route data")

    encounters = data.get("pokemon_encounters", [])

    valid = []
    for e in encounters:
        url = e["pokemon"]["url"]
        pokemon_id = int(url.rstrip("/").split("/")[-1])
        if 1 <= pokemon_id <= 386:
            valid.append(pokemon_id)

    if not valid:
        raise HTTPException(status_code=404, detail="No gen 1-3 pokemon on this route. Try another route!")

    random.shuffle(valid)
    pokemon = None
    for pid in valid:
        pokemon = db.query(Pokemon).filter(Pokemon.id == pid).first()
        if pokemon:
            break

    if not pokemon:
        raise HTTPException(status_code=404, detail="No pokemon found in database for this route. Try another!")

    if log:
        log.count += 1
    else:
        log = EncounterLog(user_id=user.id, date=today, count=1)
        db.add(log)
    db.commit()

    return {
        "id": pokemon.id,
        "name": pokemon.name,
        "types": pokemon.types,
        "sprite": pokemon.sprite,
        "capture_rate": pokemon.capture_rate,
        "encounters_used": log.count,
        "encounters_remaining": MAX_ENCOUNTERS_PER_DAY - log.count
    }

@router.post("/explore/catch")
def catch_pokemon(body: dict, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    pokemon_id = body.get("pokemon_id")

    if not pokemon_id:
        raise HTTPException(status_code=400, detail="pokemon_id required")

    pokemon = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if not pokemon:
        raise HTTPException(status_code=404, detail="Pokemon not found")

    already_caught = db.query(CaughtPokemon).filter(
        CaughtPokemon.user_id == user.id,
        CaughtPokemon.pokemon_id == pokemon_id
    ).first()
    if already_caught:
        return {"result": "already_caught", "message": "You already have this pokemon!"}

    capture_rate = pokemon.capture_rate or 45
    catch_probability = capture_rate / 255
    success = random.random() < catch_probability

    if success:
        caught = CaughtPokemon(user_id=user.id, pokemon_id=pokemon_id)
        db.add(caught)
        db.commit()
        return {"result": "caught", "message": f"You caught {pokemon.name.capitalize()}!"}
    else:
        return {"result": "fled", "message": f"{pokemon.name.capitalize()} fled!"}