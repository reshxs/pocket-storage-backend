import pytest

from pocket_storage import factories

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_ok(web_request):
    employee = factories.EmployeeFactory.create()

    resp = web_request(
        "get_employees",
        {
            "pagination": {
                "count": True,
            },
        },
    )

    assert resp.get("result") == {
        "total_size": 1,
        "has_next": False,
        "items": [
            {
                "id": str(employee.id),
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "middle_name": employee.middle_name,
                "position": {
                    "id": str(employee.position.id),
                    "name": employee.position.name,
                },
            },
        ],
    }, resp.get("error")


def test_filter_by_position(web_request):
    expected_employee = factories.EmployeeFactory.create()
    factories.EmployeeFactory.create()  # unexpected_employee

    resp = web_request(
        "get_employees",
        {
            "filters": {
                "position_ids": [str(expected_employee.position.id)],
            },
            "pagination": {
                "count": True,
            },
        },
    )

    assert resp.get("result") == {
        "total_size": 1,
        "has_next": False,
        "items": [
            {
                "id": str(expected_employee.id),
                "first_name": expected_employee.first_name,
                "last_name": expected_employee.last_name,
                "middle_name": expected_employee.middle_name,
                "position": {
                    "id": str(expected_employee.position.id),
                    "name": expected_employee.position.name,
                },
            },
        ],
    }, resp.get("error")


@pytest.mark.parametrize(
    "search_query",
    [
        "Сидоров Вячеслав Григорьевич",
        "Сидоров",
        "Вячеслав",
        "Григорьевич",
        "Вячеслав Сидоров",
    ],
)
def test_search_by_name(web_request, search_query):
    expected_employee = factories.EmployeeFactory.create(
        first_name="Вячеслав",
        last_name="Сидоров",
        middle_name="Григорьевич",
    )
    factories.EmployeeFactory.create(
        first_name="Игорь",
        last_name="Пупкин",
        middle_name="Владимирович",
    )  # unexpected_employee

    resp = web_request(
        "get_employees",
        {
            "filters": {
                "full_name_search": search_query,
            },
            "pagination": {
                "count": True,
            },
        },
    )

    assert resp.get("result") == {
        "total_size": 1,
        "has_next": False,
        "items": [
            {
                "id": str(expected_employee.id),
                "first_name": expected_employee.first_name,
                "last_name": expected_employee.last_name,
                "middle_name": expected_employee.middle_name,
                "position": {
                    "id": str(expected_employee.position.id),
                    "name": expected_employee.position.name,
                },
            },
        ],
    }, resp.get("error")
