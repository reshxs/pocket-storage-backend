from django.contrib import admin

from pocket_storage import models


@admin.register(models.Warehouse)
class WarehouseModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)