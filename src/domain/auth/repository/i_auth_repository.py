from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict, List, Any, Optional
from pydantic import EmailStr, BaseModel
from ..data_access_layer.auth_dao import UpdatePasswordDAO
from ..entity.auth_entity import AccountEntity


class IAuthRepository(ABC):

    @abstractmethod
    def find_account_by_email(self, email: EmailStr, fields: List = ['*']) -> (Optional[AccountEntity]):
        pass

    @abstractmethod
    def create_account(self, account: AccountEntity) -> (AccountEntity):
        pass

    @abstractmethod
    def update_password(self, update_password_params: UpdatePasswordDAO) -> (bool):
        pass
