import factory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory

from . import models

factory.Faker._DEFAULT_LOCALE = "ru_RU"


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    username = factory.Faker("word")
    password = factory.LazyAttribute(lambda s: make_password(s.raw_password))

    is_active = True
    is_superuser = False
    is_staff = False

    class Params:
        raw_password = "password"


class WarehouseFactory(DjangoModelFactory):
    class Meta:
        model = models.Warehouse

    name = factory.Faker("word")


class ProductCategoryFactory(DjangoModelFactory):
    class Meta:
        model = models.ProductCategory

    name = factory.Faker("word")


class ProductFactory(DjangoModelFactory):
    class Meta:
        model = models.Product

    name = factory.Faker("word")
    SKU = factory.Faker("isbn10")  # TODO: генерировать SKU
    barcode = factory.Faker("ean")
    category = factory.SubFactory(ProductCategoryFactory)


class EmployeePositionFactory(DjangoModelFactory):
    class Meta:
        model = models.EmployeePosition

    name = factory.Faker("word")


class EmployeeFactory(DjangoModelFactory):
    class Meta:
        model = models.Employee

    first_name = factory.Faker("name")
    last_name = factory.Faker("last_name")
    middle_name = factory.Faker("middle_name")
    position = factory.SubFactory(EmployeePositionFactory)


class StorageUnitFactory(DjangoModelFactory):
    class Meta:
        model = models.StorageUnit

    product = factory.SubFactory(ProductFactory)
    warehouse = factory.SubFactory(WarehouseFactory)
    state = models.StorageUnitState.NEW


class StorageUnitOperationFactory(DjangoModelFactory):
    class Meta:
        model = models.StorageUnitOperation

    storage_unit = factory.SubFactory(StorageUnitFactory)
    employee = factory.SubFactory(EmployeeFactory)
    initial_state = models.StorageUnitState.NEW
    final_state = models.StorageUnitState.NEW
