import django.db
from fastapi_jsonrpc import Entrypoint

from pocket_storage import models
from . import errors
from .schemas import web as schemas

api_v1 = Entrypoint(
    '/api/v1/web/jsonrpc',
    name='web',
    summary='Web JSON_RPC entrypoint',
)


@api_v1.method(
    tags=['web'],
    summary='Добавить склад',
)
def add_warehouse(name: str) -> schemas.WarehouseSchema:
    try:
        warehouse = models.Warehouse.objects.create(name=name)
    except django.db.IntegrityError:
        raise errors.WarehouseAlreadyExists

    return schemas.WarehouseSchema.from_model(warehouse)
