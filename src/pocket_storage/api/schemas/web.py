import uuid

from django.contrib.auth.models import User
from pydantic import BaseModel
from pydantic import Field

from pocket_storage import models


class UserSchema(BaseModel):
    id: int = Field(..., title="ID")
    username: str = Field(..., title="Имя пользователя, используемое для входа")
    first_name: str = Field(..., title="Имя")
    last_name: str = Field(..., title="Фамилия")

    @classmethod
    def from_model(cls, user: User):
        return cls(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
        )


class LoginResponseSchema(BaseModel):
    session_key: uuid.UUID = Field(
        ...,
        title="Ключ сессии",
        description="Используется авторизации",
    )
    user: UserSchema = Field(..., title="Данные пользователя")


class WarehouseSchema(BaseModel):
    """Склад."""

    id: uuid.UUID = Field(..., title="ID склада")
    name: str = Field(..., title="Название склада")

    @classmethod
    def from_model(cls, warehouse: models.Warehouse):
        return cls(id=warehouse.id, name=warehouse.name)
