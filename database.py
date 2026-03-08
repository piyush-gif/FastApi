from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:098123@localhost:3306/pokemon_users"

engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(
  autocommit = False,
  autoflush=False,
  bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()