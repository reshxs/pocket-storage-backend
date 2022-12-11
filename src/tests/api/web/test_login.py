import datetime as dt

import pytest
import simplejson as json
from django.contrib.sessions.models import Session
from django.utils import timezone

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


def test_user_not_found(web_request):
    resp = web_request(
        "login",
        {
            "username": "username",
            "password": "password",
        },
    )

    assert resp.get("error") == {"code": 1001, "message": "Wrong credentials"}


def test_wrong_password(web_request, user, user_raw_password):
    resp = web_request(
        "login",
        {
            "username": user.username,
            "password": f'{user_raw_password}_INVALID',
        },
    )

    assert resp.get("error") == {"code": 1001, "message": "Wrong credentials"}


def test_ok(web_request, user, user_raw_password, freezer):
    assert not Session.objects.exists()

    resp = web_request(
        "login",
        {
            "username": user.username,
            "password": user_raw_password,
        },
    )

    created_session = Session.objects.get()
    assert created_session.expire_date == timezone.now() + dt.timedelta(hours=3)
    assert json.loads(created_session.session_data) == {
        'user_id': user.id,
    }

    assert resp.get("result") == {
        'session_key': str(created_session.session_key),
        'user': {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    }, resp.get("error")
