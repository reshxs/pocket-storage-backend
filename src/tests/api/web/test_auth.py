import uuid

import pytest
import functools


pytestmark = [
    pytest.mark.django_db(transaction=True),
]


@pytest.fixture()
def web_request(transactional_db, api_client, requests_mock):
    requests_mock.register_uri(
        "POST", "http://testserver/api/v1/web/jsonrpc", real_http=True
    )

    return functools.partial(api_client.api_jsonrpc_request, url="/api/v1/web/jsonrpc")


def test_no_auth(web_request):
    resp = web_request(
        "add_warehouse",
        {
            "name": "test",
        },
    )

    assert resp.get("error") == {"code": 1002, "message": "Access denied"}


def test_no_session(web_request):
    session_key = uuid.uuid4()

    resp = web_request(
        "add_warehouse",
        {
            "name": "test",
        },
        session_key=str(session_key),
    )

    assert resp.get("error") == {"code": 1002, "message": "Access denied"}


def test_ok(web_request, user_session_key):
    resp = web_request(
        "add_warehouse",
        {
            "name": "test",
        },
        session_key=str(user_session_key),
    )

    assert resp.get("result")
