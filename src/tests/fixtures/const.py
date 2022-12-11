import pytest
from pocket_storage import factories


@pytest.fixture()
def warehouse():
    return factories.WarehouseFactory.create()
