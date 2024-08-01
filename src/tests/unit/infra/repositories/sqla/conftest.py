import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.config import DBConfig
from app.domain.cart_items.entities import CartItem
from app.domain.carts.entities import Cart
from app.infra.repositories.sqla.carts import CartsRepository
from app.infra.repositories.sqla.items import ItemsRepository


@pytest_asyncio.fixture(scope="session")
async def db_session(sqla_engine: AsyncEngine) -> AsyncSession:
    async with AsyncSession(sqla_engine) as async_session:
        yield async_session
        await async_session.rollback()


@pytest.fixture()
def carts_repository(db_session: AsyncSession) -> CartsRepository:
    return CartsRepository(db_session)


@pytest.fixture()
def items_repository(db_session: AsyncSession) -> ItemsRepository:
    return ItemsRepository(db_session)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def add_get_cart_item_edge_func(db_session: AsyncSession):
    stmt = text(
        """
        CREATE OR REPLACE FUNCTION get_cart_item_edge(cart_id UUID, item_id INTEGER, graph_name VARCHAR)
        RETURNS SETOF agtype
        LANGUAGE plpgsql
        AS $function$
        DECLARE sql VARCHAR;
        BEGIN
           sql := format(
           'SELECT * FROM cypher(
                %L,
                $$
                    MATCH (c:Cart {id: %L})-[r:CONTAINS]->(i:CartItem {id: %L})
                    RETURN r
                $$) AS (c agtype);
                ', graph_name, cart_id, item_id);
            RETURN QUERY EXECUTE sql;
        END
         $function$;
        """
    )
    await db_session.execute(stmt)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def add_get_cart_func(db_session: AsyncSession):
    stmt = text(
        """
        CREATE OR REPLACE FUNCTION get_cart_func(cart_id UUID, graph_name VARCHAR)
        RETURNS SETOF agtype
        LANGUAGE plpgsql
        AS $function$
        DECLARE sql VARCHAR;
        BEGIN
           sql := format(
           'SELECT * FROM cypher(
                %L,
                $$
                    MATCH (c:Cart {id: %L})
                    RETURN c
                $$) AS (c agtype);
                ', graph_name, cart_id);
            RETURN QUERY EXECUTE sql;
        END
         $function$;
        """
    )
    await db_session.execute(stmt)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def add_get_cart_item(db_session: AsyncSession):
    stmt = text(
        """
        CREATE OR REPLACE FUNCTION get_cart_item(cart_id UUID, item_id INTEGER, graph_name VARCHAR)
        RETURNS SETOF agtype
        LANGUAGE plpgsql
        AS $function$
        DECLARE sql VARCHAR;
        BEGIN
           sql := format(
           'SELECT * FROM cypher(
                %L,
                $$
                    MATCH (c:Cart {id: %L})-[r:CONTAINS]->(i:CartItem {id: %L})
                    RETURN i
                $$) AS (i agtype);
                ', graph_name, cart_id, item_id);
            RETURN QUERY EXECUTE sql;
        END
         $function$;
        """
    )
    await db_session.execute(stmt)


@pytest_asyncio.fixture
async def saved_cart(
    carts_repository: CartsRepository, cart: Cart, db_config: DBConfig
) -> Cart:
    await carts_repository.create(cart)
    return cart


@pytest_asyncio.fixture
async def saved_cart_with_item(
    db_session: AsyncSession, saved_cart: Cart, db_config: DBConfig, cart_item: CartItem
) -> (Cart, CartItem):
    stmt = text(
        "SELECT * FROM add_cart_item_func(:cart_id, :item_id, :item_qty, :graph_name);"
    )
    await db_session.execute(
        stmt.bindparams(
            cart_id=saved_cart.id,
            graph_name=db_config.graph_name,
            item_id=cart_item.id,
            item_qty=cart_item.qty,
        )
    )
    return saved_cart, cart_item
