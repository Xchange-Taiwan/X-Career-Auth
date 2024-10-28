from typing import Any, Union, Callable, Optional
from pydantic import EmailStr
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib
import uuid

from src.config.constant import AccountType
from ..dao.i_auth_repository import IAuthRepository
from ...message.model.email_model import *
from ..model import (
    gateway_auth_model as gw,
    auth_model as auth,
)
from ....infra.util import auth_util
from ....infra.client.email import EmailClient
from ....infra.db.sql.entity.auth_entity import AccountEntity
from ....config.constant import AccountType
from ....config.exception import *
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class AuthService:
    def __init__(self, auth_repo: IAuthRepository, email_client: EmailClient):
        self.auth_repo = auth_repo
        self.email_client = email_client
        self.__cls_name = self.__class__.__name__


    async def send_code_by_email(
        self,
        data: ConfirmCodeDTO,
    ):
        # entity = db schema
        account_entity: AccountEntity = None
        try:
            account_entity = await self.auth_repo.find_account_by_email(
                email=data.email,
                fields=['email', 'region']
            )
        except Exception as e:
            log.error(f'{self.__cls_name}.send_code_by_email [lack with account_entity] \
                data:%s, account_entity:%s, err:%s',
                      data, account_entity, e.__str__())
            raise NotFoundException(
                msg='Incomplete registered user information')

        try:
            if not data.exist:
                if account_entity is None:
                    await self.email_client.send_conform_code(email=data.email, confirm_code=data.code)
                    return 'email_sent'
                raise DuplicateUserException(msg='Email registered')

            else:
                if account_entity != None:
                    await self.email_client.send_conform_code(email=data.email, confirm_code=data.code)
                    return 'email_sent'
                raise NotFoundException(msg='Email not found')

        except Exception as e:
            log.error(f'{self.__cls_name}.send_code_by_email [email sending error] \
                data:%s, account_entity:%s, err:%s',
                      data, account_entity, e.__str__())
            raise_http_exception(e=e, msg=e.msg if e.msg else 'unknow_error')


    async def send_link_by_email(
        self,
        data: SendEmailDTO,
    ):
        # entity = db schema
        account_entity: AccountEntity = None
        try:
            account_entity = await self.auth_repo.find_account_by_email(
                email=data.email,
                fields=['email', 'region']
            )
        except Exception as e:
            log.error(f'{self.__cls_name}.send_code_by_email [lack with account_entity] \
                data:%s, account_entity:%s, err:%s',
                      data, account_entity, e.__str__())
            raise NotFoundException(
                msg='Incomplete registered user information')

        token = str(uuid.uuid4())
        try:
            if not data.exist:
                if account_entity is None:
                    await self.email_client.send_signup_confirm_email(email=data.email, token=token)
                else:
                    raise DuplicateUserException(msg='Email registered')

            else:
                if account_entity != None:
                    await self.email_client.send_signup_confirm_email(email=data.email, token=token)
                else:
                    raise NotFoundException(msg='Email not found')

        except Exception as e:
            log.error(f'{self.__cls_name}.send_code_by_email [email sending error] \
                data:%s, account_entity:%s, err:%s',
                      data, account_entity, e.__str__())
            raise_http_exception(e=e, msg=e.msg if e.msg else 'unknow_error')

        return {'token': token}


    '''
    註冊流程
        1. 產生帳戶資料
        2. 將帳戶資料寫入 DB
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
            account_entity = await self.auth_repo.create_account(account_entity)
            if account_entity is None:
                raise ServerException(msg='Email already registered')

            return auth.AccountVO.parse_obj(account_entity.dict())

        except Exception as e:
            log.error(f'{self.__cls_name}.signup [unknown_err] \
                data:%s, account_entity:%s, err:%s',
                      data, None if account_entity is None else account_entity.dict(), e.__str__())
            raise_http_exception(e)

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
            # 1. 取得帳戶資料
            account_entity = await self.auth_repo.find_account_by_email(email=data.email)
            if account_entity is None:
                raise NotFoundException(msg='Account not found')

            # 2. 驗證登入資訊
            pass_hash = account_entity.pass_hash
            pass_salt = account_entity.pass_salt
            if not auth_util.match_password(pass_hash=pass_hash, pw=data.password, pass_salt=pass_salt):
                raise UnauthorizedException(msg='Error password')

            return auth.AccountVO.parse_obj(account_entity.dict())

        except Exception as e:
            log.error(f'{self.__cls_name}.signup [unknown_err] \
                data:%s, account_entity:%s, err:%s',
                      data, None if account_entity is None else account_entity.dict(), e.__str__())
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
            params = auth.UpdatePasswordDTO(
                email=data.register_email,
                pass_salt=pass_salt,
                pass_hash=pass_hash,
            )

            if data.origin_password:
                account_entity = await self.auth_repo.find_account_by_email(email=data.register_email)
                if account_entity is None:
                    raise NotFoundException(msg='Account not found')

                if not auth_util.match_password(
                    pass_hash=account_entity.pass_hash,
                    pw=data.origin_password,
                    pass_salt=account_entity.pass_salt,
                ):
                    raise ForbiddenException(msg='Invalid password')

            success = await self.auth_repo.update_password(update_password_params=params)
            if not success:
                raise ServerException(
                    msg='Email not found or update password failed')
            return success

        except Exception as e:
            log.error(f'{self.__cls_name}.update_password [unknown_err] \
                data:%s, account_entity:%s, err:%s',
                      data, None if account_entity is None else account_entity.dict(), e.__str__())
            raise_http_exception(e)

    async def send_reset_password_confirm_email(
        self,
        email: EmailStr
    ) -> str:
        account_entity: AccountEntity = await self.auth_repo.find_account_by_email(email=email, fields=['aid'])
        if not account_entity:
            raise ServerException(msg='Invalid account')
        token = str(uuid.uuid4())
        await self.email_client.send_reset_password_comfirm_email(email=email, token=token)
        return token
