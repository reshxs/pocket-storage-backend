import uuid

import pytest
from django.utils import timezone

from pocket_storage import factories
from pocket_storage import models


pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_create_with_id__ok(freezer, warehouse, mobile_request):
    product = factories.ProductFactory.create()
    assert not models.StorageUnit.objects.exists()

    resp = mobile_request(
        "create_storage_unit_with_product_id",
        {
            "product_id": str(product.id),
            "ext_id": "Z123",
        },
    )

    storage_unit = models.StorageUnit.objects.get()
    assert storage_unit.product == product
    assert storage_unit.ext_id == "Z123"
    assert storage_unit.warehouse == warehouse
    assert storage_unit.created_at == timezone.now()

    assert resp.get("result") == {
        "ext_id": "Z123",
        "id": str(storage_unit.id),
        "product_SKU": product.SKU,
        "product_barcode": product.barcode,
        "product_category_id": str(product.category.id),
        "product_category_name": product.category.name,
        "product_id": str(product.id),
        "product_name": product.name,
    }


def test_create_with_id__product_not_found__return_error(mobile_request):
    assert not models.StorageUnit.objects.exists()

    resp = mobile_request(
        "create_storage_unit_with_product_id",
        {
            "product_id": str(uuid.uuid4()),
            "ext_id": "Z123",
        },
    )

    assert resp.get("error") == {"code": 4002, "message": "Product not found"}
    assert not models.StorageUnit.objects.exists()


def test_create_with_id__storage_unit_already_exists(mobile_request):
    storage_unit = factories.StorageUnitFactory.create()
    product = factories.ProductFactory.create()

    resp = mobile_request(
        "create_storage_unit_with_product_id",
        {
            "product_id": str(product.id),
            "ext_id": storage_unit.ext_id,
        },
    )

    assert resp.get("error") == {"code": 7001, "message": "Storage unit already exists"}
    assert not models.StorageUnit.objects.exclude(id=storage_unit.id).exists()


def test_create_with_barcode__ok(freezer, warehouse, mobile_request):
    product = factories.ProductFactory.create()
    assert not models.StorageUnit.objects.exists()

    resp = mobile_request(
        "create_storage_unit_with_product_barcode",
        {
            "barcode": product.barcode,
            "ext_id": "Z123",
        },
    )

    storage_unit = models.StorageUnit.objects.get()
    assert storage_unit.product == product
    assert storage_unit.ext_id == "Z123"
    assert storage_unit.warehouse == warehouse
    assert storage_unit.created_at == timezone.now()

    assert resp.get("result") == {
        "ext_id": "Z123",
        "id": str(storage_unit.id),
        "product_SKU": product.SKU,
        "product_barcode": product.barcode,
        "product_category_id": str(product.category.id),
        "product_category_name": product.category.name,
        "product_id": str(product.id),
        "product_name": product.name,
    }


def test_create_with_barcode__product_not_found__return_error(mobile_request):
    assert not models.StorageUnit.objects.exists()

    resp = mobile_request(
        "create_storage_unit_with_product_barcode",
        {
            "barcode": 'barcode',
            "ext_id": "Z123",
        },
    )

    assert resp.get("error") == {"code": 4002, "message": "Product not found"}
    assert not models.StorageUnit.objects.exists()


def test_create_with_barcode__storage_unit_already_exists(mobile_request):
    storage_unit = factories.StorageUnitFactory.create()
    product = factories.ProductFactory.create()

    resp = mobile_request(
        "create_storage_unit_with_product_barcode",
        {
            "barcode": product.barcode,
            "ext_id": storage_unit.ext_id,
        },
    )

    assert resp.get("error") == {"code": 7001, "message": "Storage unit already exists"}
    assert not models.StorageUnit.objects.exclude(id=storage_unit.id).exists()
