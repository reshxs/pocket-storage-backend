import pytest
from dirty_equals import IsListOrTuple

from pocket_storage import factories

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_ok(web_request):
    positions = factories.EmployeePositionFactory.create_batch(3)

    resp = web_request('get_employee_positions')

    assert resp.get('result') == IsListOrTuple(
        *[
            {
                'id': str(position.id),
                'name': position.name,
            }
            for position in positions
        ],
        check_order=False,
    ), resp.get('error')
