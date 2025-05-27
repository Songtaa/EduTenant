from uuid import uuid4
from sqlalchemy import delete, select
from app.utils.token_interface import ITokenRepository
from sqlmodel.ext.asyncio.session import AsyncSession
from app.domains.auth.models.token_blocklist import TokenBlocklist
from datetime import datetime
from app.config.settings import settings


class TokenBlocklistRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_token_blocked(self, jti: str, tenant: str | None = None) -> bool:
        stmt = select(TokenBlocklist).where(TokenBlocklist.jti == jti)
        if tenant:
            stmt = stmt.where(TokenBlocklist.tenant == tenant)
        else:
            stmt = stmt.where(TokenBlocklist.tenant.is_(None))

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def add_token_to_blocklist(self, jti: str, expires_at: datetime, user_id: str, tenant: str | None = None):
        token_entry = TokenBlocklist(
            jti=jti,
            expires_at=expires_at,
            user_id=user_id,
            tenant=tenant
        )
        self.session.add(token_entry)
        await self.session.commit()

    async def cleanup_expired_tokens(self) -> int:
        stmt = delete(TokenBlocklist).where(TokenBlocklist.expires_at < datetime.utcnow())
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount


# class TokenBlocklistRepository:
#     def __init__(self, session: AsyncSession):
#         self.session = session

#     async def is_token_blocked(self, jti: str, tenant: str | None) -> bool:
#         stmt = select(TokenBlocklist).where(TokenBlocklist.jti == jti)
#         if tenant:
#             stmt = stmt.where(TokenBlocklist.tenant == tenant)
#         else:
#             stmt = stmt.where(TokenBlocklist.tenant.is_(None))

#         result = await self.session.execute(stmt)
#         return result.scalar_one_or_none() is not None

#     async def add_token_to_blocklist(self, jti: str, tenant: str | None):
#         token_entry = TokenBlocklist(jti=jti, tenant=tenant)
#         self.session.add(token_entry)
#         await self.session.commit()

    

#     async def cleanup_expired_tokens(self) -> int:
#         result = await self._session.execute(
#             delete(TokenBlocklist).where(TokenBlocklist.expires_at < datetime.now)
#         )
#         await self._session.commit()
#         return result.rowcount