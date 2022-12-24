import pytest

from pocket_storage import factories

pytestmark = [
    pytest.mark.django_db(transaction=True)
]


def test_ok(web_request):
    storage_unit = factories.StorageUnitFactory.create()

    resp = web_request(
        'get_storage_units',
        {
            'product_id': str(storage_unit.product.id),
            'pagination': {
                'count': True,
            },
        },
    )

    assert resp.get('result') == {
        'has_next': False,
        'total_size': 1,
        'items': [
            {
                'id': str(storage_unit.id),
                'product': {
                    'id': str(storage_unit.product.id),
                    'name': storage_unit.product.name,
                },
                'warehouse': {
                    'id': str(storage_unit.warehouse.id),
                    'name': storage_unit.warehouse.name,
                },
                'state': storage_unit.state.value,
                'created_at': storage_unit.created_at.isoformat(),
                'updated_at': storage_unit.updated_at.isoformat() if storage_unit.updated_at else None,
            },
        ],
    }, resp.get('error')


def test_filter_filter_by_warehouse(web_request):
    expected_storage_unit = factories.StorageUnitFactory.create()
    unexpected_storage_unit = factories.StorageUnitFactory.create()

    assert expected_storage_unit.warehouse != unexpected_storage_unit.warehouse

    resp = web_request(
        'get_storage_units',
        {
            'product_id': str(expected_storage_unit.product.id),
            'filters': {
                'warehouse_ids': [str(expected_storage_unit.warehouse.id)]
            },
            'pagination': {
                'count': True,
            },
        },
    )

    assert resp.get('result') == {
        'has_next': False,
        'total_size': 1,
        'items': [
            {
                'id': str(expected_storage_unit.id),
                'product': {
                    'id': str(expected_storage_unit.product.id),
                    'name': expected_storage_unit.product.name,
                },
                'warehouse': {
                    'id': str(expected_storage_unit.warehouse.id),
                    'name': expected_storage_unit.warehouse.name,
                },
                'state': expected_storage_unit.state.value,
                'created_at': expected_storage_unit.created_at.isoformat(),
                'updated_at': expected_storage_unit.updated_at.isoformat() if expected_storage_unit.updated_at else None,
            },
        ],
    }, resp.get('error')


# TODO: добавить тесты для остальных фильтров
