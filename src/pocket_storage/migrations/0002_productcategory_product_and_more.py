# Generated by Django 4.1.3 on 2022-12-22 05:59

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("pocket_storage", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProductCategory",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(max_length=32, verbose_name="Название")),
                (
                    "parent",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="pocket_storage.productcategory",
                        verbose_name="Родительская категория",
                    ),
                ),
            ],
            options={
                "verbose_name": "Категория товара",
                "verbose_name_plural": "Категории товара",
            },
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, primary_key=True, serialize=False
                    ),
                ),
                ("name", models.CharField(max_length=256, verbose_name="Название")),
                (
                    "SKU",
                    models.CharField(max_length=24, unique=True, verbose_name="SKU"),
                ),
                (
                    "barcode",
                    models.CharField(
                        blank=True,
                        max_length=24,
                        null=True,
                        unique=True,
                        verbose_name="Штрих-код",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        blank=True,
                        help_text="Дата/Время изменения записи",
                        null=True,
                        verbose_name="Изменен",
                    ),
                ),
                (
                    "crated_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Дата/Время добавления записи",
                        verbose_name="Создан",
                    ),
                ),
                (
                    "category",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.RESTRICT,
                        to="pocket_storage.productcategory",
                        verbose_name="Категория",
                    ),
                ),
            ],
            options={
                "verbose_name": "Товар",
                "verbose_name_plural": "Товары",
            },
        ),
        migrations.AddConstraint(
            model_name="productcategory",
            constraint=models.UniqueConstraint(
                fields=("name", "parent_id"),
                name="product_category__unique_name_in_parent_scope",
            ),
        ),
        migrations.AddConstraint(
            model_name="productcategory",
            constraint=models.UniqueConstraint(
                condition=models.Q(("parent_id__isnull", True)),
                fields=("name",),
                name="product_category__unique_name_in_root_scope",
            ),
        ),
    ]
