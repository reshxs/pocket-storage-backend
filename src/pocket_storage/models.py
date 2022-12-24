import uuid

from django.db import models
from django.utils import timezone


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

    def __str__(self):
        return self.name


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
        max_length=24,
        unique=True,
    )
    barcode = models.CharField(
        "Штрих-код",
        max_length=24,
        unique=True,
        null=True,
        blank=True,
    )

    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.RESTRICT,
        verbose_name="Категория",
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


class EmployeePosition(BaseModel):
    """Должность сотрудника."""

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности сотрудника"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )
    name = models.CharField(
        "Название",
        max_length=50,
        unique=True,
    )


class Employee(BaseModel):
    """Сотрудник склада."""

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )
    first_name = models.CharField("Имя", max_length=50)
    last_name = models.CharField(
        "Фамилия",
        max_length=50,
    )
    middle_name = models.CharField(
        "Отчество",
        max_length=50,
        null=True,
        blank=True,
    )
    position = models.ForeignKey(
        EmployeePosition,
        on_delete=models.RESTRICT,
        verbose_name="Должность",
    )


class StorageUnitState(models.TextChoices):
    NEW = "new", "новая"


class StorageUnit(BaseModel):
    """Единица хранения."""

    class Meta:
        verbose_name = "Единица хранения"
        verbose_name_plural = "Единицы хранения"

    State = StorageUnitState

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )
    Product = models.ForeignKey(
        Product,
        verbose_name="Товар",
        on_delete=models.RESTRICT,
        related_name="storage_units",
    )
    Warehouse = models.ForeignKey(
        Warehouse,
        verbose_name="Склад",
        on_delete=models.RESTRICT,
        related_name="storage_units",
    )

    state = models.CharField(
        "Состояние",
        max_length=32,
        choices=State.choices,
        default=State.NEW,
    )

    updated_at = models.DateTimeField(
        "Обновлено",
        null=True,
        blank=True,
        help_text="Дата/Время обновления записи",
    )
    created_at = models.DateTimeField(
        "Создано",
        default=timezone.now,
        help_text="Дата/Время создания записи",
    )


class StorageUnitOperation(BaseModel):
    """Действие с единицей хранения."""

    class Meta:
        verbose_name = "Действие с единицей хранения"
        verbose_name_plural = "Действия с единицей хранения"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
    )
    storage_unit = models.ForeignKey(
        StorageUnit,
        on_delete=models.CASCADE,
        verbose_name="Единица хранения",
        related_name="operations",
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.RESTRICT,
        verbose_name="Сотрудник",
        related_name="operations",
        help_text="Сотрудник, совершивший действие",
    )
    initial_state = models.CharField(
        "Начальное состояние",
        max_length=32,
        choices=StorageUnitState.choices,
        help_text="Состояние единицы хранения до совершения действия",
    )
    final_state = models.CharField(
        "Конечное состояние",
        max_length=32,
        choices=StorageUnitState.choices,
        help_text="Состояние единицы хранения после совершения действия",
    )
    created_at = models.DateTimeField(
        "Создано",
        default=timezone.now,
        help_text="Дата/Время совершения действия",
    )
