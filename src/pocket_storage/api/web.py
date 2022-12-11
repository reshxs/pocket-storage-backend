import datetime as dt
import uuid

import django.db
import simplejson as json
from django.contrib.auth import authenticate
from django.contrib.sessions.models import Session
from django.utils import timezone
from fastapi_jsonrpc import Entrypoint

from pocket_storage import models
from . import errors
from .schemas import web as schemas

api_v1 = Entrypoint(
    "/api/v1/web/jsonrpc",
    name="web",
    summary="Web JSON_RPC entrypoint",
)


@api_v1.method(
    tags=["web", "auth"],
    summary="Войти",
)
def login(username: str, password: str) -> schemas.LoginResponseSchema:
    # TODO: вынести в отдельный модуль
    user = authenticate(username=username, password=password)

    if user is None:
        raise errors.WrongCredentials

    session = Session.objects.create(
        session_key=uuid.uuid4(),
        session_data=json.dumps(
            {
                'user_id': user.id,  # TODO: типизировать
            },
        ),
        expire_date=timezone.now() + dt.timedelta(hours=3),
    )

    return schemas.LoginResponseSchema(
        session_key=session.session_key,
        user=schemas.UserSchema.from_model(user),
    )


@api_v1.method(
    tags=["web", "warehouse"],
    summary="Добавить склад",
)
def add_warehouse(name: str) -> schemas.WarehouseSchema:
    try:
        warehouse = models.Warehouse.objects.create(name=name)
    except django.db.IntegrityError:
        raise errors.WarehouseAlreadyExists

    return schemas.WarehouseSchema.from_model(warehouse)
