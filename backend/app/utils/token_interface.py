from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

class ITokenRepository(ABC):
    @abstractmethod
    async def add_to_blocklist(self, jti: str, expires_at: datetime, user_id: str, tenant_id: str) -> None:
        pass
    
    @abstractmethod
    async def is_token_blocklisted(self, jti: str) -> bool:
        pass
    
    @abstractmethod
    async def cleanup_expired_tokens(self) -> int:
        pass