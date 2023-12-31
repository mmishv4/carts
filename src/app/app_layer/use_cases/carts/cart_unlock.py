from uuid import UUID

from app.app_layer.interfaces.distributed_lock_system.system import IDistributedLockSystem
from app.app_layer.interfaces.unit_of_work.sql import IUnitOfWork
from app.app_layer.interfaces.use_cases.carts.cart_unlock import IUnlockCartUseCase
from app.app_layer.interfaces.use_cases.carts.dto import CartOutputDTO


class UnlockCartUseCase(IUnlockCartUseCase):
    def __init__(
        self,
        uow: IUnitOfWork,
        distributed_lock_system: IDistributedLockSystem,
    ) -> None:
        self._uow = uow
        self._distributed_lock_system = distributed_lock_system

    async def execute(self, cart_id: UUID) -> CartOutputDTO:
        async with self._distributed_lock_system(name=f"cart-lock-{cart_id}"):
            return await self._unlock_cart(cart_id=cart_id)

    async def _unlock_cart(self, cart_id: UUID) -> CartOutputDTO:
        async with self._uow(autocommit=True):
            cart = await self._uow.carts.retrieve(cart_id=cart_id)
            cart.unlock()
            await self._uow.carts.update(cart=cart)

        return CartOutputDTO.model_validate(cart)
