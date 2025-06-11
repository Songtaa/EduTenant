from datetime import datetime, timedelta
from app.domains.auth.repository.token_blocklist import TokenBlocklistRepository
from app.config.settings import settings


class TokenService:
    def __init__(self, repository: TokenBlocklistRepository):
        self._repository = repository

    async def revoke_token(self, jti: str, expires_at: settings.JTI_EXPIRY, user_id: str, tenant_id: str) -> None:
        await self._repository.add_to_blocklist(jti, expires_at, user_id, tenant_id)

    async def verify_token_not_blocklisted(self, jti: str) -> bool:
        return not await self._repository.is_token_blocked(jti)

    async def cleanup_tokens(self) -> int:
        return await self._repository.cleanup_expired_tokens()