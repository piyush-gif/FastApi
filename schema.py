from pydantic import BaseModel

class Register(BaseModel):
  id: int
  name: str
  email: str
  password: str