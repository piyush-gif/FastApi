from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

    caught_pokemon = relationship("CaughtPokemon", back_populates="user")
    favorites = relationship("Favorite", back_populates="user")
    encounter_logs = relationship("EncounterLog", back_populates="user")


class Pokemon(Base):
    __tablename__ = "pokemon"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    types = Column(JSON, nullable=False)          # ["fire", "flying"]
    sprite = Column(String(255), nullable=False)  # image URL
    stats = Column(JSON, nullable=False)          # {"hp": 45, "attack": 49, ...}
    abilities = Column(JSON, nullable=False)      # ["overgrow", "chlorophyll"]
    moves = Column(JSON, nullable=False)          # list of moves
    height = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    base_experience = Column(Integer, nullable=True)
    capture_rate = Column(Integer, nullable=True)

    caught_by = relationship("CaughtPokemon", back_populates="pokemon")
    favorited_by = relationship("Favorite", back_populates="pokemon")


class CaughtPokemon(Base):
    __tablename__ = "caught_pokemon"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pokemon_id = Column(Integer, ForeignKey("pokemon.id"), nullable=False)
    caught_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="caught_pokemon")
    pokemon = relationship("Pokemon", back_populates="caught_by")


class Favorite(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pokemon_id = Column(Integer, ForeignKey("pokemon.id"), nullable=False)
    favorited_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="favorites")
    pokemon = relationship("Pokemon", back_populates="favorited_by")

class EncounterLog(Base):
    __tablename__ = "encounter_logs"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(String(20), nullable=False)  # stored as "YYYY-MM-DD"
    count = Column(Integer, default=0)
    user = relationship("User", back_populates="encounter_logs")