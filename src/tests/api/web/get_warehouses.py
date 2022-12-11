import pytest

from dirty_equals import IsListOrTuple

from pocket_storage import factories

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_empty_list(web_request):
    resp = web_request("get_warehouses")

    assert resp.get("result") == [], resp.get("error")


def test_ok(web_request):
    warehouses = factories.WarehouseFactory.create_batch(3)

    resp = web_request("get_warehouses")

    assert resp.get("result") == IsListOrTuple(
        *[
            {
                "id": str(warehouse.id),
                "name": warehouse.name,
            }
            for warehouse in warehouses
        ],
        check_order=False,
    ), resp.get("error")
