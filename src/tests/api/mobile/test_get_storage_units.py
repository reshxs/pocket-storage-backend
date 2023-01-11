import pytest

from pocket_storage import factories, models

pytestmark = [pytest.mark.django_db(transaction=True)]


def test_empty(mobile_request):
    resp = mobile_request(
        "get_storage_units",
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
    storage_unit: models.StorageUnit = factories.StorageUnitFactory.create()

    resp = mobile_request(
        "get_storage_units",
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
                "ext_id": storage_unit.ext_id,
                "id": str(storage_unit.id),
                "product_SKU": storage_unit.product.SKU,
                "product_barcode": storage_unit.product.barcode,
                "product_category_id": str(storage_unit.product.category.id),
                "product_category_name": storage_unit.product.category.name,
                "product_id": str(storage_unit.product.id),
                "product_name": storage_unit.product.name,
            }
        ],
        "total_size": 1,
    }, resp.get("error")


def test_filter_by_category_id(mobile_request):
    expected_storage_unit: models.StorageUnit = factories.StorageUnitFactory.create()
    factories.StorageUnitFactory.create()  # unexpected_storage_unit

    resp = mobile_request(
        "get_storage_units",
        {
            "pagination": {
                "count": True,
            },
            "filters": {
                'category_ids': [str(expected_storage_unit.product.category.id)],
            },
        },
    )

    assert resp.get("result") == {
        "has_next": False,
        "items": [
            {
                "ext_id": expected_storage_unit.ext_id,
                "id": str(expected_storage_unit.id),
                "product_SKU": expected_storage_unit.product.SKU,
                "product_barcode": expected_storage_unit.product.barcode,
                "product_category_id": str(expected_storage_unit.product.category.id),
                "product_category_name": expected_storage_unit.product.category.name,
                "product_id": str(expected_storage_unit.product.id),
                "product_name": expected_storage_unit.product.name,
            }
        ],
        "total_size": 1,
    }, resp.get("error")


@pytest.mark.parametrize(
    'search_query',
    [
        'Ламинат',
        'SNI/01/136/0500',
        '4600702084566',
        'F123',
    ]
)
def test_search(mobile_request, search_query):
    expected_storage_unit: models.StorageUnit = factories.StorageUnitFactory.create(
        ext_id='F123',
        product__name='Ламинат',
        product__SKU='SNI/01/136/0500',
        product__barcode='4600702084566',
    )
    factories.StorageUnitFactory.create()  # unexpected_storage_unit

    resp = mobile_request(
        "get_storage_units",
        {
            "pagination": {
                "count": True,
            },
            "filters": {
                'search_query': search_query,
            },
        },
    )

    assert resp.get("result") == {
        "has_next": False,
        "items": [
            {
                "ext_id": expected_storage_unit.ext_id,
                "id": str(expected_storage_unit.id),
                "product_SKU": expected_storage_unit.product.SKU,
                "product_barcode": expected_storage_unit.product.barcode,
                "product_category_id": str(expected_storage_unit.product.category.id),
                "product_category_name": expected_storage_unit.product.category.name,
                "product_id": str(expected_storage_unit.product.id),
                "product_name": expected_storage_unit.product.name,
            }
        ],
        "total_size": 1,
    }, resp.get("error")