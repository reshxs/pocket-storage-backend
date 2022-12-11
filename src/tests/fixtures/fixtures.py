import functools
import pytest
import simplejson as json

from starlette.testclient import TestClient


@pytest.fixture(autouse=True, scope="session")
def _init_django():
    import os

    import django

    os.environ["DJANGO_SETTINGS_MODULE"] = "pocket_storage.settings"
    django.setup()


class ApiClient(TestClient):
    def api_jsonrpc_request(
        self,
        method: str,
        params: dict = None,
        *,
        url: str,
        use_decimal: bool = True,
        session_key: str = None,
        headers: dict = None,
        cookies: dict = None,
    ):
        headers = headers or {}
        cookies = cookies or {}

        if session_key is not None:
            headers["X-session-key"] = session_key

        resp = self.post(
            url=url,
            data=json.dumps(
                {
                    "id": 0,
                    "jsonrpc": "2.0",
                    "method": method,
                    "params": params or {},
                },
            ),
            headers=headers,
            cookies=cookies,
        )

        # return resp.json(use_decimal=use_decimal)  # FIXME: куда делся use_decimal?
        return resp.json()


@pytest.fixture()
def api_app():
    import pocket_storage.app

    return pocket_storage.app.app


@pytest.fixture()
def api_client(
    api_app,
):
    client = ApiClient(api_app)
    return client


@pytest.fixture()
def web_request(transactional_db, api_client, requests_mock, user_session_key):
    requests_mock.register_uri(
        "POST", "http://testserver/api/v1/web/jsonrpc", real_http=True
    )

    return functools.partial(
        api_client.api_jsonrpc_request,
        url="/api/v1/web/jsonrpc",
        session_key=user_session_key,
    )
