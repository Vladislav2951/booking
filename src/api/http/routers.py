from fastapi import APIRouter

from api.http.endpoints import booking_router


routers = APIRouter()
_router_list = [booking_router]

for router in _router_list:
    routers.include_router(router)
