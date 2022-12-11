from django.contrib.auth.models import User
from fastapi import Depends
from pydantic import parse_obj_as
from starlette.requests import Request

from pocket_storage import auth
from . import errors


def get_session_key(request: Request) -> str:
    session_key = request.headers.get("X-session-key")

    if session_key is None:
        raise errors.AccessDenied

    return session_key


def get_session(session=Depends(get_session_key)) -> auth.Session:
    session = auth.get_session(session_key=session)

    if session is None:
        raise errors.AccessDenied

    return session


def get_user(session: auth.Session = Depends(get_session)) -> User:
    return User.objects.get(id=session.data.user_id)
