import pytest
from pocket_storage import factories


@pytest.fixture()
def warehouse():
    return factories.WarehouseFactory.create()


@pytest.fixture()
def user_raw_password():
    return "password"


@pytest.fixture()
def user(user_raw_password):
    return factories.UserFactory.create(raw_password=user_raw_password)
