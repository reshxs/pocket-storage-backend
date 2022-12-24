import uuid

import django.db
from django.db import transaction
from django.utils import timezone
from fastapi import Depends, Body
from fastapi_jsonrpc import Entrypoint

from pocket_storage import auth
from pocket_storage import models
from . import dependencies
from . import errors
from . import pagination
from .schemas import web as schemas

api_v1 = Entrypoint(
    "/api/v1/web/jsonrpc",
    name="web",
    summary="Web JSON_RPC entrypoint",
    errors=[
        errors.AccessDenied,
    ],
)


@api_v1.method(
    tags=["web", "auth"],
    summary="Войти",
    errors=[
        errors.WrongCredentials,
    ],
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
    errors=[
        errors.WarehouseAlreadyExists,
    ],
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
    # FIXME: catch warehouse not found
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
    # FIXME: catch warehouse not found
    warehouses = list(models.Warehouse.objects.order_by("name").all())
    return [schemas.WarehouseSchema.from_model(warehouse) for warehouse in warehouses]


@api_v1.method(
    tags=["web", "products"],
    summary="Добавить новую категорию товаров",
    errors=[
        errors.ProductCategoryNotFound,
        errors.ProductCategoryAlreadyExists,
    ],
)
def add_product_category(
    _: auth.Session = Depends(dependencies.get_session),
    name: str = Body(..., title="Название категории"),
    parent_id: uuid.UUID | None = Body(None, title="ID родительской категории"),
) -> schemas.ProductCategorySchema:
    if parent_id:
        try:
            parent = models.ProductCategory.objects.get(id=parent_id)
        except models.ProductCategory.DoesNotExist:
            raise errors.ProductCategoryNotFound
    else:
        parent = None

    try:
        category = models.ProductCategory.objects.create(
            name=name,
            parent=parent,
        )
    except django.db.IntegrityError as exc:
        if "violates unique constraint" in str(exc):
            raise errors.ProductCategoryAlreadyExists
        raise

    return schemas.ProductCategorySchema.from_model(category)


@api_v1.method(
    tags=["web", "products"],
    summary="Переименовать категорию товаров",
    errors=[
        errors.ProductCategoryNotFound,
    ],
)
def rename_product_category(
    _: auth.Session = Depends(dependencies.get_session),
    category_id: uuid.UUID = Body(..., title="ID категории товаров", alias="id"),
    new_name: str = Body(..., title="Название категории"),
) -> schemas.ProductCategorySchema:
    with transaction.atomic():
        try:
            category = (
                models.ProductCategory.objects.select_for_update(
                    of=("self",), no_key=True
                )
                .select_related("parent")
                .get(id=category_id)
            )
        except models.ProductCategory.DoesNotExist:
            raise errors.ProductCategoryNotFound

        if new_name != category.name:
            category.name = new_name
            try:
                category.save()
            except django.db.IntegrityError:
                raise errors.ProductCategoryAlreadyExists

    return schemas.ProductCategorySchema.from_model(category)


@api_v1.method(
    tags=["web", "products"],
    summary="Получить список категорий товаров",
)
def get_product_categories(
    _: auth.Session = Depends(dependencies.get_session),
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
    tags=["web", "products"],
    summary="Добавить товар",
    errors=[
        errors.ProductAlreadyExists,
        errors.ProductCategoryNotFound,
    ],
)
def add_product(
    _: auth.Session = Depends(dependencies.get_session),
    product_data: schemas.ProductCreateSchema = Body(
        ..., title="Данные для создания товара"
    ),
) -> schemas.ProductSchema:
    try:
        category = models.ProductCategory.objects.get(id=product_data.category_id)
    except models.ProductCategory.DoesNotExist:
        raise errors.ProductCategoryNotFound

    try:
        product = models.Product.objects.create(
            name=product_data.name,
            SKU=product_data.SKU,
            barcode=product_data.barcode,
            category=category,
        )
    except django.db.IntegrityError as exc:
        if "violates unique constraint" in str(exc):
            raise errors.ProductAlreadyExists
        raise

    return schemas.ProductSchema.from_model(product)


@api_v1.method(
    tags=["web", "products"],
    summary="Редактировать товар",
    errors=[
        errors.ProductNotFound,
        errors.ProductAlreadyExists,
        errors.ProductCategoryNotFound,
    ],
)
def update_product(
    _: auth.Session = Depends(dependencies.get_session),
    product_id: uuid.UUID = Body(..., title="ID товара", alias="id"),
    product_data: schemas.ProductUpdateSchema = Body(
        ..., title="Данные для изменения товара"
    ),
) -> schemas.ProductSchema:
    update_kwargs = product_data.dict(exclude_none=True)
    with transaction.atomic():
        try:
            product = (
                models.Product.objects.select_for_update(of=("self",), no_key=True)
                .select_related("category")
                .get(id=product_id)
            )
        except models.Product.DoesNotExist:
            raise errors.ProductNotFound

        if update_kwargs:
            category_id = update_kwargs.pop("category_id", None)
            if category_id is not None:
                try:
                    category = models.ProductCategory.objects.get(id=category_id)
                except models.ProductCategory.DoesNotExist:
                    raise errors.ProductCategoryNotFound

                product.category = category

            for k, v in update_kwargs.items():
                setattr(product, k, v)

            product.updated_at = timezone.now()

            try:
                product.save(
                    update_fields=[
                        "name",
                        "SKU",
                        "barcode",
                        "category_id",
                        "updated_at",
                    ]
                )
            except django.db.IntegrityError as exc:
                if "violates unique constraint" in str(exc):
                    raise errors.ProductAlreadyExists
                raise

    return schemas.ProductSchema.from_model(product)


@api_v1.method(
    tags=["web", "products"],
    summary="Получить товар по ID",
)
def get_product(
    _: auth.Session = Depends(dependencies.get_session),
    product_id: uuid.UUID = Body(..., title="ID товара", alias="id"),
) -> schemas.ProductSchema:
    try:
        product = models.Product.objects.select_related("category").get(id=product_id)
    except models.Product.DoesNotExist:
        raise errors.ProductNotFound

    return schemas.ProductSchema.from_model(product)


@api_v1.method(
    tags=["web", "product"],
    summary="Получить список продуктов",
)
def get_products(
    _: auth.Session = Depends(dependencies.get_session),
    any_pagination: pagination.AnyPagination = Depends(
        dependencies.get_mutual_exclusive_pagination
    ),
    filters: schemas.ProductFilters = Body(
        schemas.ProductFilters(), title="Фильтрация"
    ),
) -> pagination.PaginatedResponse[schemas.ProductSchema]:
    query = filters.filter_query(models.Product.objects.all())

    paginator = pagination.TypedPaginator(schemas.ProductSchema, query)
    return paginator.get_response(any_pagination)


@api_v1.method(
    tags=["web", "employees"],
    summary="Добавить должность сотрудника",
    errors=[
        errors.EmployeePositionAlreadyExists,
    ],
)
def add_employee_position(
    _: auth.Session = Depends(dependencies.get_session),
    name: str = Body(..., title="Название должности"),
) -> schemas.EmployeePositionSchema:
    try:
        created_position = models.EmployeePosition.objects.create(name=name)
    except django.db.IntegrityError as exc:
        if "violates unique constraint" in str(exc):
            raise errors.EmployeePositionAlreadyExists
        raise

    return schemas.EmployeePositionSchema.from_model(created_position)


@api_v1.method(
    tags=["web", "employees"],
    summary="Получить список должностей",
)
def get_employee_positions(
    _: auth = Depends(dependencies.get_session),
) -> list[schemas.EmployeePositionSchema]:
    positions = list(models.EmployeePosition.objects.all())
    return [
        schemas.EmployeePositionSchema.from_model(position) for position in positions
    ]


@api_v1.method(
    tags=["web", "employees"],
    summary="Добавить сотрудника",
    errors=[
        errors.EmployeePositionNotFound,
    ],
)
def add_employee(
    _: auth.Session = Depends(dependencies.get_session),
    employee_data: schemas.CreateEmployeeSchema = Body(
        ..., title="Данные нового сотрудника"
    ),
) -> schemas.EmployeeSchema:
    employee_data = employee_data.dict()

    position_id = employee_data.pop("position_id")
    position = models.EmployeePosition.objects.get_or_none(id=position_id)

    if not position:
        raise errors.EmployeePositionNotFound

    employee = models.Employee.objects.create(
        **employee_data,
        position=position,
    )

    return schemas.EmployeeSchema.from_model(employee)


@api_v1.method(
    tags=["web", "employees"],
    summary="Получить сотрудника по ID",
    errors=[
        errors.EmployeeNotFound,
    ],
)
def get_employee(
    _: auth.Session = Depends(dependencies.get_session),
    employee_id: uuid.UUID = Body(..., title="ID сотрудника"),
) -> schemas.EmployeeSchema:
    employee = models.Employee.objects.select_related("position").get_or_none(
        id=employee_id
    )

    if not employee:
        raise errors.EmployeeNotFound

    return schemas.EmployeeSchema.from_model(employee)


@api_v1.method(
    tags=["web", "employees"],
    summary="Получить список сотрудников",
)
def get_employees(
    _: auth.Session = Depends(dependencies.get_session),
    any_pagination: pagination.AnyPagination = Depends(
        dependencies.get_mutual_exclusive_pagination
    ),
    filters: schemas.EmployeeFilters = Body(
        schemas.EmployeeFilters(), title="Фильтрация"
    ),
) -> pagination.PaginatedResponse[schemas.EmployeeSchema]:
    query = models.Employee.objects.select_related("position").order_by(
        "last_name", "first_name", "middle_name"
    )
    query = filters.filter_query(query)

    paginator = pagination.TypedPaginator(schemas.EmployeeSchema, query)
    return paginator.get_response(any_pagination)


@api_v1.method(
    tags=["web", "employees"],
    summary="Изменить сотрудника",
    errors=[
        errors.EmployeeNotFound,
        errors.EmployeePositionNotFound,
    ],
)
def update_employee(
    _: auth.Session = Depends(dependencies.get_session),
    employee_id: uuid.UUID = Body(..., title="ID сотрудника"),
    employee_data: schemas.UpdateEmployeeSchema = Body(
        ..., title="Данные для изменения сотрудника"
    ),
) -> schemas.EmployeeSchema:
    with transaction.atomic():
        employee = models.Employee.objects.select_for_update(of=("self",)).get_or_none(
            id=employee_id
        )

        if not employee:
            raise errors.EmployeeNotFound

        employee_data = employee_data.dict(exclude_none=True)
        _update_fields = []

        position_id = employee_data.pop("position_id", None)
        if position_id:
            position = models.EmployeePosition.objects.get_or_none(id=position_id)
            if not position:
                raise errors.EmployeePositionNotFound

            employee.position = position
            _update_fields.append("position")

        for key, value in employee_data.items():
            setattr(employee, key, value)
            _update_fields.append(key)

        employee.save()

    return schemas.EmployeeSchema.from_model(employee)


@api_v1.method(
    tags=["web", "products"],
    summary="Получить список единиц хранения продукта",
    errors=[errors.ProductNotFound],
)
def get_storage_units(
    _: auth.Session = Depends(dependencies.get_session),
    any_pagination: pagination.AnyPagination = Depends(
        dependencies.get_mutual_exclusive_pagination
    ),
    product_id: uuid.UUID = Body(..., title="ID товара"),
    filters: schemas.StorageUnitFilters = Body(
        schemas.StorageUnitFilters(), title="Фильтрация"
    ),
) -> pagination.PaginatedResponse[schemas.StorageUnitSchema]:
    product = models.Product.objects.get_or_none(id=product_id)
    if not product:
        raise errors.ProductNotFound

    query = (
        models.StorageUnit.objects.select_related("product", "warehouse")
        .order_by("warehouse", "-updated_at")
        .filter(product_id=product_id)
    )
    query = filters.filter_query(query)

    paginator = pagination.TypedPaginator(schemas.StorageUnitSchema, query)
    return paginator.get_response(any_pagination)


@api_v1.method(
    tags=["web", "products"],
    summary="Получить список действий с единицей хранения товара",
    errors=[errors.StorageUnitNotFound],
)
def get_storage_unit_operations(
    _: auth.Session = Depends(dependencies.get_session),
    any_pagination: pagination.AnyPagination = Depends(
        dependencies.get_mutual_exclusive_pagination
    ),
    storage_unit_id: uuid.UUID = Body(..., title="ID единицы хранения"),
) -> pagination.PaginatedResponse[schemas.StorageUnitOperationSchema]:
    storage_unit = models.StorageUnit.objects.get_or_none(id=storage_unit_id)
    if not storage_unit:
        raise errors.StorageUnitNotFound

    query = models.StorageUnitOperation.objects.filter(
        storage_unit=storage_unit,
    ).order_by("-created_at")
    paginator = pagination.TypedPaginator(schemas.StorageUnitOperationSchema, query)
    return paginator.get_response(any_pagination)
