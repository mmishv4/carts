from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.carts.entities import Cart


class ICartsRepository(ABC):
    @abstractmethod
    async def retrieve(self, cart_id: UUID) -> Cart:
        ...

    @abstractmethod
    async def update(self, cart: Cart) -> Cart:
        ...

    @abstractmethod
    async def get_list(self) -> Cart:
        ...