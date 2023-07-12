from http import HTTPStatus

import pytest
from passlib.context import CryptContext
from sqlalchemy import select

from src.auth.models import User
from tests.fakes import fake


@pytest.fixture
def get_user_from_database(get_session):
    async def get_user_from_user_data(user_data: dict) -> User | None:
        stmt = select(User).where(
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
        "password": fake.password(),
    }


@pytest.fixture(scope="module")
def pwd_context():
    return CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.fixture(scope="module")
def create_user(client) -> dict:
    create_user_data = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "password": fake.password(),
    }
    client.post("/auth/register", json=create_user_data)
    return create_user_data


@pytest.fixture(scope="module")
def get_token(client, create_user) -> str:
    login_data = {
        "username": create_user["email"],
        "password": create_user["password"],
    }
    res = client.post(
        "/auth/token",
        data=login_data,
        headers={"content-type": "application/x-www-form-urlencoded"},
    )
    return res.json().get("access_token")


@pytest.fixture(scope="module")
def get_headers(get_token) -> dict:
    return {"Authorization": f"Bearer {get_token}"}


async def test_create_user(
    async_client, create_user_data, get_user_from_database, pwd_context
):
    result = await async_client.post("/auth/register", json=create_user_data)

    assert result.status_code == HTTPStatus.OK
    data = result.json()
    assert data["first_name"] == create_user_data["first_name"]
    assert data["last_name"] == create_user_data["last_name"]
    assert data["email"] == create_user_data["email"]
    user_from_db = await get_user_from_database(create_user_data)
    assert user_from_db
    assert user_from_db.first_name == create_user_data["first_name"]
    assert user_from_db.last_name == create_user_data["last_name"]
    assert user_from_db.email == create_user_data["email"]
    assert pwd_context.verify(
        create_user_data["password"], user_from_db.hashed_password
    )


async def test_login_user(async_client, create_user):
    user_data: dict = create_user
    login_data = {
        "username": user_data["email"],
        "password": user_data["password"],
    }

    result = await async_client.post(
        "/auth/token",
        data=login_data,
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    data = result.json()
    assert result.status_code == HTTPStatus.OK
    assert data["token_type"] == "bearer"
    assert data["access_token"]


async def test_read_users_me(async_client, create_user, get_headers):
    result = await async_client.get("/auth/me", headers=get_headers)

    data = result.json()
    assert result.status_code == HTTPStatus.OK
    assert data["email"] == create_user["email"]
    assert data["first_name"] == create_user["first_name"]
    assert data["last_name"] == create_user["last_name"]
