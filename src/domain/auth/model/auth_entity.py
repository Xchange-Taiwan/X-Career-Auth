from typing import Optional
from pydantic import BaseModel, EmailStr
from src.config.constant import AccountType
from src.infra.util.time_util import current_seconds
from src.infra.db.sql.entity.auth_entity import Account

class AccountEntity(BaseModel):
    aid: Optional[int] = None
    email: Optional[EmailStr] = None
    email2: Optional[EmailStr] = None
    pass_hash: Optional[str] = ''
    pass_salt: Optional[str] = ''
    oauth_id: Optional[str] = ''
    refresh_token: Optional[str] = ''
    user_id: Optional[int] = None
    account_type: Optional[AccountType] = None
    is_active: Optional[bool] = True
    region: Optional[str] = ''
    created_at: Optional[int] = 0
    updated_at: Optional[int] = 0

    class Config:
        orm_mode = True


    def register_format(self):
        if self.account_type is None:
            raise ValueError('Account type is required')

        return {
            'email': self.email,
            'account_type': self.account_type.value,
            'oauth_id': self.oauth_id,
            'region': self.region,
        }


    @staticmethod
    def from_orm(account: Account):
        return AccountEntity(
            aid=getattr(account, 'aid', None),
            email=getattr(account, 'email', None),
            email2=getattr(account, 'email2', None),
            pass_hash=getattr(account, 'pass_hash', ''),
            pass_salt=getattr(account, 'pass_salt', ''),
            oauth_id=getattr(account, 'oauth_id', ''),
            refresh_token=getattr(account, 'refresh_token', ''),
            user_id=getattr(account, 'user_id', None),
            account_type=AccountType(getattr(account, 'account_type', AccountType.XC.value)),
            is_active=getattr(account, 'is_active', True),
            region=getattr(account, 'region', None),
        )

    def to_orm(self):
        return Account(
            aid=self.aid,
            email=self.email,
            email2=self.email2,
            pass_hash=self.pass_hash,
            pass_salt=self.pass_salt,
            oauth_id=self.oauth_id,
            refresh_token=self.refresh_token,
            user_id=self.user_id,
            account_type=getattr(self.account_type, 'value', AccountType.XC.value),
            is_active=self.is_active,
            region=self.region,
        )
