from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas.User import LoginRequest, RegisterRequest
from sqlalchemy.orm import Session
from database import get_db, engine
from models.models import Base, User
from auth.token import create_access_token, create_refresh_token
import bcrypt
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

@app.post("/register")
def register(user: RegisterRequest, db: Session = Depends(get_db)):
  
  if db.query(User).filter(User.username == user.username ).first():
    raise HTTPException(status_code=400, detail="Username already taken")
  
  if db.query(User).filter(User.email == user.email).first():
    raise HTTPException(status_code = 400, detail = "Email hase been already used")
  
  hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())

  new_user  = User(username=user.username, email=user.email, hashed_password=hashed_password)

  db.add(new_user)
  db.commit()
  db.refresh(new_user)

@app.post("/login")
def register(user: LoginRequest, db: Session = Depends(get_db) ):
  db_user = db.query(User).filter(User.email == user.email).first()
  if not db_user:
    raise HTTPException(status_code = 400, detail = "User not found")

  if not bcrypt.checkpw(user.password.encode("utf-8"), db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
  
  access_token = create_access_token({"sub": db_user.username})
  refresh_token = create_refresh_token({"sub": db_user.username})

  return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }