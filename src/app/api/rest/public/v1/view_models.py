from uuid import UUID

from pydantic import BaseModel, Field


class BaseItemViewModel(BaseModel):
    class Config:
        from_attributes = True
        populate_by_name = True

    id: int
    name: str = Field(alias="title")
    qty: float = Field(alias="quantity")
    price: float
    cost: float
    is_weight: bool


class CartViewModel(BaseModel):
    class Config:
        from_attributes = True
        populate_by_name = True

    id: UUID
    items: list[BaseItemViewModel]
    items_qty: float = Field(alias="items_quantity")
    cost: float
