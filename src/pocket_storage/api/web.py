import django.db
from django.contrib.auth.models import User
from fastapi import Depends, Body
from fastapi_jsonrpc import Entrypoint

from pocket_storage import auth
from pocket_storage import models
from . import errors
from .schemas import web as schemas
from . import dependencies

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
    session = auth.login(username, password)

    if session is None:
        raise errors.WrongCredentials

    return schemas.LoginResponseSchema(
        session_key=session.key,
    )


@api_v1.method(
    tags=["web", "warehouse"],
    summary="Добавить склад",
)
def add_warehouse(
    _: auth.Session = Depends(dependencies.get_session),
    name: str = Body(..., title="Название склада"),
) -> schemas.WarehouseSchema:
    try:
        warehouse = models.Warehouse.objects.create(name=name)
    except django.db.IntegrityError:
        raise errors.WarehouseAlreadyExists

    return schemas.WarehouseSchema.from_model(warehouse)
