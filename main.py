from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models.models import Base
from routers.auth import router as auth_router
from routers.pokedex import router as pokedex_router


app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(pokedex_router)