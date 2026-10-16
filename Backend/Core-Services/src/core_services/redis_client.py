from redis.asyncio import Redis

from core_services.config import get_settings  # adjust

redis_client = Redis.from_url(get_settings().REDIS_URL, decode_responses=True)
