import json

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import DBConfig
from app.domain.cart_items.entities import CartItem
from app.domain.carts.entities import Cart
from app.infra.repositories.sqla import models
from app.infra.repositories.sqla.carts import CartsRepository


@pytest.mark.asyncio()
async def test_create_cart_success(
    db_session: AsyncSession,
    carts_repository: CartsRepository,
    cart: Cart,
    db_config: DBConfig,
):
    result = await carts_repository.create(cart)
    assert result == cart

    stmt = select(models.Cart).where(models.Cart.id == cart.id)
    record_in_rdb = await db_session.scalars(stmt)
    assert record_in_rdb.first().id == cart.id

    stmt = text("SELECT * FROM get_cart_func(:cart_id, :graph_name);")
    record_in_gdb = await db_session.execute(
        stmt.bindparams(cart_id=cart.id, graph_name=db_config.graph_name)
    )
    data = json.loads(record_in_gdb.scalar().split("::")[0])
    assert data["properties"]["id"] == str(cart.id)


@pytest.mark.asyncio()
async def test_clear_cart_success(
    db_session,
    carts_repository: CartsRepository,
    saved_cart_with_item: (Cart, CartItem),
    db_config: DBConfig,
):
    cart_, item_ = saved_cart_with_item
    stmt = text("SELECT * FROM get_cart_item_edge(:cart_id, :item_id, :graph_name);")

    # before clearing
    record_in_gdb = await db_session.execute(
        stmt.bindparams(
            cart_id=cart_.id, item_id=item_.id, graph_name=db_config.graph_name
        )
    )
    assert record_in_gdb.scalar()

    await carts_repository.clear(cart_.id)

    # after clearing
    record_in_gdb = await db_session.execute(
        stmt.bindparams(
            cart_id=cart_.id, item_id=item_.id, graph_name=db_config.graph_name
        )
    )
    assert record_in_gdb.scalar() is None


@pytest.mark.asyncio()
async def test_get_cart_items_total_quantity_success(
    carts_repository: CartsRepository, saved_cart_with_item: (Cart, CartItem)
):
    cart_, item_ = saved_cart_with_item
    result = await carts_repository.get_cart_items_total_quantity(cart_id=cart_.id)
    assert result == float(item_.qty)


@pytest.mark.asyncio()
async def test_get_cart_items_total_quantity_no_items(
    carts_repository: CartsRepository, saved_cart: Cart
):
    result = await carts_repository.get_cart_items_total_quantity(cart_id=saved_cart.id)
    assert result == 0
