import uuid

import pytest

from pocket_storage import factories, models

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_ok(web_request):
    employee = factories.EmployeeFactory.create()

    resp = web_request(
        "get_employee",
        {
            "employee_id": str(employee.id),
        },
    )

    assert resp.get("result") == {
        "id": str(employee.id),
        "first_name": employee.first_name,
        "last_name": employee.last_name,
        "middle_name": employee.middle_name,
        "position": {
            "id": str(employee.position.id),
            "name": employee.position.name,
        },
    }, resp.get("error")


def test_not_found__return_error(web_request):
    assert not models.Employee.objects.exists()

    resp = web_request(
        "get_employee",
        {
            "employee_id": str(uuid.uuid4()),
        },
    )

    assert resp.get("error") == {
        "code": 6002,
        "message": "Employee not found",
    }
