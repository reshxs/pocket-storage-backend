import datetime as dt
import functools

import pytest
import simplejson as json
from django.contrib.sessions.models import Session
from django.utils import timezone

pytestmark = [
    pytest.mark.django_db(transaction=True),
]


@pytest.fixture()
def web_request(transactional_db, api_client, requests_mock):
    requests_mock.register_uri(
        "POST", "http://testserver/api/v1/web/jsonrpc", real_http=True
    )

    return functools.partial(api_client.api_jsonrpc_request, url="/api/v1/web/jsonrpc")


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
            "password": f"{user_raw_password}_INVALID",
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
        "user_id": user.id,
        "username": user.username,
    }

    assert resp.get("result") == {
        "session_key": str(created_session.session_key),
    }, resp.get("error")
