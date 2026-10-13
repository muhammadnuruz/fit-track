from fastapi import APIRouter, Depends

from app.api.v1.routes import admin, users
from app.core.security import require_api_key

api_router = APIRouter(dependencies=[Depends(require_api_key)])
api_router.include_router(users.router)
api_router.include_router(admin.router)
