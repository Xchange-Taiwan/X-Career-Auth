from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, List, Any, Optional
from pydantic import EmailStr, BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from ..model.auth_model import UpdatePasswordDTO
from ..entity.auth_entity import AccountEntity


class IAuthRepository(ABC):

    @abstractmethod
    async def find_account_by_email(self, db: AsyncSession, email: EmailStr, fields: List = ['*']) -> (Optional[AccountEntity]):
        pass

    @abstractmethod
    async def create_account(self, db: AsyncSession, account: AccountEntity) -> (AccountEntity):
        pass

    @abstractmethod
    async def update_password(self, db: AsyncSession, update_password_params: UpdatePasswordDTO) -> (bool):
        pass