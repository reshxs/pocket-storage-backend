import pytest

from pocket_storage import models


pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_ok(web_request):
    assert not models.Warehouse.objects.exists()

    resp = web_request(
        "add_warehouse",
        {
            "name": "Новый склад",
        },
    )

    created_warehouse = models.Warehouse.objects.get()
    assert created_warehouse.name == "Новый склад"

    assert resp.get("result") == {
        "id": str(created_warehouse.id),
        "name": "Новый склад",
    }, resp.get("error")


def test_already_exists__return_error(web_request, warehouse):
    resp = web_request(
        "add_warehouse",
        {
            "name": warehouse.name,
        },
    )

    assert resp.get("error") == {
        "code": 2001,
        "message": "Склад с таким именем уже существует",
    }

    assert not models.Warehouse.objects.exclude(id=warehouse.id).exists()
