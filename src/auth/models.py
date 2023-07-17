from sqlalchemy.orm import mapped_column, Mapped

from src.models import Base
from src.utils import fake_uuid


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(primary_key=True, default=fake_uuid)
    first_name: Mapped[str]
    last_name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True, server_default="true")
    is_admin: Mapped[bool] = mapped_column(default=False, server_default="false")
    is_superuser: Mapped[bool] = mapped_column(default=False, server_default="false")
