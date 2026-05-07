from motor.motor_asyncio import AsyncIOMotorClient

from app.config.config import settings

_client: AsyncIOMotorClient | None = None


async def connect_to_mongo():
    global _client

    _client = AsyncIOMotorClient(
        settings.mongo_uri,
        serverSelectionTimeoutMS=5000
    )

    await _client.admin.command("ping")
    db = _client[settings.mongo_db]
    await db["users"].create_index("email", unique=True)
    await db["periods"].create_index(
        [("user_id", 1), ("day", 1)],
        unique=False,
    )


async def close_mongo():
    global _client

    if _client:
        _client.close()
        _client = None


def get_database():
    if _client is None:
        raise RuntimeError("Mongo not connected")

    return _client[settings.mongo_db]