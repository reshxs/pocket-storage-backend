import typing as tp
from base64 import b64encode
from . import storage_unit_qrcode

from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from pocket_storage import models

_AdminActionT = tp.TypeVar("_AdminActionT", bound=tp.Callable[..., object])

admin.site.index_title = "Pocket storage"
admin.site.site_header = "Pocket storage"


class _AdminActionAttrs(tp.Protocol[_AdminActionT]):
    short_description: str | None
    __call__: _AdminActionT


def admin_attrs(
    short_description: str | None = None,
    boolean: bool | None = None,
):
    def inner(func: _AdminActionT) -> _AdminActionAttrs[_AdminActionT]:
        func_ = tp.cast(_AdminActionAttrs[_AdminActionT], func)
        if short_description is not None:
            func_.short_description = short_description

        if boolean is not None:
            func_.boolean = boolean

        return func_

    return inner


class ParentProductCategoryLinkMixin(object):
    @admin_attrs(short_description="Родительская категория")
    def parent_link(self, obj):
        if obj.parent is None:
            return format_html("")

        link = reverse(
            "admin:pocket_storage_productcategory_change", args=[obj.parent_id]
        )
        return format_html(f'<a href="{link}">{obj.parent.name}</a>')


class ProductCategoryLinkMixin(object):
    @admin_attrs(short_description="Категория")
    def category_link(self, obj):
        if obj.category is None:
            return format_html("")

        link = reverse(
            "admin:pocket_storage_productcategory_change", args=[obj.category_id]
        )
        return format_html(f'<a href="{link}">{obj.category.name}</a>')


class ProductLinkMixin(object):
    @admin_attrs(short_description="Товар")
    def product_link(self, obj):
        link = reverse(
            "admin:pocket_storage_product_change", args=[obj.product_id]
        )
        return format_html(f'<a href="{link}">{obj.product.name}</a>')


class WarehouseLinkMixin(object):
    @admin_attrs(short_description="Склад")
    def warehouse_link(self, obj):
        link = reverse(
            "admin:pocket_storage_warehouse_change", args=[obj.warehouse_id]
        )
        return format_html(f'<a href="{link}">{obj.warehouse.name}</a>')


class ProductCategoryParentFilter(AutocompleteFilter):
    title = "Родительская категория"
    field_name = "parent"


class ProductCategoryFilter(AutocompleteFilter):
    title = "Категория"
    field_name = "category"


class ProductFilter(AutocompleteFilter):
    title = "Товар"
    field_name = "product"


class WarehouseFilter(AutocompleteFilter):
    title = "Склад"
    field_name = "warehouse"


@admin.register(models.Warehouse)
class WarehouseModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(models.ProductCategory)
class ProductCategoryModelAdmin(ParentProductCategoryLinkMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "id",
        "parent_link",
    )
    list_display_links = ("name",)
    search_fields = ("id", "name", "parent__name")
    list_filter = [ProductCategoryParentFilter]


@admin.register(models.Product)
class ProductModelAdmin(ProductCategoryLinkMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "SKU",
        "barcode",
        "category_link",
    )
    search_fields = (
        "id",
        "name",
        "SKU",
        "barcode",
    )
    list_filter = (
        ProductCategoryFilter,
    )


def image_from_bytes(image_content: tp.Union[bytes, memoryview]) -> str:
    b64_content = b64encode(image_content).decode('utf8')
    return mark_safe(f'<img src = "data: image/png; base64, {b64_content}">')  # noqa


@admin.register(models.StorageUnit)
class StorageUnitModelAdmin(
    ProductLinkMixin,
    WarehouseLinkMixin,
    admin.ModelAdmin,
):
    list_display = (
        "id",
        "ext_id",
        "product_link",
        "warehouse_link",
    )

    search_fields = (
        "id",
        "ext_id",
        "product__name",
        "product__SKU",
        "product__barcode",
    )

    readonly_fields = ('qrcode_img',)

    list_filter = (
        ProductFilter,
        WarehouseFilter,
    )

    @admin.display(description='QR-код')
    def qrcode_img(self, obj: models.StorageUnit) -> tp.Optional[str]:
        content = storage_unit_qrcode.make_qrcode(obj)

        return image_from_bytes(content)
