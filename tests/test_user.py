from http import HTTPStatus

import pytest
from sqlalchemy import select

from src.auth.models import User
from tests.fakes import fake


@pytest.fixture
def get_user_from_database(get_session):
    async def get_user_from_user_data(user_data: dict) -> User | None:
        stmt = select(User).where(
            User.first_name == user_data["first_name"],
            User.last_name == user_data["last_name"],
            User.email == user_data["email"],
        )
        res = await get_session.execute(stmt)
        return res.scalar_one_or_none()

    return get_user_from_user_data


@pytest.fixture
def create_user_data():
    return {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
    }


async def test_create_user(async_client, create_user_data, get_user_from_database):
    user_data = create_user_data

    result = await async_client.post("/auth/", json=user_data)

    assert result.status_code == HTTPStatus.OK
    data = result.json()
    assert data["first_name"] == user_data["first_name"]
    assert data["last_name"] == user_data["last_name"]
    assert data["email"] == user_data["email"]
    user_from_db = await get_user_from_database(user_data)
    assert user_from_db
    assert user_from_db.first_name == user_data["first_name"]
    assert user_from_db.last_name == user_data["last_name"]
    assert user_from_db.email == user_data["email"]
