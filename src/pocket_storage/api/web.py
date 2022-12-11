import uuid

import django.db
from django.db import transaction
from fastapi import Depends, Body
from fastapi_jsonrpc import Entrypoint

from pocket_storage import auth
from pocket_storage import models
from . import dependencies
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


@api_v1.method(
    tags=["web", "warehouse"],
    summary="Переименовать склад",
)
def rename_warehouse(
    _: auth.Session = Depends(dependencies.get_session),
    warehouse_id: uuid.UUID = Body(..., title="ID склада", alias="id"),
    new_name: str = Body(..., title="Новое название"),
) -> schemas.WarehouseSchema:
    with transaction.atomic():
        warehouse = models.Warehouse.objects.select_for_update(
            of=("self",), no_key=True
        ).get(id=warehouse_id)
        if warehouse.name != new_name:
            warehouse.name = new_name
            warehouse.save(update_fields=["name"])

    return schemas.WarehouseSchema.from_model(warehouse)


@api_v1.method(
    tags=["web", "warehouse"],
    summary="Получить список складов",
)
def get_warehouses(
    _: auth.Session = Depends(dependencies.get_session),
) -> list[schemas.WarehouseSchema]:
    warehouses = list(models.Warehouse.objects.order_by("name").all())
    return [schemas.WarehouseSchema.from_model(warehouse) for warehouse in warehouses]


@api_v1.method(
    tags=["web", "products"],
    summary="Добавить новую категорию товаров",
)
def add_product_category(
    _: auth.Session = Depends(dependencies.get_session),
    name: str = Body(..., title="Название категории"),
    parent_id: uuid.UUID | None = Body(None, title="ID родительской категории"),
) -> schemas.ProductCategorySchema:
    try:
        category = models.ProductCategory.objects.create(
            name=name,
            parent_id=parent_id,
        )
    except django.db.IntegrityError as exc:
        if "violates unique constraint" in str(exc):
            raise errors.ProductCategoryAlreadyExists
        elif "violates foreign key constraint" in str(exc):
            raise errors.ProductCategoryNotFound
        raise

    return schemas.ProductCategorySchema.from_model(category)
