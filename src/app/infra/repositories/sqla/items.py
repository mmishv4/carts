from logging import getLogger

from sqlalchemy import delete, text, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Config
from app.domain.cart_items.entities import CartItem
from app.domain.carts.entities import Cart
from app.domain.interfaces.repositories.items.exceptions import ItemAlreadyExists
from app.domain.interfaces.repositories.items.repo import IItemsRepository
from app.infra.repositories.sqla import models

logger = getLogger(__name__)


class ItemsRepository(IItemsRepository):
    """
    Responsible for interacting with the database to perform CRUD operations on
    CartItem objects. It uses SQLAlchemy to execute SQL statements asynchronously.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.graph_name = Config().DB.graph_name

    async def add_item(self, item: CartItem) -> None:
        """Inserts a new CartItem object into the database."""

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
        stmt = text(
            "SELECT * FROM add_cart_item_func(:cart_id, :item_id, :item_qty, :graph_name);"
        )
        await self._session.execute(
            stmt.bindparams(
                cart_id=item.cart_id,
                item_id=item.id,
                graph_name=self.graph_name,
                item_qty=item.qty,
            )
        )

    async def update_item(self, item: CartItem) -> CartItem:
        """Updates an existing CartItem object in the database."""

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

    async def delete_item(self, cart: Cart, item_id: int) -> None:
        """
        Deletes an item from the database based on the provided cart and item_id.
        """

        stmt = delete(models.CartItem).where(
            models.CartItem.id == item_id, models.CartItem.cart_id == cart.id
        )
        await self._session.execute(stmt)

        stmt = text(
            "SELECT * FROM remove_cart_item_func(:cart_id, :item_id, :graph_name);"
        )
        await self._session.execute(
            stmt.bindparams(cart_id=cart.id, item_id=item_id, graph_name=self.graph_name)
        )
