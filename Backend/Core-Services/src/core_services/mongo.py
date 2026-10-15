from beanie import init_beanie
from pymongo import AsyncMongoClient

from core_services.config import get_settings
from core_services.models.category import Category

settings = get_settings()

mongo_client: AsyncMongoClient | None = None


async def init_mongo() -> None:
    global mongo_client
    mongo_client = AsyncMongoClient(settings.MONGODB_URL)
    await init_beanie(
        database=mongo_client[settings.MONGODB_DB_NAME],
        document_models=[Category],
    )


async def close_mongo() -> None:
    if mongo_client is not None:
        await mongo_client.close()
