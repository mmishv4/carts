"""add-apache-age

Revision ID: 377748753606
Revises: f82269e25cac
Create Date: 2024-07-19 21:13:41.320325

"""
from typing import Sequence, Union

from sqlalchemy import text

from alembic import op
from app.config import Config

app_config = Config()

# revision identifiers, used by Alembic.
revision: str = "377748753606"
down_revision: Union[str, None] = "f82269e25cac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(text("CREATE EXTENSION IF NOT EXISTS age;"))
    stmt = text("SELECT * FROM ag_catalog.create_graph(:graph_name)")
    op.execute(stmt.bindparams(graph_name=app_config.DB.graph_name))
    op.execute(text("LOAD 'age';"))
    op.execute(text('SET search_path = ag_catalog, "$user", public;'))
    stmt = text(
        """
        CREATE OR REPLACE FUNCTION create_cart_func(cart_id UUID, graph_name VARCHAR)
        RETURNS SETOF agtype
        LANGUAGE plpgsql
        AS $function$
        DECLARE sql VARCHAR;
        BEGIN
           sql := format(
           'SELECT * FROM cypher(
                %L,
                $$
                    MERGE (c:Cart {id: %L})
                    RETURN c
                $$) AS (c agtype);
                ', graph_name, cart_id);
            RETURN QUERY EXECUTE sql;
        END
         $function$;
        """
    )
    op.execute(stmt)
    stmt = text(
        """
        CREATE OR REPLACE FUNCTION remove_cart_items_func(cart_id UUID, graph_name VARCHAR)
        RETURNS SETOF agtype
        LANGUAGE plpgsql
        AS $function$
        DECLARE sql VARCHAR;
        BEGIN
           sql := format(
           'SELECT * FROM cypher(
                %L,
                $$
                    MATCH (c:Cart {id: %L})-[r:CONTAINS]->() 
                    DELETE r
                $$) AS (c agtype);
                ', graph_name, cart_id);
            RETURN QUERY EXECUTE sql;
        END
         $function$;
        """
    )
    op.execute(stmt)
    stmt = text(
        """
        CREATE OR REPLACE FUNCTION add_cart_item_func(cart_id UUID, item_id INTEGER, item_qty NUMERIC, graph_name VARCHAR)
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
                    MERGE (i:CartItem {id: %L, qty: %L})
                    CREATE (c)-[r:CONTAINS]->(i)
                    RETURN i
                $$) AS (c agtype);
                ', graph_name, cart_id, item_id, item_qty);
            RETURN QUERY EXECUTE sql;
        END
         $function$;
        """
    )
    op.execute(stmt)
    stmt = text(
        """
        CREATE OR REPLACE FUNCTION remove_cart_item_func(cart_id UUID, item_id INTEGER, graph_name VARCHAR)
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
                    DELETE r
                $$) AS (c agtype);
                ', graph_name, cart_id, item_id);
            RETURN QUERY EXECUTE sql;
        END
         $function$;
        """
    )
    op.execute(stmt)
    stmt = text(
        """
        CREATE OR REPLACE FUNCTION sum_cart_items_qty_func(cart_id UUID, graph_name VARCHAR)
        RETURNS SETOF agtype
        LANGUAGE plpgsql
        AS $function$
        DECLARE sql VARCHAR;
        BEGIN
           sql := format(
           'SELECT * FROM cypher(
                %L,
                $$
                    MATCH (c:Cart {id: %L})-[r:CONTAINS]->(i:CartItem)
                    RETURN coalesce(toFloat(sum(i.qty)), 0) as total_qty
                $$) AS (c agtype);
                ', graph_name, cart_id);
            RETURN QUERY EXECUTE sql;
        END
         $function$;
        """
    )
    op.execute(stmt)


def downgrade() -> None:
    stmt = text("SELECT * FROM ag_catalog.drop_graph(:graph_name, true);")
    op.execute(stmt.bindparams(graph_name=app_config.DB.graph_name))
