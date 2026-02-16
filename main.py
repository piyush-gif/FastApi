from fastapi import FastAPI
from schema import Register
app = FastAPI()

todos=["drink", "run"]

info = []

@app.get("/")
def read_root():
  return {"Hello":"World"}



@app.get("/items/{items_id}")
def get_items(items_id: int):
  todos.append(items_id)
  return todos

@app.post("/register")
def post_register(user: Register):

  data = {
    "id" : user.id,
    "name" : user.name,
    "email" : user.email,
    "password" : user.password
        }
  
  info.append(data)

  return data


