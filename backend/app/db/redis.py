import redis.asyncio as redis
from app.config.settings import settings

redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"

# Create the async Redis client from URL (preferred)
token_blocklist = redis.Redis.from_url(
    redis_url, decode_responses=True
)

# If you're using host/port instead of URL, use this:
# token_blocklist = redis.Redis(
#     host=settings.REDIS_HOST,
#     port=settings.REDIS_PORT,
#     db=0,
#     decode_responses=True
# )

async def add_jti_to_blocklist(jti: str) -> None:
    """Add a JWT ID to the blocklist with expiration."""
    await token_blocklist.set(name=jti, value="", ex=settings.JTI_EXPIRY)

async def token_in_blocklist(jti: str) -> bool:
    """Check if the JWT ID is in the blocklist."""
    return await token_blocklist.exists(jti) > 0
