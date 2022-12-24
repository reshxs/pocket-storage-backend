import uuid

import pytest
from django.forms import model_to_dict

from pocket_storage import factories

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_ok(web_request):
    employee = factories.EmployeeFactory.create(
        first_name="old_first_name",
        last_name="old_last_name",
        middle_name="old_middle_name",
    )
    new_position = factories.EmployeePositionFactory.create()

    resp = web_request(
        "update_employee",
        {
            "employee_id": str(employee.id),
            "employee_data": {
                "first_name": "new_first_name",
                "last_name": "new_last_name",
                "middle_name": "new_middle_name",
                "position_id": str(new_position.id),
            },
        },
    )

    assert resp.get("result") == {
        "id": str(employee.id),
        "first_name": "new_first_name",
        "last_name": "new_last_name",
        "middle_name": "new_middle_name",
        "position": {
            "id": str(new_position.id),
            "name": new_position.name,
        },
    }, resp.get("error")

    employee.refresh_from_db()
    assert employee.first_name == "new_first_name"
    assert employee.last_name == "new_last_name"
    assert employee.middle_name == "new_middle_name"
    assert employee.position == new_position


def test_position_not_found__return_error(web_request):
    employee = factories.EmployeeFactory.create()

    resp = web_request(
        "update_employee",
        {
            "employee_id": str(employee.id),
            "employee_data": {
                "position_id": str(uuid.uuid4()),
            },
        },
    )

    assert resp.get("error") == {
        "code": 5002,
        "message": "Employee position not found",
    }

    old_employee = model_to_dict(employee)
    employee.refresh_from_db()
    actual_employee = model_to_dict(employee)

    assert actual_employee == old_employee


def test_employee_not_found__return_error(web_request):
    resp = web_request(
        "update_employee",
        {
            "employee_id": str(uuid.uuid4()),
            "employee_data": {
                "position_id": str(uuid.uuid4()),
            },
        },
    )

    assert resp.get("error") == {
        "code": 6002,
        "message": "Employee not found",
    }
