from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET

from aiohttp import ClientSession
from redis import asyncio as redis
from redis.asyncio.client import Redis


class RedisClient:
    def __init__(self) -> None:
        self.client: Redis = redis.Redis(
            host='redis',
            port=6379,
            db=0,
            decode_responses=True
        )

    async def gather_all_info(self) -> str:
        cursor = '0'
        keys = []
        while cursor != 0:
            cursor, batch = await self.client.scan(cursor, match='*')
            keys.extend(batch)
        keys_values = {}
        for key in keys:
            keys_values[key] = await self.client.get(key)
        text = ''
        for key, value in keys_values.items():
            text += f'{key} - {value} \n'
        return text

    async def inser_currency(self, key: str, value: str) -> None:
        target_time = (
            datetime
            .now(timezone.utc)
            .replace(hour=9, minute=0, second=0, microsecond=0)
        )
        if target_time < datetime.now(timezone.utc):
            target_time += timedelta(days=1)
        timestamp = int(target_time.timestamp())
        await self.client.set(key, value)
        await self.client.expireat(key, timestamp)

    async def get_currency(self, key: str) -> str:
        return await self.client.get(key)

    async def is_not_empty(self) -> bool:
        cursor = '0'
        _, batch = await self.client.scan(cursor, match='*')
        return bool(batch)

    async def insert_currencies(self, url) -> None:
        async with ClientSession() as session:
            async with session.get(url) as response:
                text = await response.text()
                root = ET.fromstring(text)
                for elem in root.findall('Valute'):
                    current_code = elem.find('CharCode').text
                    current_rate = elem.find('VunitRate').text
                    await self.inser_currency(current_code, current_rate)

    def buy_foreign_currency(self, rate: str, amount: float) -> float:
        rate = float('.'.join(rate.split(',')))
        return round(amount / rate, 2)

    def sell_foreign_currency(self, rate: str, amount: float) -> float:
        rate = float('.'.join(rate.split(',')))
        return round(amount * rate, 2)
