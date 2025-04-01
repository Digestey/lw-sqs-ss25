from sqlalchemy import create_engine, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

base = declarative_base()

class User(base):
    __tablename__ = "User"
    id = Column(int, unique=True, )
    Username = Column(String(50),unique=True, index=True, nullable=False)
    password = Column(String(128), index=True, nullable=False)

class Highscores(base):
    __tablename__ = "Highscores"
    Username = Column(String(50),foreign_key=True, index=True)
    Score = Column(int)