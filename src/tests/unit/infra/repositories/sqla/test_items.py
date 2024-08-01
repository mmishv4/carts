import json

import pytest
from sqlalchemy import select, text

from app.config import DBConfig
from app.domain.cart_items.entities import CartItem
from app.domain.carts.entities import Cart
from app.infra.repositories.sqla import models
from app.infra.repositories.sqla.items import ItemsRepository


@pytest.mark.asyncio()
async def test_add_cart_item_success(
    db_session,
    items_repository: ItemsRepository,
    saved_cart: Cart,
    db_config: DBConfig,
    cart_item: CartItem,
) -> None:
    await items_repository.add_item(cart_item)

    stmt = select(models.CartItem).where(
        models.CartItem.id == cart_item.id, models.CartItem.cart_id == saved_cart.id
    )
    record_in_rdb = await db_session.scalars(stmt)
    assert record_in_rdb.first().id == cart_item.id

    stmt = text("SELECT * FROM get_cart_item(:cart_id, :item_id, :graph_name);")
    record_in_gdb = await db_session.execute(
        stmt.bindparams(
            cart_id=saved_cart.id, item_id=cart_item.id, graph_name=db_config.graph_name
        )
    )
    assert len(result := record_in_gdb.scalars().all()) == 1
    data = [json.loads(record.split("::")[0]) for record in result]
    assert data[0]["properties"]["id"] == str(cart_item.id)
    assert data[0]["properties"]["qty"] == str(cart_item.qty)


@pytest.mark.asyncio()
async def test_delete_cart_item_success(
    db_session,
    items_repository: ItemsRepository,
    saved_cart_with_item: (Cart, CartItem),
    db_config: DBConfig,
) -> None:
    cart_, item_ = saved_cart_with_item
    await items_repository.delete_item(cart_, item_.id)

    stmt = select(models.CartItem).where(
        models.CartItem.id == item_.id, models.CartItem.cart_id == cart_.id
    )
    record_in_rdb = await db_session.scalars(stmt)
    assert record_in_rdb.first() is None

    stmt = text("SELECT * FROM get_cart_item_edge(:cart_id, :item_id, :graph_name);")
    record_in_gdb = await db_session.execute(
        stmt.bindparams(
            cart_id=cart_.id, item_id=item_.id, graph_name=db_config.graph_name
        )
    )
    assert record_in_gdb.scalar() is None
