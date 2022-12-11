import factory
from factory.django import DjangoModelFactory

from . import models

factory.Faker._DEFAULT_LOCALE = 'ru_RU'


class WarehouseFactory(DjangoModelFactory):
    class Meta:
        model = models.Warehouse

    name = factory.Faker('word')
