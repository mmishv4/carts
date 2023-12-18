from decimal import Decimal

import pytest

from app.domain.cart_items.dto import ItemDTO
from app.domain.cart_items.entities import CartItem
from tests.environment.unit_of_work import TestUow
from tests.utils import fake


@pytest.fixture()
def item_id() -> int:
    return fake.numeric.integer_number(start=1, end=99)


@pytest.fixture()
async def existing_item(uow: TestUow, item_id: int) -> CartItem:
    item = CartItem(
        data=ItemDTO(id=item_id, name=fake.text.word(), qty=Decimal(1), price=Decimal(1))
    )

    async with uow(autocommit=True):
        await uow.items.create_item(item)

    return item
