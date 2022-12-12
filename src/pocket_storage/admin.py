import typing as tp

from admin_auto_filters.filters import AutocompleteFilter
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

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


@admin.register(models.Warehouse)
class WarehouseModelAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


class ProductCategoryParentFilter(AutocompleteFilter):
    title = "Родительская категория"
    field_name = "parent"


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
