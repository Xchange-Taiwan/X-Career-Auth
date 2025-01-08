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
from ....config.conf import XC_AUTH_BUCKET
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
        s3_client: Any,
        data: auth.NewOauthAccountDTO,
    ) -> auth.AccountOauthVO:
        # account schema
        account_entity: AccountEntity = None
        object_key = f'accounts/{data.email}.json'
        try:
            # 1. 檢查 S3 是否已經有帳戶資料，若有則拋錯
            response = await s3_client.head_object(
                Bucket=XC_AUTH_BUCKET,
                Key=object_key
            )
            if self.s3_has_object(response):
                raise DuplicateUserException(msg='Email already registered in global storage')
        except botocore.exceptions.ClientError as e:
            self.s3_client_error(e)

        try:
            # 2. 產生帳戶資料, no Dict but custom BaseModel
            account_entity = data.gen_account_entity(AccountType.GOOGLE)

            # 3. 將帳戶資料寫入 S3 (email, region, account_type, oauth_id)
            # await self.register_account_to_global_storage(s3_client, account_entity)
            # stoage_session = await self.storage_rsc.access()
            # async with stoage_session as s3_client:
            account_data = account_entity.register_format()  # 將帳戶資料轉換為字典格式
            await s3_client.put_object(
                Bucket=XC_AUTH_BUCKET,
                Key=object_key,
                Body=json.dumps(account_data),
                ContentType='application/json'
            )

            # 4. 將帳戶資料寫入 DB
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
