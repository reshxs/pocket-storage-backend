import uuid

import django.db
import jwt
from django.db import transaction
from fastapi import Depends, Body
from fastapi_jsonrpc import Entrypoint
from django.db.models import Q

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


@api_v1.method(
    tags=["mobile"],
    summary="Изменить номер ячейки для единицы хранения",
    errors=[
        errors.StorageUnitNotFound,
    ],
)
def update_storage_unit_ext_id(
    storage_unit_id: uuid.UUID = Body(..., title="ID единицы хранения"),
    ext_id: str = Body(..., title="Новый номер ячейки"),
) -> schemas.StorageUnitSchema:
    with transaction.atomic():
        storage_unit = models.StorageUnit.objects.select_for_update(
            of=("self",), no_key=True
        ).get_or_none(id=storage_unit_id)
        if not storage_unit:
            raise errors.StorageUnitNotFound

        storage_unit.ext_id = ext_id
        storage_unit.save()

    return schemas.StorageUnitSchema.from_model(storage_unit)


@api_v1.method(
    tags=["mobile"],
    summary="Удалить единицу хранения",
    errors=[
        errors.StorageUnitNotFound,
    ],
)
def delete_storage_unit(
    storage_unit_id: uuid.UUID = Body(..., title="ID единицы хранения")
) -> bool:
    """Всегда возвращает либо True, либо одну из возможных ошибок."""
    with transaction.atomic():
        storage_unit = models.StorageUnit.objects.select_for_update(
            of=("self",), no_key=True
        ).get_or_none(id=storage_unit_id)
        if not storage_unit:
            raise errors.StorageUnitNotFound

        storage_unit.delete()

    return True


@api_v1.method(
    tags=["mobile"],
    summary="Получить список товаров",
)
def get_products(
    any_pagination: pagination.AnyPagination = Depends(
        dependencies.get_mutual_exclusive_pagination
    ),
    search_str: str
    | None = Body(
        None,
        title="Поисковый запрос",
        description="Поиск по названию, SKU и штрих-коду товара",
        alias="search",
    ),
) -> pagination.PaginatedResponse[schemas.ProductSchema]:
    query = models.Product.objects.order_by("name")
    if search_str:
        query = query.filter(
            Q(
                Q(name__icontains=search_str)
                | Q(SKU__icontains=search_str)
                | Q(barcode__icontains=search_str)
            ),
        )

    paginator = pagination.TypedPaginator(schemas.ProductSchema, query)
    return paginator.get_response(any_pagination)


@api_v1.method(
    tags=["mobile"],
    summary="Создать единицу хранения с id товара",
    errors=[errors.ProductNotFound, errors.StorageUnitAlreadyExists],
)
def create_storage_unit_with_product_id(
    product_id: uuid.UUID = Body(..., title="ID товара"),
    ext_id: str = Body(..., title="Номер ячейки"),
) -> schemas.StorageUnitSchema:
    product = models.Product.objects.get_or_none(id=product_id)
    if not product:
        raise errors.ProductNotFound

    # TODO: с этим надо аккуратно
    warehouse = models.Warehouse.objects.first()

    try:
        storage_unit = models.StorageUnit.objects.create(
            product=product, warehouse=warehouse, ext_id=ext_id
        )
    except django.db.IntegrityError:
        raise errors.StorageUnitAlreadyExists

    return schemas.StorageUnitSchema.from_model(storage_unit)


@api_v1.method(
    tags=["mobile"],
    summary="Создать единицу хранения по штрих-коду товара",
    errors=[errors.ProductNotFound, errors.StorageUnitAlreadyExists],
)
def create_storage_unit_with_product_barcode(
    barcode: str = Body(..., title="Штрих-код товара"),
    ext_id: str = Body(..., title="Номер ячейки"),
) -> schemas.StorageUnitSchema:
    product = models.Product.objects.get_or_none(barcode=barcode)
    if not product:
        raise errors.ProductNotFound

    # TODO: с этим надо аккуратно
    warehouse = models.Warehouse.objects.first()

    try:
        storage_unit = models.StorageUnit.objects.create(
            product=product, warehouse=warehouse, ext_id=ext_id
        )
    except django.db.IntegrityError:
        raise errors.StorageUnitAlreadyExists

    return schemas.StorageUnitSchema.from_model(storage_unit)
