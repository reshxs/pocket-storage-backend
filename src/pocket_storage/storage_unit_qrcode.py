import qrcode
from io import BytesIO
import jwt
from django.conf import settings
from pydantic import BaseModel

from pocket_storage import models


class QrCodeContentPayload(BaseModel):
    storage_unit_id: str

    @classmethod
    def from_storage_unit(cls, storage_unit: models.StorageUnit):
        return cls(
            storage_unit_id=str(storage_unit.id),
        )


def make_qrcode(storage_unit: models.StorageUnit) -> bytes:
    content = make_qrcode_content(storage_unit)
    buffer = BytesIO()
    qr = qrcode.make(content)
    qr.save(buffer)
    return buffer.getvalue()


def make_qrcode_content(storage_unit: models.StorageUnit) -> str:
    payload = QrCodeContentPayload.from_storage_unit(storage_unit).dict()
    return jwt.encode(
        payload,
        key=settings.SECRET_KEY,
        algorithm="HS256",
    )


def parse_qrcode_content(content: str) -> QrCodeContentPayload:
    payload = jwt.decode(
        content,
        key=settings.SECRET_KEY,
        algorithms=["HS256"],
        options={"verify_signature": True},
    )

    return QrCodeContentPayload.parse_obj(payload)
