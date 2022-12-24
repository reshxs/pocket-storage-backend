import uuid

import pytest

from pocket_storage import factories

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_ok(web_request):
    operation = factories.StorageUnitOperationFactory.create()

    resp = web_request(
        "get_storage_unit_operations",
        {
            "storage_unit_id": str(operation.storage_unit.id),
            "pagination": {
                "count": True,
            },
        },
    )

    assert resp.get("result") == {
        "has_next": False,
        "total_size": 1,
        "items": [
            {
                "id": str(operation.id),
                "storage_unit_id": str(operation.storage_unit.id),
                "employee": {
                    "id": str(operation.employee.id),
                    "first_name": operation.employee.first_name,
                    "last_name": operation.employee.last_name,
                    "middle_name": operation.employee.middle_name,
                    "position": {
                        "id": str(operation.employee.position.id),
                        "name": operation.employee.position.name,
                    },
                },
                "initial_state": operation.initial_state,
                "final_state": operation.final_state,
                "created_at": operation.created_at.isoformat(),
            },
        ],
    }, resp.get("error")


def test_storage_unit_not_found__return_error(web_request):
    resp = web_request(
        "get_storage_unit_operations",
        {
            "storage_unit_id": str(uuid.uuid4()),
        },
    )

    assert resp.get("error") == {
        "code": 7002,
        "message": "Storage unit not found",
    }
