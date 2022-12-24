import pytest

from pocket_storage import factories
from pocket_storage import models

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_ok(web_request):
    assert not models.EmployeePosition.objects.exists()

    resp = web_request(
        'add_employee_position',
        {
            'name': 'Кладовщик',
        },
    )

    created_position = models.EmployeePosition.objects.get()
    assert created_position.name == 'Кладовщик'

    assert resp.get('result') == {
        'id': str(created_position.id),
        'name': 'Кладовщик',
    }, resp.get('error')


def test_already_exists__return_error(web_request):
    existing_position = factories.EmployeePositionFactory.create()

    resp = web_request(
        'add_employee_position',
        {
            'name': existing_position.name,
        },
    )

    assert resp.get('error') == {
        'code': 5001,
        'message': 'Employee position already exists',
    }

    assert not models.EmployeePosition.objects.exclude(id=existing_position.id).exists()
