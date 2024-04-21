from typing import Any, Union, Callable, Optional
from pydantic import EmailStr
from decimal import Decimal
import hashlib
import uuid

from src.config.constant import AccountType
from ..repository.i_auth_repository import IAuthRepository
from ..model import (
    gateway_auth_model as gw,
    auth_model as auth,
)
from ..entity.auth_entity import AccountEntity
from ..data_access_layer.auth_dao import UpdatePasswordDAO
from ...message.model.email_model import *
from ..model import (
    gateway_auth_model as gw,
    auth_model as auth,
)
from ....infra.util import auth_util
from ....infra.api.email import Email
from ....config.constant import AccountType
from ....config.exception import *
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class AuthService:
    def __init__(self, auth_repo: IAuthRepository, email: Email):
        self.auth_repo = auth_repo
        self.email = email
        self.__cls_name = self.__class__.__name__


    async def send_code_by_email(
        self,
        data: ConfirmCodeDTO,
        exist: bool = False,
    ):
        # entity = db schema
        account_entity: AccountEntity = None
        try:
            account_entity = self.auth_repo.find_account_by_email(
                email=data.email,
                fields=['email', 'region']
            )
        except NotFoundError as e:
            log.error(f'{self.__cls_name}.send_code_by_email [lack with account_entity] \
                data:%s, account_entity:%s, err:%s',
                data, account_entity, e.__str__())
            raise NotFoundException(msg='incomplete_registered_user_information')
                      
        if not exist:
            if account_entity is None:
                await self.email.send_conform_code(email=data.email, confirm_code=data.code)
                return 'email_sent'
            raise DuplicateUserException(msg='email_registered')

        else:
            if account_entity != None:
                await self.email.send_conform_code(email=data.email, confirm_code=data.code)
                return 'email_sent'
            raise NotFoundException(msg='email_not_found')

    '''
    註冊流程
        1. 檢查 email 有沒註冊過
        2. 產生帳戶資料
        3. 將帳戶資料寫入 DB
    '''
    async def signup(
        self,
        data: auth.NewAccountDTO,
    ) -> (auth.AccountVO):
        # account schema
        account_entity: AccountEntity = None
        try:
            # 1. 產生帳戶資料, no Dict but custom BaseModel
            account_entity = data.gen_account_entity(AccountType.XC)

            # 2. 將帳戶資料寫入 DB
            account_entity = self.auth_repo.create_account(account)
            return auth.AccountVO.parse_obj(account_entity)
        
        except Exception as e:
            log.error(f'{self.__cls_name}.signup [unknown_err] \
                data:%s, account_entity:%s, err:%s',
                data, account_entity, e.__str__())
            raise ServerException(msg='unknown_err')

    '''
    登入流程
        1. 取得帳戶資料
        2. 驗證登入資訊
    '''
    async def login(
        self,
        data: gw.LoginDTO,
    ) -> (auth.AccountVO):
        # account schema
        account_entity: AccountEntity = None
        try:
            # 1. 透過 email 取得 account_entity
            account_entity = self.auth_repo.find_account_by_email(email=data.email)
            
            # 2. validation password
            pass_hash = account_entity.pass_hash
            pass_salt = account_entity.pass_salt
            if not auth_util.match_password(pass_hash=pass_hash, pw=data.password, pass_salt=pass_salt):
                raise UnauthorizedException(msg='error_password')

            return auth.AccountVO.parse_obj(account_entity)
        
        except Exception as e:
            log.error(f'{self.__cls_name}.signup [unknown_err] \
                data:%s, account_entity:%s, err:%s',
                data, account_entity, e.__str__())
            raise_http_exception(e)
    

    async def update_password(
        self,
        data: gw.UpdatePasswordDTO,
    ) -> (bool):
        account_entity: AccountEntity = None
        try:
            pass_salt = auth_util.gen_pass_salt()
            pass_hash = auth_util.gen_password_hash(
                data.password, 
                pass_salt
            )
            params = UpdatePasswordDAO(
                email=data.register_email,
                pass_salt=pass_salt,
                pass_hash=pass_hash,
            )
            
            if data.origin_password:
                account_entity = self.auth_repo.find_account_by_email(email=data.register_email)
                if account_entity is None:
                    raise NotFoundException(msg='account_not_found')
                
                if not auth_util.match_password(
                    pass_hash=account_entity.pass_hash, 
                    pw=data.origin_password, 
                    pass_salt=account_entity.pass_salt,
                ):
                    raise ForbiddenException(msg='Invalid Password') 

            return self.auth_repo.update_password(update_password_params=params)
        
        except Exception as e:
            log.error(f'{self.__cls_name}.update_password [unknown_err] \
                data:%s, account_entity:%s, err:%s',
                data, account_entity, e.__str__())
            raise_http_exception(e)


    async def send_reset_password_confirm_email(
        self,
        email: EmailStr
    ) -> str:
        account_entity: AccountEntity = self.auth_repo.find_account_by_email(email=email, fields=['aid'])
        if not account_entity:
            raise ServerException(msg='invalid account')
        token = uuid.uuid1()
        self.email.send_reset_password_comfirm_email(email=email, token=token)
        return token
