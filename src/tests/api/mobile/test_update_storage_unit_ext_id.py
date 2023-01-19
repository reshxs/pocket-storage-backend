import uuid

import pytest
from dirty_equals import IsPartialDict
from pocket_storage import factories

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_ok(mobile_request):
    storage_unit = factories.StorageUnitFactory.create(ext_id="old_ext_id")

    resp = mobile_request(
        "update_storage_unit_ext_id",
        {
            "storage_unit_id": str(storage_unit.id),
            "ext_id": "new_ext_id",
        },
    )

    assert resp.get("result") == IsPartialDict(
        {
            "id": str(storage_unit.id),
            "ext_id": "new_ext_id",
        },
    )

    storage_unit.refresh_from_db()
    assert storage_unit.ext_id == "new_ext_id"


def test_storage_unit_not_found(mobile_request):
    resp = mobile_request(
        "update_storage_unit_ext_id",
        {
            "storage_unit_id": str(uuid.uuid4()),
            "ext_id": "new_ext_id",
        },
    )

    assert resp.get("error") == {
        "code": 7002,
        "message": "Storage unit not found",
    }
