import uuid

from django.contrib.auth.models import User
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
