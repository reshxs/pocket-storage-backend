import uuid

import pytest

from pocket_storage import models, factories

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_ok(mobile_request):
    storage_unit: models.StorageUnit = factories.StorageUnitFactory.create()

    resp = mobile_request(
        "get_storage_unit_with_id",
        {
            "id": str(storage_unit.id),
        },
    )

    assert resp.get("result") == {
        "ext_id": storage_unit.ext_id,
        "id": str(storage_unit.id),
        "product_SKU": storage_unit.product.SKU,
        "product_barcode": storage_unit.product.barcode,
        "product_category_id": str(storage_unit.product.category.id),
        "product_category_name": storage_unit.product.category.name,
        "product_id": str(storage_unit.product.id),
        "product_name": storage_unit.product.name,
    }, resp.get("error")


def test_not_found(mobile_request):
    resp = mobile_request(
        "get_storage_unit_with_id",
        {
            "id": str(uuid.uuid4()),
        },
    )

    assert resp.get("error") == {
        "code": 7002,
        "message": "Storage unit not found",
    }
