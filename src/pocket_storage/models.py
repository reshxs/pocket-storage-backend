import uuid

from django.db import models


class QuerySet(models.QuerySet):
    def get_or_none(self, **kwargs):
        try:
            return self.get(**kwargs)
        except models.ObjectDoesNotExist:
            return None


class BaseModel(models.Model):
    objects = QuerySet.as_manager()

    class Meta:
        abstract = True


class Warehouse(BaseModel):
    """Склад."""

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )
    name = models.CharField(
        "Название",
        max_length=128,
        unique=True,
    )


class ProductCategory(BaseModel):
    """Категория товара."""

    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товара"

        constraints = [
            models.UniqueConstraint(
                fields=("name", "parent_id"),
                name="product_category__unique_name_in_parent_scope",
            ),
            models.UniqueConstraint(
                fields=("name",),
                condition=models.Q(parent_id__isnull=True),
                name="product_category__unique_name_in_root_scope",
            ),
        ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )
    name = models.CharField(
        "Название",
        max_length=32,
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        verbose_name="Родительская категория",
        null=True,
        blank=True,
    )


class Product(BaseModel):
    """Товар."""

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )
    name = models.CharField(
        "Название",
        max_length=256,
    )
    SKU = models.CharField(
        "SKU",
        max_length=16,
        unique=True,
    )
    barcode = models.IntegerField(
        "Штрих-код",
        unique=True,
        null=True,
        blank=True,
    )

    updated_at = models.DateTimeField(
        "Изменен",
        null=True,
        blank=True,
        help_text="Дата/Время изменения записи",
    )
    crated_at = models.DateTimeField(
        "Создан",
        auto_now_add=True,
        help_text="Дата/Время добавления записи",
    )
