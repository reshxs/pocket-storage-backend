import uuid

from pydantic import BaseModel
from pydantic import Field

from pocket_storage import models


class WarehouseSchema(BaseModel):
    """Склад."""
    id: uuid.UUID = Field(..., title='ID склада')
    name: str = Field(..., title='Название склада')

    @classmethod
    def from_model(cls, warehouse: models.Warehouse):
        return cls(id=warehouse.id, name=warehouse.name)
