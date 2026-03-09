from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas.User import UserRequest, RegisterRequest
from sqlalchemy.orm import Session
from database import get_db, engine
from models.models import Base, User
import bcrypt
app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def register(user: UserRequest ):
  return {
    "message" : "Logged in",
    "username" : user.username
  }


