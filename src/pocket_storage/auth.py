import dataclasses
import datetime as dt
import uuid

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session as DjangoSession
from django.utils import timezone
from pydantic import BaseModel
from pydantic import parse_raw_as


class SessionData(BaseModel):
    user_id: int
    username: str

    @classmethod
    def from_user_model(cls, user: User):
        return cls(
            user_id=user.id,
            username=user.username,
        )


@dataclasses.dataclass
class Session:
    key: str
    data: SessionData


def login(username, password) -> Session | None:
    user = authenticate(username=username, password=password)

    if user is None:
        return None

    session_data = SessionData.from_user_model(user)
    session = DjangoSession.objects.create(
        session_key=uuid.uuid4(),
        session_data=session_data.json(),
        expire_date=timezone.now() + dt.timedelta(hours=3),
    )

    return Session(key=session.session_key, data=session_data)


def get_session(session_key: str) -> Session | None:
    try:
        django_session = DjangoSession.objects.get(session_key=session_key)
    except DjangoSession.DoesNotExist:
        return None

    return Session(
        key=session_key, data=parse_raw_as(SessionData, django_session.session_data)
    )
