import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, EmailStr, validator
from ..entity.auth_entity import AccountEntity
from ....infra.util.auth_util import *
from ....config.constant import AccountType
from ....config.exception import ClientException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class SignupDTO(BaseModel):
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
                pw=password, 
                pass_salt=pass_salt,
            )

            return AccountEntity(
                aid=aid,
                email=email,
                pass_hash=pass_hash,
                pass_salt=pass_salt,
                user_id=user_id,
                account_type=account_type.value,
                region=region,
            )

        else:
            # TODO: oauth: oauth_id
            return None

class AccountVO(BaseModel):
    aid: int
    email: EmailStr
    user_id: int
    account_type: AccountType
    region: str
