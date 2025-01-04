import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, EmailStr, validator, Field
from ....infra.util.auth_util import *
from ....infra.db.sql.entity.auth_entity import AccountEntity
from ....config.constant import AccountType
from ....config.exception import ClientException
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class NewAccountDTO(BaseModel):
    # region: pass by gateway
    region: str
    email: EmailStr
    password: str

    # TODO: implement, no Dict
    def gen_account_entity(self, account_type: AccountType) -> (AccountEntity):
        aid = gen_snowflake_id()
        user_id = gen_snowflake_id()

        if account_type == AccountType.XC:
            pass_salt = gen_pass_salt()
            pass_hash = gen_password_hash(
                pw=self.password,
                pass_salt=pass_salt,
            )

            return AccountEntity(
                aid=aid,
                email=self.email,
                pass_hash=pass_hash,
                pass_salt=pass_salt,
                user_id=user_id,
                account_type=account_type.value,
                region=self.region,
            )

        else:
            # TODO: oauth: oauth_id
            return None


class NewOauthAccountDTO(BaseModel):
    # region: pass by gateway
    region: str
    email: EmailStr
    oauth_id: str
    access_token: str

    # TODO: implement, no Dict
    def gen_account_entity(self, account_type: AccountType) -> (AccountEntity):
        aid = gen_snowflake_id()
        user_id = gen_snowflake_id()

        if account_type == AccountType.GOOGLE:
            return AccountEntity(
                aid=aid,
                email=self.email,
                user_id=user_id,
                pass_hash='',
                pass_salt='',
                account_type=account_type.value,
                region=self.region,
                oauth_id=self.oauth_id
            )


class UpdatePasswordDTO(BaseModel):
    pass_hash: str
    pass_salt: str
    email: EmailStr
    # NOTE: for password validation in repository
    origin_password: Optional[str] = None


class AccountVO(BaseModel):
    aid: int
    email: EmailStr
    account_type: AccountType
    region: str
    user_id: int

    class Config:
        use_enum_values = True


class AccountOauthVO(AccountVO):
    oauth_id: str
    account_type: AccountType = Field(default=AccountType.GOOGLE)
