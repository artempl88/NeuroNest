"""
Упрощенная версия NeuroNest API для быстрого запуска
Используется для разработки и демонстрации
"""

import os
import logging
import hashlib
import hmac
import urllib.parse
from contextlib import asynccontextmanager
from typing import Dict, List, Any

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ton_api import TONAPIClient

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
class Settings:
    # Telegram Bot API Token
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    
    # TON API настройки
    TON_API_KEY = os.getenv("TON_API_KEY", "")
    TONAPI_TOKEN = os.getenv("TONAPI_TOKEN", "")
    
    # Режим разработки
    DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", "true").lower() == "true"
    
    # Разрешенные NFT коллекции
    ALLOWED_NFT_COLLECTIONS = [
        "EQCGbQyAJxxMsYQWLCklkXQq4fkIBK3kz3GA1TkFJyUR9nTH"  # NeuroNest Access Collection
    ]

settings = Settings()

# Pydantic модели
class WalletCheckRequest(BaseModel):
    wallet_address: str = Field(..., min_length=10, max_length=100)

class TelegramInitData(BaseModel):
    init_data: str
    hash: str

class AgentExecutionRequest(BaseModel):
    agent_name: str = Field(..., min_length=1, max_length=100)
    wallet_address: str = Field(..., min_length=10, max_length=100)
    parameters: Dict[str, Any] = Field(default_factory=dict)

# Глобальный TON API клиент
ton_client = TONAPIClient(
    api_key=settings.TON_API_KEY,
    tonapi_token=settings.TONAPI_TOKEN
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    logger.info("🚀 NeuroNest API запускается...")
    
    # Startup
    try:
        logger.info("✅ NeuroNest API готов к работе")
        yield
    finally:
        # Shutdown
        logger.info("🔄 NeuroNest API завершает работу...")

# Создание приложения FastAPI
app = FastAPI(
    title="NeuroNest API",
    description="Упрощенный API для Telegram Mini App с NFT доступом",
    version="1.0.0",
    lifespan=lifespan
)

# CORS настройки
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000", 
        "https://neuronest.app",
        "https://*.telegram.org"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

def verify_telegram_data(init_data: str, bot_token: str = None) -> Dict[str, Any]:
    """
    Проверяет подлинность данных от Telegram WebApp
    """
    if not bot_token or bot_token == "":
        if settings.DEVELOPMENT_MODE:
            logger.warning("🔓 Development mode: пропуск проверки Telegram данных")
            # В режиме разработки парсим данные без проверки подписи
            return parse_init_data_without_verification(init_data)
        else:
            raise HTTPException(status_code=401, detail="Telegram bot token не настроен")
    
    try:
        # Парсим init_data
        parsed_data = dict(urllib.parse.parse_qsl(init_data))
        
        # Извлекаем hash
        received_hash = parsed_data.pop('hash', '')
        if not received_hash:
            raise HTTPException(status_code=401, detail="Отсутствует hash в данных")
        
        # Создаем строку для проверки
        data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(parsed_data.items())])
        
        # Вычисляем ключ
        secret_key = hmac.new("WebAppData".encode(), bot_token.encode(), hashlib.sha256).digest()
        
        # Вычисляем hash
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        # Проверяем hash
        if not hmac.compare_digest(received_hash, calculated_hash):
            raise HTTPException(status_code=401, detail="Неверная подпись данных")
        
        return parsed_data
        
    except Exception as e:
        logger.error(f"Ошибка проверки Telegram данных: {e}")
        if settings.DEVELOPMENT_MODE:
            logger.warning("🔓 Development mode: fallback к парсингу без проверки")
            return parse_init_data_without_verification(init_data)
        raise HTTPException(status_code=401, detail="Ошибка проверки данных")

def parse_init_data_without_verification(init_data: str) -> Dict[str, Any]:
    """Парсинг данных без проверки подписи (только для разработки)"""
    try:
        parsed_data = dict(urllib.parse.parse_qsl(init_data))
        return parsed_data
    except Exception as e:
        logger.error(f"Ошибка парсинга init_data: {e}")
        return {"user": {"id": 12345, "first_name": "Demo", "username": "demo_user"}}

async def check_nft_ownership(wallet_address: str) -> Dict[str, Any]:
    """
    Проверяет владение NFT из разрешенных коллекций
    """
    logger.info(f"Checking NFT ownership for wallet: {wallet_address}")
    logger.info(f"Allowed collections: {settings.ALLOWED_NFT_COLLECTIONS}")
    
    try:
        async with ton_client as client:
            nfts = await client.get_wallet_nfts(wallet_address)
            logger.info(f"Retrieved NFTs: {nfts}")
            
            # Фильтруем NFT из разрешенных коллекций
            valid_nfts = []
            for nft in nfts:
                nft_collection = nft.get("collection")
                is_verified = nft.get("verified", False)
                logger.info(f"Checking NFT: collection={nft_collection}, verified={is_verified}")
                
                if nft_collection in settings.ALLOWED_NFT_COLLECTIONS and is_verified:
                    valid_nfts.append(nft)
                    logger.info(f"Valid NFT found: {nft}")
            
            # Определяем уровень доступа
            access_level = "none"
            has_access = len(valid_nfts) > 0
            
            if has_access:
                nft_count = len(valid_nfts)
                if nft_count >= 10:
                    access_level = "premium"
                elif nft_count >= 3:
                    access_level = "advanced"
                else:
                    access_level = "basic"
            
            result = {
                "has_access": has_access,
                "access_level": access_level,
                "nfts": valid_nfts,
                "total_nfts": len(valid_nfts),
                "all_nfts": nfts,
                "fallback_mode": len(nfts) == 1 and nfts[0].get("name", "").endswith("Pass #1"),
                "debug_info": {
                    "wallet_checked": wallet_address,
                    "allowed_collections": settings.ALLOWED_NFT_COLLECTIONS,
                    "raw_nfts_count": len(nfts),
                    "valid_nfts_count": len(valid_nfts)
                }
            }
            
            logger.info(f"Final result: {result}")
            return result
            
    except Exception as e:
        logger.error(f"Ошибка проверки NFT: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка проверки NFT: {str(e)}")

# API маршруты
@app.get("/health")
async def health_check():
    """Проверка состояния API"""
    return {"status": "healthy", "service": "neuronest-backend"}

@app.post("/api/v1/wallet/check-nft")
async def check_wallet_nft(request: WalletCheckRequest):
    """Проверка NFT в кошельке"""
    try:
        result = await check_nft_ownership(request.wallet_address)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in check_wallet_nft: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

@app.get("/api/v1/wallet/{wallet_address}/nfts")
async def get_wallet_nfts(wallet_address: str):
    """Получение всех NFT кошелька"""
    try:
        async with ton_client as client:
            nfts = await client.get_wallet_nfts(wallet_address)
            return {
                "wallet_address": wallet_address,
                "nfts": nfts,
                "total_count": len(nfts)
            }
    except Exception as e:
        logger.error(f"Error getting wallet NFTs: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения NFT")

@app.post("/api/v1/telegram/verify")
async def verify_telegram(request: TelegramInitData):
    """Проверка данных от Telegram WebApp"""
    try:
        verified_data = verify_telegram_data(request.init_data, settings.TELEGRAM_BOT_TOKEN)
        return {
            "verified": True,
            "user_data": verified_data,
            "development_mode": settings.DEVELOPMENT_MODE
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying Telegram data: {e}")
        raise HTTPException(status_code=500, detail="Ошибка проверки данных")

@app.post("/api/v1/agents/execute")
async def execute_agent(request: AgentExecutionRequest):
    """Выполнение AI агента (заглушка)"""
    try:
        # Проверяем NFT доступ
        nft_check = await check_nft_ownership(request.wallet_address)
        
        if not nft_check["has_access"]:
            raise HTTPException(status_code=403, detail="Требуется NFT доступ")
        
        # Симуляция выполнения агента
        return {
            "status": "success",
            "agent": request.agent_name,
            "wallet": request.wallet_address,
            "access_level": nft_check["access_level"],
            "result": {
                "message": f"Агент {request.agent_name} успешно выполнен",
                "execution_id": f"exec_{hash(request.wallet_address + request.agent_name)}"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing agent: {e}")
        raise HTTPException(status_code=500, detail="Ошибка выполнения агента")

@app.get("/api/v1/collections/allowed")
async def get_allowed_collections():
    """Получение списка разрешенных NFT коллекций"""
    return {
        "collections": [
            {
                "address": addr,
                "name": "NeuroNest Access Collection",
                "description": "Официальная NFT коллекция для доступа к NeuroNest"
            }
            for addr in settings.ALLOWED_NFT_COLLECTIONS
        ]
    }

# Обработчик ошибок
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Обработчик HTTP ошибок"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Запуск NeuroNest API сервера...")
    logger.info(f"🔧 Development mode: {settings.DEVELOPMENT_MODE}")
    logger.info(f"🔑 TON API key configured: {'✅' if settings.TON_API_KEY else '❌'}")
    logger.info(f"🔑 TONAPI token configured: {'✅' if settings.TONAPI_TOKEN else '❌'}")
    logger.info(f"🤖 Telegram bot configured: {'✅' if settings.TELEGRAM_BOT_TOKEN else '❌'}")
    
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 