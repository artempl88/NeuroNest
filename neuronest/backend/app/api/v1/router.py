"""
Основной роутер API v1
"""

from fastapi import APIRouter

api_router = APIRouter()

# TODO: Добавить импорты роутеров когда они будут созданы
# from app.api.v1.endpoints import agents, users, transactions

# TODO: Подключить роутеры
# api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])

# Временный тестовый эндпоинт
@api_router.get("/test")
async def test_endpoint():
    return {"message": "API v1 работает"} 