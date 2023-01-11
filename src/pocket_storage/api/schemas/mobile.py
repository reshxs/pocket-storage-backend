import uuid
from django.db.models import Q

from pydantic import BaseModel, Field

from pocket_storage import models


class StorageUnitSchema(BaseModel):
    id: uuid.UUID = Field(..., title="ID")
    product_id: uuid.UUID = Field(..., title="ID товара")
    product_name: str = Field(..., title="Название товара")
    product_SKU: str = Field(..., title="SKU товара")
    product_barcode: str | None = Field(None, title="Штрих-код товара (если есть)")
    product_category_id: uuid.UUID = Field(..., title="ID категории товара")
    product_category_name: str = Field(..., title="Название категории товара")
    ext_id: str | None = Field(None, title="Номер ячейки")

    @classmethod
    def from_model(cls, storage_unit: models.StorageUnit):
        return cls(
            id=storage_unit.id,
            product_id=storage_unit.product.id,
            product_name=storage_unit.product.name,
            product_SKU=storage_unit.product.SKU,
            product_barcode=storage_unit.product.barcode,
            product_category_id=storage_unit.product.category.id,
            product_category_name=storage_unit.product.category.name,
            ext_id=storage_unit.ext_id,
        )


class StorageUnitFilters(BaseModel):
    search_query: str | None = Field(None, title="Поисковый запрос")
    product__category__id__in: list[uuid.UUID] | None = Field(
        None,
        title="ID категории товара",
        alias="category_ids",
    )

    def filter_query(self, query: models.QuerySet):
        filter_kwargs = self.dict(exclude_none=True)

        if search_query := filter_kwargs.pop("search_query", None):
            query = query.filter(
                Q(product__name__icontains=search_query)
                | Q(product__SKU__icontains=search_query)
                | Q(product__barcode__icontains=search_query)
                | Q(ext_id__icontains=search_query)
            )

        return query.filter(**filter_kwargs)
