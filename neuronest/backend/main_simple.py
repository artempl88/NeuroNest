"""
Упрощенная версия NeuroNest Backend для тестирования
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
import hmac
import hashlib
from urllib.parse import parse_qsl
from typing import Optional

# Импортируем TON API клиент
from ton_api import ton_client

# Создание приложения
app = FastAPI(
    title="NeuroNest API",
    description="Telegram Mini-App маркетплейс AI агентов с NFT-доступом",
    version="1.0.0"
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://localhost:3001", 
        "https://neuronest.notpunks.com",
        "https://bridge.tonapi.io",
        "https://tonhub.com",
        "https://wallet.ton.org"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Модели данных
class TelegramUser(BaseModel):
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = False

class ExecuteAgentRequest(BaseModel):
    agent_id: str
    wallet_address: Optional[str] = None
    transaction_hash: Optional[str] = None

class NFTCheckRequest(BaseModel):
    wallet_address: str

# Мок данные разрешенных NFT коллекций
ALLOWED_COLLECTIONS = [
    {
        "address": "EQCGbQyAJxxMsYQWLCklkXQq4fkIBK3kz3GA1TkFJyUR9nTH",
        "name": "NeuroNest Access Collection",
        "description": "Официальная NFT коллекция для доступа к NeuroNest"
    }
]

def verify_telegram_data(init_data: str, bot_token: str = "fake_token") -> dict:
    """
    Проверка данных от Telegram WebApp
    В реальном проекте здесь будет настоящий токен бота
    """
    try:
        # В режиме разработки пропускаем проверку
        if bot_token == "fake_token":
            # Парсим данные без проверки
            parsed_data = dict(parse_qsl(init_data))
            if 'user' in parsed_data:
                user_data = json.loads(parsed_data['user'])
                return {"valid": True, "user": user_data}
            return {"valid": False}
        
        # Реальная проверка подписи (для продакшена)
        parsed_data = dict(parse_qsl(init_data))
        hash_value = parsed_data.pop('hash', '')
        
        # Создаем строку данных для проверки
        data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(parsed_data.items())])
        
        # Вычисляем хеш
        secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        if calculated_hash == hash_value:
            user_data = json.loads(parsed_data.get('user', '{}'))
            return {"valid": True, "user": user_data}
        
        return {"valid": False}
    except Exception as e:
        print(f"Ошибка проверки Telegram данных: {e}")
        return {"valid": False}

async def check_nft_ownership(wallet_address: str) -> dict:
    """
    Проверка владения NFT из разрешенных коллекций через TON API
    """
    try:
        # Получаем адреса разрешенных коллекций
        allowed_collection_addresses = [collection["address"] for collection in ALLOWED_COLLECTIONS]
        
        # Используем TON API клиент для проверки
        result = await ton_client.check_collection_ownership(wallet_address, allowed_collection_addresses)
        
        return result
        
    except Exception as e:
        print(f"Ошибка проверки NFT: {e}")
        # Fallback к мок данным в случае ошибки API
        return await _fallback_nft_check(wallet_address)

async def _fallback_nft_check(wallet_address: str) -> dict:
    """
    Fallback функция с мок данными когда TON API недоступно
    """
    # Базовая проверка - если адрес валидный, считаем что есть NFT
    if wallet_address and len(wallet_address) > 10:
        mock_nfts = [
            {
                "collection": ALLOWED_COLLECTIONS[0]["address"],
                "token_id": "1",
                "name": "NeuroNest Access Pass #1",
                "image": "https://via.placeholder.com/300x300/00FFFF/000000?text=NEURONEST",
                "verified": True,
                "description": "Official NeuroNest Access NFT"
            }
        ]
        
        return {
            "has_access": True,
            "access_level": "basic",
            "nfts": mock_nfts,
            "total_nfts": len(mock_nfts),
            "fallback_mode": True
        }
    
    return {
        "has_access": False,
        "access_level": "none",
        "nfts": [],
        "total_nfts": 0,
        "fallback_mode": True
    }

@app.get("/")
async def root():
    return {"message": "NeuroNest Backend работает! 🚀"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "neuronest-backend"}

@app.post("/api/v1/auth/telegram")
async def verify_telegram_auth(
    init_data: str = Header(..., alias="x-telegram-init-data")
):
    """Проверка авторизации через Telegram WebApp"""
    result = verify_telegram_data(init_data)
    
    if not result["valid"]:
        raise HTTPException(status_code=401, detail="Недействительные данные Telegram")
    
    user = result["user"]
    return {
        "authenticated": True,
        "user": user,
        "session_token": f"session_{user['id']}_{hash(str(user))}"
    }

@app.get("/api/v1/agents")
async def get_agents():
    """Список доступных AI агентов"""
    return {
        "agents": [
            {
                "id": "crypto_analyzer",
                "name": "crypto_analyzer",
                "display_name": "💰 Crypto Portfolio Analyzer",
                "description": "Анализирует криптовалютный портфель и дает рекомендации по торговле",
                "category": "finance",
                "base_price": 5.0,
                "rating": 95,
                "total_executions": 1234,
                "required_access": "basic"
            },
            {
                "id": "nft_valuator",
                "name": "nft_valuator", 
                "display_name": "🎨 NFT Collection Valuator",
                "description": "Оценивает стоимость NFT коллекций и предсказывает ценовые тренды",
                "category": "finance",
                "base_price": 3.0,
                "rating": 88,
                "total_executions": 856,
                "required_access": "basic"
            },
            {
                "id": "code_reviewer",
                "name": "code_reviewer",
                "display_name": "👨‍💻 AI Code Reviewer", 
                "description": "Проводит детальный анализ кода и предлагает улучшения",
                "category": "productivity",
                "base_price": 2.0,
                "rating": 92,
                "total_executions": 2156,
                "required_access": "basic"
            },
            {
                "id": "market_predictor",
                "name": "market_predictor",
                "display_name": "📈 Market Predictor Pro",
                "description": "Предсказывает движения рынка на основе ИИ анализа",
                "category": "finance",
                "base_price": 10.0,
                "rating": 97,
                "total_executions": 543,
                "required_access": "advanced"
            },
            {
                "id": "degen_advisor",
                "name": "degen_advisor",
                "display_name": "🦍 Degen Trade Advisor",
                "description": "Экстремальный анализ для высокорискованных стратегий",
                "category": "finance",
                "base_price": 20.0,
                "rating": 89,
                "total_executions": 234,
                "required_access": "premium"
            }
        ],
        "allowed_collections": ALLOWED_COLLECTIONS
    }

@app.post("/api/v1/wallet/check-nft")
async def check_wallet_nft(request: NFTCheckRequest):
    """Проверка NFT в кошельке пользователя"""
    try:
        result = await check_nft_ownership(request.wallet_address)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка проверки NFT: {str(e)}")

@app.get("/api/v1/wallet/{wallet_address}/nfts")
async def get_wallet_nfts(wallet_address: str):
    """Получить все NFT в кошельке"""
    try:
        # Получаем все NFT через TON API
        all_nfts = await ton_client.get_account_nfts(wallet_address)
        
        # Получаем адреса разрешенных коллекций
        allowed_addresses = [collection["address"] for collection in ALLOWED_COLLECTIONS]
        
        # Разделяем на разрешенные и остальные
        allowed_nfts = [nft for nft in all_nfts if nft.get("collection") in allowed_addresses]
        other_nfts = [nft for nft in all_nfts if nft.get("collection") not in allowed_addresses]
        
        return {
            "wallet_address": wallet_address,
            "total_nfts": len(all_nfts),
            "allowed_nfts": allowed_nfts,
            "other_nfts": other_nfts,
            "has_access": len(allowed_nfts) > 0,
            "collections_summary": {
                collection["address"]: {
                    "name": collection["name"],
                    "count": len([nft for nft in allowed_nfts if nft.get("collection") == collection["address"]])
                } for collection in ALLOWED_COLLECTIONS
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения NFT: {str(e)}")

@app.get("/api/v1/user/profile")
async def get_user_profile(
    wallet_address: Optional[str] = None,
    telegram_user_id: Optional[int] = None
):
    """Профиль пользователя"""
    nft_data = {"has_access": False, "access_level": "none", "nfts": [], "total_nfts": 0}
    
    if wallet_address:
        nft_data = await check_nft_ownership(wallet_address)
    
    return {
        "user": {
            "id": telegram_user_id or 1,
            "telegram_id": telegram_user_id or 123456789,
            "username": "test_user",
            "display_name": "@test_user",
            "wallet_address": wallet_address,
            "has_nft_access": nft_data["has_access"],
            "access_level": nft_data["access_level"],
            "total_nfts": nft_data["total_nfts"],
            "agents_used_count": 5
        },
        "nfts": nft_data["nfts"]
    }

@app.post("/api/v1/agents/{agent_id}/execute")
async def execute_agent(agent_id: str, request: ExecuteAgentRequest):
    """Выполнение AI агента"""
    
    # Проверяем NFT доступ если указан кошелек
    if request.wallet_address:
        nft_data = await check_nft_ownership(request.wallet_address)
        if not nft_data["has_access"]:
            raise HTTPException(
                status_code=403, 
                detail="Для доступа к агентам требуется NFT из разрешенных коллекций"
            )
    
    # Получаем информацию об агенте
    agents_response = await get_agents()
    agents = agents_response["agents"]
    agent = next((a for a in agents if a["id"] == agent_id), None)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Агент не найден")
    
    # Проверяем уровень доступа
    if request.wallet_address:
        nft_data = await check_nft_ownership(request.wallet_address)
        user_access = nft_data["access_level"]
        required_access = agent["required_access"]
        
        access_hierarchy = {"none": 0, "basic": 1, "advanced": 2, "premium": 3}
        
        if access_hierarchy[user_access] < access_hierarchy[required_access]:
            raise HTTPException(
                status_code=403,
                detail=f"Для этого агента требуется доступ уровня {required_access}"
            )
    
    # Мок выполнения агента
    execution_id = f"exec_{agent_id}_{hash(str(request.dict()))}"
    
    return {
        "execution_id": execution_id,
        "status": "processing",
        "message": f"Агент {agent['display_name']} запущен для выполнения",
        "agent": agent,
        "estimated_completion": "2-5 минут",
        "transaction_hash": request.transaction_hash
    }

@app.get("/api/v1/executions/{execution_id}")
async def get_execution_status(execution_id: str):
    """Статус выполнения агента"""
    # Мок данные статуса
    import random
    
    statuses = ["processing", "completed", "failed"]
    status = random.choice(statuses)
    
    result = {
        "execution_id": execution_id,
        "status": status,
        "progress": random.randint(0, 100) if status == "processing" else 100,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:35:00Z"
    }
    
    if status == "completed":
        result["result"] = {
            "summary": "Анализ завершен успешно",
            "data": {
                "recommendations": [
                    "Рассмотрите диверсификацию портфеля",
                    "Увеличьте долю стейблкоинов",
                    "Следите за волатильностью TON"
                ],
                "risk_score": random.randint(1, 10),
                "confidence": random.randint(70, 95)
            }
        }
    elif status == "failed":
        result["error"] = "Временная недоступность внешних API"
    
    return result

@app.get("/api/v1/collections")
async def get_allowed_collections():
    """Список разрешенных NFT коллекций"""
    return {"collections": ALLOWED_COLLECTIONS}

if __name__ == "__main__":
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 