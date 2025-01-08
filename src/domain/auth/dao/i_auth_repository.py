from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, List, Any, Optional, Callable
from pydantic import EmailStr, BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.auth.model.auth_model import UpdatePasswordDTO
from src.domain.auth.model.auth_entity import AccountEntity


class IAuthRepository(ABC):

    @abstractmethod
    async def find_account_by_email(self, db: AsyncSession, email: EmailStr, fields: List = ['*']) -> (Optional[AccountEntity]):
        pass

    @abstractmethod
    async def find_account_by_oauth_id(self, db: AsyncSession, oauth_id: str, fields: List = ['*']) -> (Optional[AccountEntity]):
        pass

    @abstractmethod
    async def create_account(self, db: AsyncSession, account_entity: AccountEntity) -> (AccountEntity):
        pass

    @abstractmethod
    async def update_password(self, db: AsyncSession, update_password_params: UpdatePasswordDTO) -> (int):
        pass

    @abstractmethod
    async def check_and_update_password(self, db: AsyncSession, update_password_params: UpdatePasswordDTO, validate_function: Callable) -> (int):
        pass

    @abstractmethod
    async def delete_account_by_email(self, db: AsyncSession, account_entity: AccountEntity) -> (int):
        pass
