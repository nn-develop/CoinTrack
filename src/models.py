from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Coin(Base):
    __tablename__: str = "coin"
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    symbol: str = Column(String, unique=True, nullable=False)
    name: str = Column(String, nullable=False)
