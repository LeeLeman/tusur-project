from fastapi import FastAPI
from mangum import Mangum

from settings import settings
from src.admin.router import admin_router
from src.auth.router import auth_router


app = FastAPI(root_path=settings.ROOT_PATH)

app.include_router(auth_router)
app.include_router(admin_router)

handler = Mangum(app=app)
