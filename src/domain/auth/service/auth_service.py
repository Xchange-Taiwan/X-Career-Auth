from typing import Any, Dict, Union, Callable, Optional
import aioboto3.session
from pydantic import EmailStr
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib
import uuid
import json
import botocore

from src.config.constant import AccountType
from ..dao.i_auth_repository import IAuthRepository
from ...message.model.email_model import *
from ..model import (
    gateway_auth_model as gw,
    auth_model as auth,
)
from ....domain.auth.model.auth_entity import AccountEntity
from ....infra.util import auth_util
from ....infra.client.email import EmailClient
from ....infra.client.async_service_api_adapter import AsyncServiceApiAdapter
from ....config.constant import AccountType
from ....config.exception import *
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        auth_repo: IAuthRepository,
        email_client: EmailClient,
        http_request: AsyncServiceApiAdapter,
    ):
        self.auth_repo = auth_repo
        self.email_client = email_client
        self.http_request = http_request
        self.cls_name = self.__class__.__name__


    async def send_code_by_email(
        self,
        db: AsyncSession,  # read db
        data: ConfirmCodeDTO,
    ):
        # entity = db schema
        account_entity: AccountEntity = None
        try:
            account_entity = await self.auth_repo.find_account_by_email(
                db=db, email=data.email, fields=["email", "region"]
            )

            # email sending
            if not data.exist:
                if account_entity is None:
                    await self.email_client.send_conform_code(
                        email=data.email, confirm_code=data.code
                    )
                    return "email_sent"
                raise DuplicateUserException(msg="Email registered")
            else:
                if account_entity != None:
                    await self.email_client.send_conform_code(
                        email=data.email, confirm_code=data.code
                    )
                    return "email_sent"
                raise NotFoundException(msg="Email not found")

        except Exception as e:
            log.error(
                f"{self.cls_name}.send_code_by_email [database OR email sending error] data: %s, account_entity: %s, err: %s",
                data,
                account_entity,
                e.__str__(),
            )
            err_msg = getattr(e, "msg", "Unable to send code by email")
            raise_http_exception(e=e, msg=err_msg)


    async def send_link_by_email(
        self,
        db: AsyncSession,  # read db
        data: SendEmailDTO,
    ):
        # entity = db schema
        account_entity: AccountEntity = None
        token: str = None
        try:
            account_entity = await self.auth_repo.find_account_by_email(
                db=db, email=data.email, fields=["email", "region"]
            )

            # email sending
            token: str = str(uuid.uuid4())
            if not data.exist:
                if account_entity is None:
                    await self.email_client.send_signup_confirm_email(
                        email=data.email, token=token
                    )
                else:
                    raise DuplicateUserException(msg="Email registered")
            else:
                if account_entity != None:
                    await self.email_client.send_signup_confirm_email(
                        email=data.email, token=token
                    )
                else:
                    raise NotFoundException(msg="Email not found")

        except Exception as e:
            log.error(
                f"{self.cls_name}.send_link_by_email [database OR email sending error] data: %s, account_entity: %s, err: %s",
                data,
                account_entity,
                e.__str__(),
            )
            err_msg = getattr(e, "msg", "Unable to send link by email")
            raise_http_exception(e=e, msg=err_msg)
        return {"token": token}




    """
    註冊流程
        1. 產生帳戶資料
        2. 將帳戶資料寫入 DB
    """

    async def signup(
        self,
        db: AsyncSession,  # write db
        data: auth.NewAccountDTO,
    ) -> auth.AccountVO:
        # account schema
        account_entity: AccountEntity = None

        try:
            # 1. 產生帳戶資料, no Dict but custom BaseModel
            account_entity = data.gen_account_entity(AccountType.XC)

            # 2. 將帳戶資料寫入 DB
            account_entity = await self.auth_repo.create_account(db, account_entity)
            if account_entity is None:
                raise ServerException(msg="Email already registered")

            return auth.AccountVO.parse_obj(account_entity.dict())

        except Exception as e:
            log.error(
                f"{self.cls_name}.signup [unknown_err] data:%s, account_entity:%s, err:%s",
                data,
                None if account_entity is None else account_entity.dict(),
                e.__str__(),
            )
            err_msg = getattr(e, "msg", "Unable to signup")
            raise_http_exception(e=e, msg=err_msg)


    """
    登入流程
        1. 取得帳戶資料
        2. 驗證登入資訊
    """

    async def login(
        self,
        db: AsyncSession,  # read db
        data: gw.LoginDTO,
    ) -> auth.AccountVO:
        # account schema
        account_entity: AccountEntity = None
        try:
            # 1. 取得帳戶資料
            account_entity = await self.auth_repo.find_account_by_email(
                db=db, email=data.email
            )
            if account_entity is None:
                raise NotFoundException(msg="Account not found")
            
            if account_entity.account_type != AccountType.XC:
                raise UnauthorizedException(msg=f"You registered as a {account_entity.account_type.value} account")

            # 2. 驗證登入資訊
            pass_hash = account_entity.pass_hash
            pass_salt = account_entity.pass_salt
            if not auth_util.match_password(
                pass_hash=pass_hash, pw=data.password, pass_salt=pass_salt
            ):
                raise UnauthorizedException(msg="Error password")

            return auth.AccountVO.parse_obj(account_entity.dict())

        except Exception as e:
            log.error(
                f"{self.cls_name}.signup [unknown_err] data:%s, account_entity:%s, err:%s",
                data,
                None if account_entity is None else account_entity.dict(),
                e.__str__(),
            )
            err_msg = getattr(e, "msg", "Unable to login")
            raise_http_exception(e=e, msg=err_msg)

    async def update_password(
        self,
        db: AsyncSession,  # write db
        data: gw.UpdatePasswordDTO,
    ) -> bool:
        account_entity: AccountEntity = None
        try:
            pass_salt = auth_util.gen_pass_salt()
            pass_hash = auth_util.gen_password_hash(data.password, pass_salt)
            params = auth.UpdatePasswordDTO(
                email=data.register_email,
                pass_salt=pass_salt,
                pass_hash=pass_hash,
                origin_password=data.origin_password,  # for password validation in repository
            )

            if data.origin_password:
                effect_row = await self.auth_repo.check_and_update_password(
                    db=db,
                    update_password_params=params,
                    validate_function=auth_util.match_password,
                )
                if effect_row == 0:
                    raise NotFoundException(msg="Account not found")

                if effect_row == -1:
                    raise ForbiddenException(msg="Invalid password")
            else:
                effect_row = await self.auth_repo.update_password(
                    db=db, update_password_params=params
                )
                if effect_row == 0:
                    raise ServerException(
                        msg="Account not found or update password failed"
                    )
            return True

        except Exception as e:
            log.error(
                f"{self.cls_name}.update_password [unknown_err] data: %s, account_entity: %s, err: %s",
                data,
                None if account_entity is None else account_entity.dict(),
                e.__str__(),
            )
            err_msg = getattr(e, "msg", "Unable to update password")
            raise_http_exception(e=e, msg=err_msg)

    async def send_reset_password_confirm_email(
        self, db: AsyncSession, email: EmailStr  # read db
    ) -> str:
        try:
            account_entity: AccountEntity = await self.auth_repo.find_account_by_email(
                db=db, email=email, fields=["aid"]
            )
            if not account_entity:
                raise ServerException(msg="Invalid account")
            token = str(uuid.uuid4())
            await self.email_client.send_reset_password_comfirm_email(
                email=email, token=token
            )
            return token
        except Exception as e:
            log.error(
                f"{self.cls_name}.send_reset_password_confirm_email [unknown_err] email: %s, err: %s",
                email,
                e.__str__(),
            )
            err_msg = getattr(e, "msg", "Unable to send email")
            raise_http_exception(e=e, msg=err_msg)
