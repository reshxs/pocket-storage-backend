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
