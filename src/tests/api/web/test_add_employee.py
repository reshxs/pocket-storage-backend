import uuid

import pytest

from pocket_storage import models, factories

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_ok(web_request):
    assert not models.Employee.objects.exists()

    position = factories.EmployeePositionFactory.create()

    resp = web_request(
        "add_employee",
        {
            "employee_data": {
                "first_name": "Иван",
                "last_name": "Иванов",
                "middle_name": "Иванович",
                "position_id": str(position.id),
            },
        },
    )

    created_employee = models.Employee.objects.get()

    assert created_employee.first_name == "Иван"
    assert created_employee.last_name == "Иванов"
    assert created_employee.middle_name == "Иванович"
    assert created_employee.position == position

    assert resp.get("result") == {
        "id": str(created_employee.id),
        "first_name": "Иван",
        "last_name": "Иванов",
        "middle_name": "Иванович",
        "position": {
            "id": str(position.id),
            "name": position.name,
        },
    }, resp.get("error")


def test_position_not_found__return_error(web_request):
    assert not models.Employee.objects.exists()
    assert not models.EmployeePosition.objects.exists()

    resp = web_request(
        "add_employee",
        {
            "employee_data": {
                "first_name": "Иван",
                "last_name": "Иванов",
                "middle_name": "Иванович",
                "position_id": str(uuid.uuid4()),
            },
        },
    )

    assert resp.get("error") == {
        "code": 5002,
        "message": "Employee position not found",
    }

    assert not models.Employee.objects.exists()
