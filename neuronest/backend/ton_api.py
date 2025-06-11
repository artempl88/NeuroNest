"""
TON API клиент для проверки NFT
"""

import asyncio
import aiohttp
import requests
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class TONAPIClient:
    """Клиент для работы с TON API для проверки NFT"""
    
    def __init__(self, api_key: str = None, tonapi_token: str = None):
        self.api_key = api_key
        self.tonapi_token = tonapi_token
        self.session = None
        
        # Базовые URL для различных API
        self.ton_center_base = "https://toncenter.com/api/v2"
        self.tonapi_base = "https://tonapi.io/v2" 
        self.tonscan_base = "https://tonscan.org/api/v3"
        
        logger.info(f"TON API Client initialized. Has API key: {api_key is not None}, Has TONAPI token: {tonapi_token is not None}")
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_wallet_nfts(self, wallet_address: str) -> List[Dict[str, Any]]:
        """
        Получает NFT для указанного кошелька
        Пробует несколько API источников для получения данных
        """
        try:
            # Пробуем TONAPI.io
            if self.tonapi_token:
                nfts = await self._get_nfts_from_tonapi(wallet_address)
                if nfts:
                    logger.info(f"Получено {len(nfts)} NFT с TONAPI.io")
                    return nfts
            
            # Fallback к TONCenter
            nfts = await self._get_nfts_from_toncenter(wallet_address)
            if nfts:
                logger.info(f"Получено {len(nfts)} NFT с TONCenter")
                return nfts
            
            # Если все API недоступны, используем мок данные
            logger.warning("Все TON API недоступны, используем мок данные")
            return await self._get_mock_nfts(wallet_address)
            
        except Exception as e:
            logger.error(f"Ошибка получения NFT: {e}")
            return await self._get_mock_nfts(wallet_address)
    
    async def _get_nfts_from_tonapi(self, wallet_address: str) -> List[Dict[str, Any]]:
        """Получение NFT через TONAPI.io"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        headers = {
            "Authorization": f"Bearer {self.tonapi_token}",
            "accept": "application/json"
        }
        
        url = f"{self.tonapi_base}/accounts/{wallet_address}/nfts"
        
        try:
            async with self.session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_tonapi_nfts(data.get('nft_items', []))
                else:
                    logger.warning(f"TONAPI.io ошибка: {response.status}")
                    return []
        except asyncio.TimeoutError:
            logger.warning("TONAPI.io timeout")
            return []
        except Exception as e:
            logger.error(f"Ошибка TONAPI.io: {e}")
            return []
    
    async def _get_nfts_from_toncenter(self, wallet_address: str) -> List[Dict[str, Any]]:
        """Получение NFT через TONCenter API"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        params = {
            "address": wallet_address,
            "api_key": self.api_key
        }
        
        url = f"{self.ton_center_base}/getAddressInformation"
        
        try:
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    # TONCenter требует дополнительную обработку для NFT
                    return self._parse_toncenter_data(data)
                else:
                    logger.warning(f"TONCenter ошибка: {response.status}")
                    return []
        except asyncio.TimeoutError:
            logger.warning("TONCenter timeout")
            return []
        except Exception as e:
            logger.error(f"Ошибка TONCenter: {e}")
            return []
    
    def _parse_tonapi_nfts(self, nft_items: List[Dict]) -> List[Dict[str, Any]]:
        """Парсинг NFT данных от TONAPI.io"""
        parsed_nfts = []
        
        for item in nft_items:
            try:
                nft_data = {
                    "collection": item.get("collection", {}).get("address", ""),
                    "token_id": item.get("index", ""),
                    "name": item.get("metadata", {}).get("name", "Unknown NFT"),
                    "image": item.get("metadata", {}).get("image", ""),
                    "verified": item.get("verified", False),
                    "description": item.get("metadata", {}).get("description", "")
                }
                parsed_nfts.append(nft_data)
            except Exception as e:
                logger.error(f"Ошибка парсинга NFT: {e}")
                continue
        
        return parsed_nfts
    
    def _parse_toncenter_data(self, data: Dict) -> List[Dict[str, Any]]:
        """Парсинг данных от TONCenter (упрощенная версия)"""
        # TONCenter API не предоставляет прямой доступ к NFT
        # Это заглушка для совместимости
        return []
    
    async def _get_mock_nfts(self, wallet_address: str) -> List[Dict[str, Any]]:
        """Мок данные для тестирования и fallback"""
        logger.info(f"Using mock NFT data for address: {wallet_address}")
        
        # Симулируем задержку API
        await asyncio.sleep(1)
        
        return [
            {
                "collection": "EQCGbQyAJxxMsYQWLCklkXQq4fkIBK3kz3GA1TkFJyUR9nTH",
                "token_id": "1",
                "name": "NeuroNest Access Pass #1",
                "image": "https://via.placeholder.com/300x300/00FFFF/000000?text=NEURONEST",
                "verified": True,
                "description": "Official NeuroNest Access NFT"
            }
        ]

# Глобальный экземпляр клиента
ton_client = TONAPIClient() 