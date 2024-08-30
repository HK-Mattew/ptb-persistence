import pytest_asyncio
import config

from motor.motor_asyncio import AsyncIOMotorClient

_motor_client = AsyncIOMotorClient(
    config.MONGO_DB_URI
    )

@pytest_asyncio.fixture()
async def motor_client():
    return _motor_client

