import datetime as dt
import uuid

from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector
from pydantic import BaseModel
from pydantic import Field
from django.db.models import Q

from pocket_storage import models


class UserSchema(BaseModel):
    id: int = Field(..., title="ID")
    username: str = Field(..., title="Имя пользователя, используемое для входа")
    first_name: str = Field(..., title="Имя")
    last_name: str = Field(..., title="Фамилия")

    @classmethod
    def from_model(cls, user: User):
        return cls(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )


class LoginResponseSchema(BaseModel):
    session_key: uuid.UUID = Field(
        ...,
        title="Ключ сессии",
        description="Передается в заголовке X-session-key",
    )


class WarehouseSchema(BaseModel):
    """Склад."""

    id: uuid.UUID = Field(..., title="ID склада")
    name: str = Field(..., title="Название склада")

    @classmethod
    def from_model(cls, warehouse: models.Warehouse):
        return cls(id=warehouse.id, name=warehouse.name)


class ProductCategorySchema(BaseModel):
    """Категория товара."""

    id: uuid.UUID = Field(..., title="ID")
    name: str = Field(..., title="Название категории")
    parent_id: uuid.UUID | None = Field(..., title="ID родительской категории")

    @classmethod
    def from_model(cls, category: models.ProductCategory):
        return cls(
            id=category.id,
            name=category.name,
            parent_id=category.parent_id,
        )


class ProductCreateSchema(BaseModel):
    name: str = Field(..., title="Название товара")
    SKU: str = Field(..., title="SKU товара")
    barcode: str | None = Field(None, title="Штрих-код товара (если есть)")
    category_id: uuid.UUID | None = Field(None, title="ID категории товара")


class ProductUpdateSchema(BaseModel):
    name: str | None = Field(None, title="Название товара")
    SKU: str | None = Field(None, title="SKU товара")
    barcode: str | None = Field(None, title="Штрих-код товара (если есть)")
    category_id: uuid.UUID | None = Field(None, title="ID категории товара")


class ProductSchema(BaseModel):
    id: uuid.UUID = Field(..., title="ID")
    name: str = Field(..., title="Название товара")
    SKU: str = Field(..., title="SKU товара")
    barcode: str | None = Field(None, title="Штрих-код товара (если есть)")
    category: ProductCategorySchema | None = Field(None, title="Категория товара")

    @classmethod
    def from_model(cls, product: models.Product):
        return cls(
            id=product.id,
            name=product.name,
            SKU=product.SKU,
            barcode=product.barcode,
            category=ProductCategorySchema.from_model(product.category),
        )


class ShortProductSchema(BaseModel):
    id: uuid.UUID = Field(..., title="ID")
    name: str = Field(..., title="Название товара")

    @classmethod
    def from_model(cls, product: models.Product):
        return cls(
            id=product.id,
            name=product.name,
        )


class ProductFilters(BaseModel):
    search_str: str | None = Field(
        None,
        title="Поисковый запрос",
        description="Поиск по названию, SKU и штрих-коду товара",
        alias="search",
    )
    category_id: uuid.UUID | None = Field(
        None,
        title="Фильтр по категории",
        description="На данный момент не работает с родительскими категориями",
    )

    def filter_query(self, query: models.QuerySet):
        if self.search_str:
            query = query.filter(
                Q(
                    Q(name__icontains=self.search_str)
                    | Q(SKU__icontains=self.search_str)
                    | Q(barcode__icontains=self.search_str)
                ),
            )

        if self.category_id:
            query = query.filter(category_id=self.category_id)

        return query


class EmployeePositionSchema(BaseModel):
    id: uuid.UUID = Field(..., title="ID должности")
    name: str = Field(..., title="Название дложности")

    @classmethod
    def from_model(cls, position: models.EmployeePosition):
        return cls(
            id=position.id,
            name=position.name,
        )


class CreateEmployeeSchema(BaseModel):
    first_name: str = Field(..., title="Имя")
    last_name: str = Field(..., title="Фамилия")
    middle_name: str | None = Field(None, title="Отчество")
    position_id: uuid.UUID = Field(..., title="ID должности")


class EmployeeSchema(BaseModel):
    id: uuid.UUID = Field(..., title="ID сотрудника")
    first_name: str = Field(..., title="Имя")
    last_name: str = Field(..., title="Фамилия")
    middle_name: str | None = Field(None, title="Отчество")
    position: EmployeePositionSchema = Field(..., title="Должность")

    @classmethod
    def from_model(cls, employee: models.Employee):
        return cls(
            id=employee.id,
            first_name=employee.first_name,
            last_name=employee.last_name,
            middle_name=employee.middle_name,
            position=EmployeePositionSchema.from_model(employee.position),
        )


class EmployeeFilters(BaseModel):
    full_name_search: str | None = Field(
        None, title="Поиск по имени", alias="full_name_search"
    )
    position_id__in: list[uuid.UUID] | None = Field(
        None, title="Фильтрация по должности", alias="position_ids"
    )

    def filter_query(self, query: models.QuerySet):
        if self.full_name_search:
            query = query.annotate(
                full_name_search=SearchVector("first_name", "last_name", "middle_name"),
            )

        return query.filter(
            **self.dict(exclude_none=True),
        )


class UpdateEmployeeSchema(BaseModel):
    first_name: str | None = Field(None, title="Имя")
    last_name: str | None = Field(None, title="Фамилия")
    middle_name: str | None = Field(None, title="Отчество")
    position_id: uuid.UUID | None = Field(None, title="ID должности")


class StorageUnitFilters(BaseModel):
    warehouse_id__in: list[uuid.UUID] | None = Field(None, title='ID складов', alias='warehouse_ids')
    state__in: list[models.StorageUnitState] | None = Field(None, title='Состояния', alias='states')
    created_at__gte: dt.datetime | None = Field(None, title='Создано после')
    created_at__lte: dt.datetime | None = Field(None, title='Создано до')
    updated_at__gte: dt.datetime | None = Field(None, title='Обновлено до')
    updated_at__lte: dt.datetime | None = Field(None, title='Обновлено после')

    def filter_query(self, query: models.QuerySet):
        filter_kwargs = self.dict(exclude_none=True)
        return query.filter(**filter_kwargs)


class StorageUnitSchema(BaseModel):
    id: uuid.UUID = Field(..., title='ID единицы хранения')
    product: ShortProductSchema = Field(..., title='Товар')
    warehouse: WarehouseSchema = Field(..., title='Склад')
    state: models.StorageUnitState = Field(..., title='Состояние')
    created_at: dt.datetime = Field(..., title='Создано', description='Дата/Время создания записи')
    updated_at: dt.datetime | None = Field(..., title='Обновлено', description='Дата/Время обновления записи')

    @classmethod
    def from_model(cls, storage_unit: models.StorageUnit):
        return cls(
            id=storage_unit.id,
            product=ShortProductSchema.from_model(storage_unit.product),
            warehouse=WarehouseSchema.from_model(storage_unit.warehouse),
            state=storage_unit.state,
            created_at=storage_unit.created_at,
            updated_at=storage_unit.updated_at,
        )
