from logging import getLogger

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.cart_items.dto import ItemDTO
from app.domain.cart_items.entities import CartItem
from app.domain.interfaces.repositories.items.exceptions import ItemAlreadyExists
from app.domain.interfaces.repositories.items.repo import IItemsRepository
from app.infra.repositories.sqla import models

logger = getLogger(__name__)


class ItemsRepository(IItemsRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add_item(self, item: CartItem) -> None:
        stmt = insert(models.CartItem).values(
            id=item.id,
            name=item.name,
            qty=item.qty,
            price=item.price,
            is_weight=item.is_weight,
            cart_id=item.cart_id,
        )

        try:
            await self._session.execute(stmt)
        except IntegrityError as err:
            raise ItemAlreadyExists(str(err)) from err

    async def get_items(self) -> list[CartItem]:
        stmt = select(models.CartItem)
        result = await self._session.scalars(stmt)

        return [CartItem(data=ItemDTO.model_validate(item)) for item in result.all()]

    async def update_item(self, item: CartItem) -> CartItem:
        stmt = (
            update(models.CartItem)
            .where(models.CartItem.id == item.id, models.CartItem.cart_id == item.cart_id)
            .values(
                name=item.name,
                qty=item.qty,
                price=item.price,
                is_weight=item.is_weight,
            )
        )
        await self._session.execute(stmt)

        return item

    async def delete_item(self, item: CartItem) -> None:
        stmt = delete(models.CartItem).where(
            models.CartItem.id == item.id, models.CartItem.cart_id == item.cart_id
        )
        await self._session.execute(stmt)
