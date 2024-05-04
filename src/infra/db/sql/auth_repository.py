from typing import List, Optional
from pydantic import EmailStr
from ....domain.auth.repository.i_auth_repository import IAuthRepository
from ....domain.auth.entity.auth_entity import AccountEntity
from ....domain.auth.model.auth_model import UpdatePasswordDTO
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class AuthRepository(IAuthRepository):
    def __init__(self):
        self.__cls_name = self.__class__.__name__
        
    def find_account_by_email(self, email: EmailStr, fields: List = ['*']) -> (Optional[AccountEntity]):
        pass

    def create_account(self, account: AccountEntity) -> (AccountEntity):
        pass

    def update_password(self, update_password_params: UpdatePasswordDTO) -> (bool):
        pass