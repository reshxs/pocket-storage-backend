import datetime as dt
import uuid

import pytest
from django.utils import timezone

from pocket_storage import auth
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


@pytest.fixture()
def user_session_key(user, user_raw_password, freezer) -> str:
    session_data = auth.SessionData.from_user_model(user)
    session = auth.DjangoSession.objects.create(
        session_key=uuid.uuid4(),
        session_data=session_data.json(),
        expire_date=timezone.now() + dt.timedelta(hours=3),
    )
    return str(session.session_key)
