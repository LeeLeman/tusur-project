from src.auth.schemas import UserCreate, UserGet, UserPermissions


class AdminCreateUser(UserCreate, UserPermissions):
    pass


class AdminUpdateUser(AdminCreateUser):
    pass


class AdminGetUser(UserGet, UserPermissions):
    pass
