import uuid

import pytest

from pocket_storage import factories, models

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_ok(web_request):
    product = factories.ProductFactory.create()

    resp = web_request(
        "get_product",
        {
            "id": str(product.id),
        },
    )

    assert resp.get("result") == {
        "id": str(product.id),
        "name": product.name,
        "SKU": product.SKU,
        "barcode": product.barcode,
        "category": {
            "id": str(product.category.id),
            "name": product.category.name,
            "parent_id": str(product.category.parent_id)
            if product.category.parent_id
            else None,
        },
    }


def test_not_found__return_error(web_request):
    assert not models.Product.objects.exists()

    resp = web_request(
        "get_product",
        {
            "id": str(uuid.uuid4()),
        },
    )

    assert resp.get("error") == {
        "code": 4002,
        "message": "Product not found",
    }
