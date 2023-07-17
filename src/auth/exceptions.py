from fastapi import HTTPException, status


class AuthException(HTTPException):
    def __init__(self, detail: str, authenticate_value: str = "Bearer"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": authenticate_value},
        )
