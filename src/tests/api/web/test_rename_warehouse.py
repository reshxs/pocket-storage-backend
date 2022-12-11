import pytest

from pocket_storage import factories

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_ok(web_request):
    warehouse = factories.WarehouseFactory.create(name="old_name")

    resp = web_request(
        "rename_warehouse",
        {
            "id": str(warehouse.id),
            "new_name": "new_name",
        },
    )

    assert resp.get("result") == {"id": str(warehouse.id), "name": "new_name"}

    warehouse.refresh_from_db()
    assert warehouse.name == "new_name"
