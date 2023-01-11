import uuid

import jwt
from fastapi import Depends, Body
from fastapi_jsonrpc import Entrypoint

from . import pagination, dependencies, errors
from .schemas import mobile as schemas
from .. import models
from ..storage_unit_qrcode import parse_qrcode_content

api_v1 = Entrypoint(
    "/api/v1/mobile/jsonrpc",
    name="web",
    summary="Mobile JSON_RPC entrypoint",
)


@api_v1.method(
    tags=["mobile"],
    summary="Получить список единиц хранения",
)
def get_storage_units(
    any_pagination: pagination.AnyPagination = Depends(
        dependencies.get_mutual_exclusive_pagination
    ),
    filters: schemas.StorageUnitFilters = Body(
        schemas.StorageUnitFilters(), title="Фильтрация"
    ),
) -> pagination.PaginatedResponse[schemas.StorageUnitSchema]:
    query = models.StorageUnit.objects.select_related(
        "product", "product__category"
    ).order_by("-product__name", "-ext_id")

    query = filters.filter_query(query)
    paginator = pagination.TypedPaginator(schemas.StorageUnitSchema, query)

    return paginator.get_response(any_pagination)


@api_v1.method(
    tags=["mobile"],
    summary="Получить единицу хранения по ID",
    errors=[
        errors.StorageUnitNotFound,
    ],
)
def get_storage_unit_with_id(
    storage_unit_id: uuid.UUID = Body(..., title="ID единицы хранения", alias="id"),
) -> schemas.StorageUnitSchema:
    storage_unit = models.StorageUnit.objects.select_related(
        "product", "product__category"
    ).get_or_none(id=storage_unit_id)

    if not storage_unit:
        raise errors.StorageUnitNotFound

    return schemas.StorageUnitSchema.from_model(storage_unit)


@api_v1.method(
    tags=["mobile"],
    summary="Получить единицу хранения по содержимому QR-кода",
    errors=[
        errors.StorageUnitNotFound,
    ],
)
def get_storage_unit_with_qrcode(
    qrcode_content: str = Body(..., title="Содержимое QR-кода"),
) -> schemas.StorageUnitSchema:
    try:
        qrcode_payload = parse_qrcode_content(qrcode_content)
    except jwt.exceptions.InvalidTokenError:
        raise errors.StorageUnitNotFound

    storage_unit = models.StorageUnit.objects.select_related(
        "product", "product__category"
    ).get_or_none(id=qrcode_payload.storage_unit_id)

    if not storage_unit:
        raise errors.StorageUnitNotFound

    return schemas.StorageUnitSchema.from_model(storage_unit)


@api_v1.method(
    tags=["mobile"],
    summary="Получить список категорий товаров",
)
def get_product_categories(
    parent_id: uuid.UUID
    | None = Body(None, title="Фильтрация по ID родительской категории"),
) -> list[schemas.ProductCategorySchema]:
    query = models.ProductCategory.objects.select_related("parent")
    if parent_id is not None:
        query = query.filter(parent_id=parent_id)

    categories = list(query.all())
    return [
        schemas.ProductCategorySchema.from_model(category) for category in categories
    ]