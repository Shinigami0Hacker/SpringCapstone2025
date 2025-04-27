from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.requests import Request
from routers.admin_router import router as admin_routers
from routers.system_router import router as system_router
from routers.user_router import router as user_router
from dependencies.auth import UnauthorizedException
import os

app = FastAPI()

@app.exception_handler(UnauthorizedException)
async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
    return RedirectResponse(url="/admin/verification", status_code=302)

app.include_router(admin_routers, prefix="/admin")
app.include_router(system_router, prefix="/system")
app.include_router(user_router, prefix="/user")
