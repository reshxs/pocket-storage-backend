import pytest

from pocket_storage import factories

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_ok(mobile_request):
    product = factories.ProductFactory.create()

    resp = mobile_request(
        "get_product_with_barcode",
        {
            "barcode": product.barcode,
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
            "parent_id": (
                str(product.category.parent_id) if product.category.parent_id else None
            ),
        },
    }


def test_not_found(mobile_request):
    resp = mobile_request(
        "get_product_with_barcode",
        {
            "barcode": "some_barcode",
        },
    )

    assert resp.get("error") == {
        "code": 4002,
        "message": "Product not found",
    }
