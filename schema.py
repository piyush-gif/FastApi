from pydantic import BaseModel

class Register(BaseModel):
  id: int
  name: str
  email: str
  password: str


class Login(BaseModel):
  id: int
  email: str
  password: str