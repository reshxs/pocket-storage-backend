import uuid

import pytest
from django.forms import model_to_dict
from django.utils import timezone

from pocket_storage import factories, models

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_ok(web_request, freezer):
    old_sku = "SNI/01/136/0500"
    new_sku = "SNI/03/213/1477"

    product = factories.ProductFactory.create(
        name="old_name",
        SKU=old_sku,
        barcode=None,
    )
    new_category = factories.ProductCategoryFactory.create()

    assert product.updated_at is None

    resp = web_request(
        "update_product",
        {
            "id": str(product.id),
            "product_data": {
                "name": "new_name",
                "barcode": "4600702084566",
                "SKU": new_sku,
                "category_id": str(new_category.id),
            },
        },
    )

    assert resp.get("result") == {
        "id": str(product.id),
        "name": "new_name",
        "SKU": new_sku,
        "barcode": "4600702084566",
        "category": {
            "id": str(new_category.id),
            "name": new_category.name,
            "parent_id": str(new_category.parent_id)
            if new_category.parent_id
            else None,
        },
    }, resp.get("error")

    product.refresh_from_db()
    assert product.name == "new_name"
    assert product.SKU == new_sku
    assert product.barcode == "4600702084566"
    assert product.category_id == new_category.id
    assert product.updated_at == timezone.now()


def test_product_not_found__return_error(web_request):
    assert not models.Product.objects.exists()

    resp = web_request(
        "update_product",
        {
            "id": str(uuid.uuid4()),
            "product_data": {
                "name": "new_name",
            },
        },
    )

    assert resp.get("error") == {
        "code": 4002,
        "message": "Product not found",
    }


def test_barcode_exists__return_error(web_request):
    product = factories.ProductFactory.create()
    other_product = factories.ProductFactory.create()

    resp = web_request(
        "update_product",
        {
            "id": str(product.id),
            "product_data": {
                "barcode": other_product.barcode,
            },
        },
    )

    assert resp.get("error") == {
        "code": 4001,
        "message": "Product already exists",
    }

    old_product = model_to_dict(product)
    product.refresh_from_db()
    actual_product = model_to_dict(product)
    assert actual_product == old_product


def test_sku_exists__return_error(web_request):
    product = factories.ProductFactory.create()
    other_product = factories.ProductFactory.create()

    resp = web_request(
        "update_product",
        {
            "id": str(product.id),
            "product_data": {
                "SKU": other_product.SKU,
            },
        },
    )

    assert resp.get("error") == {
        "code": 4001,
        "message": "Product already exists",
    }

    old_product = model_to_dict(product)
    product.refresh_from_db()
    actual_product = model_to_dict(product)
    assert actual_product == old_product


def test_category_not_found__return_error(web_request):
    product = factories.ProductFactory.create()

    resp = web_request(
        "update_product",
        {
            "id": str(product.id),
            "product_data": {
                "category_id": str(uuid.uuid4()),
            },
        },
    )

    assert resp.get("error") == {
        "code": 3002,
        "message": "Product category not found",
    }

    old_product = model_to_dict(product)
    product.refresh_from_db()
    actual_product = model_to_dict(product)
    assert actual_product == old_product
