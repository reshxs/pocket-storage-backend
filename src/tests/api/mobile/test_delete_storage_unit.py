import uuid

import pytest

from pocket_storage import factories, models

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_ok(mobile_request):
    storage_unit = factories.StorageUnitFactory.create()

    resp = mobile_request(
        'delete_storage_unit',
        {
            'storage_unit_id': str(storage_unit.id),
        },
    )

    assert resp.get('result') is True

    assert not models.StorageUnit.objects.filter(id=storage_unit.id).exists()


def test_not_found(mobile_request):
    resp = mobile_request(
        'delete_storage_unit',
        {
            'storage_unit_id': str(uuid.uuid4()),
        },
    )

    assert resp.get("error") == {
        "code": 7002,
        "message": "Storage unit not found",
    }