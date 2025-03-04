from sqlalchemy import Column, Float, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Coin(Base):
    __tablename__: str = "coin"
    id: str = Column(String, primary_key=True)
    symbol: str = Column(String, unique=True, nullable=False)
    name: str = Column(String, nullable=False)
    target_price: float = Column(Float, nullable=True)
