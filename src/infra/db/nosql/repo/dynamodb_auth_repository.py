from typing import Any, List, Optional, Callable
from pydantic import EmailStr
from src.config.conf import DDB_TABLE_ACCOUNTS
from src.domain.auth.dao.i_auth_repository import IAuthRepository
from src.domain.auth.model.auth_model import UpdatePasswordDTO
from src.domain.auth.model.auth_entity import AccountEntity
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class DynamoDBAuthRepository(IAuthRepository):
    def __init__(self):
        self.cls_name = self.__class__.__name__

    async def find_account_by_email(self, db: Any, email: EmailStr, fields: List = ['*']) -> (Optional[AccountEntity]):
        # table name: DDB_TABLE_ACCOUNTS
        pass

    
    async def find_account_by_oauth_id(self, db: Any, oauth_id: str, fields: List = ['*']) -> (Optional[AccountEntity]):
        # 別用這個 function, 外部 OAuth 登入 改用 find_account_by_email
        pass

    """
    class AccountEntity:
        email: Optional[EmailStr] = None # DynamodDB Partition Key
        region: Optional[str] = '' # DynamodDB Sort Key
        aid: Optional[int] = None
        email2: Optional[EmailStr] = None
        pass_hash: Optional[str] = ''
        pass_salt: Optional[str] = ''
        oauth_id: Optional[str] = ''
        refresh_token: Optional[str] = ''
        user_id: Optional[int] = None
        account_type: Optional[AccountType] = None # Enum 轉換成 str
        is_active: Optional[bool] = True
        created_at: Optional[int] = 0
        updated_at: Optional[int] = 0
    """
    async def create_account(self, db: Any, account_entity: AccountEntity) -> (AccountEntity):
        # 1. table name: DDB_TABLE_ACCOUNTS
        # 2. 將 AccountEntity 轉為合法的 dict, account_type -> Enum 轉換成 str
        # email -> DynamodDB Partition Key
        pass

    
    async def update_password(self, db: Any, update_password_params: UpdatePasswordDTO) -> (int):
        # table name: DDB_TABLE_ACCOUNTS
        pass

    
    async def check_and_update_password(self, db: Any, update_password_params: UpdatePasswordDTO, validate_function: Callable) -> (int):
        # table name: DDB_TABLE_ACCOUNTS
        pass

    
    async def delete_account_by_email(self, db: Any, account_entity: AccountEntity) -> (int):
        # table name: DDB_TABLE_ACCOUNTS
        pass
