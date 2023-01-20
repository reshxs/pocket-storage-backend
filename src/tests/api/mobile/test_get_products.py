import pytest
from dirty_equals import IsPartialDict

from pocket_storage import factories, models

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_empty_list(mobile_request):
    assert not models.Product.objects.exists()

    resp = mobile_request(
        "get_products",
        {
            "pagination": {
                "count": True,
            },
        },
    )

    assert resp.get("result") == {
        "has_next": False,
        "items": [],
        "total_size": 0,
    }, resp.get("error")


def test_ok(mobile_request):
    expected_product = factories.ProductFactory.create()

    resp = mobile_request(
        "get_products",
        {
            "pagination": {
                "count": True,
            },
        },
    )

    assert resp.get("result") == {
        "has_next": False,
        "items": [
            {
                "id": str(expected_product.id),
                "name": expected_product.name,
                "SKU": expected_product.SKU,
                "barcode": expected_product.barcode,
                "category": {
                    "id": str(expected_product.category.id),
                    "name": expected_product.category.name,
                    "parent_id": (
                        str(expected_product.category.parent_id)
                        if expected_product.category.parent_id
                        else None
                    ),
                },
            }
        ],
        "total_size": 1,
    }, resp.get("error")


@pytest.mark.parametrize(
    "query",
    [
        "Краска",
        "краска",
        "крас",
        "ска",
        "SNI/01/136/0500",
        "SNI",
        "0500",
        "sni",
        "4600702084566",
        "4600",
        "4566",
    ],
)
def test_search(mobile_request, query):
    expected_product = factories.ProductFactory.create(
        name="Краска",
        SKU="SNI/01/136/0500",
        barcode="4600702084566",
    )

    resp = mobile_request(
        "get_products",
        {
            "pagination": {
                "count": True,
            },
            "search": query,
        },
    )

    assert resp.get("result") == {
        "has_next": False,
        "items": [
            IsPartialDict(
                {
                    "id": str(expected_product.id),
                    "name": expected_product.name,
                    "SKU": expected_product.SKU,
                    "barcode": expected_product.barcode,
                },
            )
        ],
        "total_size": 1,
    }, resp.get("error")
