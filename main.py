from fastapi import FastAPI
from pydantic import BaseModel
import httpx
app = FastAPI()


class RegisterRequest(BaseModel):
  username: str
  email: str
  passwrod: str


@app.post("post")
def register(user: RegisterRequest):
  return {
    "message" : "Registered",
    "username" : user.username
  }