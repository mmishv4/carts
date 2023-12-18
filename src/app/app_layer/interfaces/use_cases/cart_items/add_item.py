from abc import ABC, abstractmethod
from uuid import UUID

from app.app_layer.interfaces.use_cases.cart_items.dto import AddItemToCartInputDTO
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO


class IAddCartItemUseCase(ABC):
    @abstractmethod
    async def execute(self, cart_id: UUID, data: AddItemToCartInputDTO) -> CartOutputDTO:
        ...
