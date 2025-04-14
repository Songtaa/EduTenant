from app.domains.auth.schemas.user_schema import UserCreate
from app.domains.auth.services.user_service import UserService
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

async def seed_admin_user(
    session: AsyncSession,
    user_data: UserCreate,
) -> None:
    """Seeds a default admin user in the given session."""
    user_service = UserService(session)

    if await user_service.user_exists(user_data.email):
        logger.info(f"Admin user {user_data.email} already exists. Skipping.")
        return

    logger.info(f"Seeding admin user: {user_data.email}")
    await user_service.create(user_data)
    await session.commit()
    logger.info("Admin user created successfully.")



