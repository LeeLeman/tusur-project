from fastapi import FastAPI

from src.admin.router import admin_router
from src.auth.router import auth_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(admin_router)
