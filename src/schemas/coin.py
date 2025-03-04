from pydantic import BaseModel, Field, ConfigDict


class CoinBase(BaseModel):
    id: str
    symbol: str
    name: str
    target_price: float | None = None

    model_config = ConfigDict(from_attributes=True)


class CoinCreate(CoinBase):
    pass


class CoinUpdate(BaseModel):
    id: str | None = Field(default=None)
    symbol: str | None = Field(default=None)
    name: str | None = Field(default=None)
    target_price: float | None = Field(default=None)
