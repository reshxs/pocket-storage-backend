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
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
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
