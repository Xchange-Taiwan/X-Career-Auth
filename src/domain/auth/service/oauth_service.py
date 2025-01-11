from typing import Any, Union, Callable, Optional
from pydantic import EmailStr
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
import hashlib
import uuid
import json
import botocore

from src.config.constant import AccountType
from .auth_service import AuthService
from ..dao.i_auth_repository import IAuthRepository
from ...message.model.email_model import *
from ..model import (
    gateway_auth_model as gw,
    auth_model as auth,
)
from ....domain.auth.model.auth_entity import AccountEntity
from ....infra.util.auth_util import *
from ....infra.client.email import EmailClient
from ....infra.client.async_service_api_adapter import AsyncServiceApiAdapter
from ....config.constant import AccountType
from ....config.exception import *
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class OauthService(AuthService):
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

    """
    OAuth註冊流程
        1. Verify oauth_id
        2. 產生帳戶資料
        3. 將帳戶資料及oauth_id寫入 DB
    """

    async def signup_oauth_google(
        self,
        db: AsyncSession,  # write db
        data: auth.NewOauthAccountDTO,
    ) -> auth.AccountOauthVO:
        # account schema
        account_entity: AccountEntity = None

        try:
            # 1. 產生帳戶資料, no Dict but custom BaseModel
            account_entity = data.gen_account_entity(AccountType.GOOGLE)

            # 2. 將帳戶資料寫入 DB
            account_entity = await self.auth_repo.create_account(db, account_entity)
            if account_entity is None:
                raise ServerException(msg="Google email already registered")

            return auth.AccountOauthVO.parse_obj(account_entity.dict())

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

    async def login_oauth_google(
        self,
        db: AsyncSession,  # read db
        data: gw.LoginOauthDTO,
    ) -> auth.AccountVO:
        # account schema
        account_entity: AccountEntity = None
        try:
            # 1. 取得帳戶資料
            account_entity = await self.auth_repo.find_account_by_oauth_id(
                db=db, oauth_id=data.oauth_id
            )
            if account_entity is None:
                raise NotFoundException(msg="Google account not found")

            # 2. 驗證登入資訊
            if data.email == account_entity.email:
                return auth.AccountOauthVO.parse_obj(account_entity.dict())
            else:
                raise ServerException(msg="Your google account is not valid")

        except Exception as e:
            log.error(
                f"{self.cls_name}.signup [unknown_err] data:%s, account_entity:%s, err:%s",
                data,
                None if account_entity is None else account_entity.dict(),
                e.__str__(),
            )
            err_msg = getattr(e, "msg", "Unable to login")
            raise_http_exception(e=e, msg=err_msg)
