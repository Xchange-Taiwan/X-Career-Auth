from typing import List, Optional, Callable
from pydantic import EmailStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from ..entity.auth_entity import AccountEntity
from .....domain.auth.dao.i_auth_repository import IAuthRepository
from .....domain.auth.model.auth_model import UpdatePasswordDTO
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class AuthRepository(IAuthRepository):

    def __init__(self):
        self.cls_name = self.__class__.__name__

    async def find_account_by_email(self, db: AsyncSession, email: EmailStr, fields: List = ['*']) -> (Optional[AccountEntity]):
        try:
            if fields == ['*']:
                query = select(AccountEntity).where(
                    AccountEntity.email == email)
            else:
                query = select(*[getattr(AccountEntity, field)
                                 for field in fields]).where(AccountEntity.email == email)

            result = await db.execute(query)
            account = result.scalar_one_or_none()
            return account
        except SQLAlchemyError as e:
            log.error(f'Error in %s.find_account_by_email: %s',
                      self.cls_name, e)
            return None

    async def find_account_by_oauth_id(self, db: AsyncSession, oauth_id: str, fields: List = ['*']) -> (Optional[AccountEntity]):
        try:
            if fields == ['*']:
                query = select(AccountEntity).where(
                    AccountEntity.oauth_id == oauth_id)
            else:
                query = select(*[getattr(AccountEntity, field)
                                 for field in fields]).where(AccountEntity.oauth_id == oauth_id)

            result = await db.execute(query)
            account = result.scalar_one_or_none()
            return account
        except SQLAlchemyError as e:
            log.error(f'Error in %s.find_account_by_oauth_id: %s',
                      self.cls_name, e)
            return None

    async def create_account(self, db: AsyncSession, account: AccountEntity) -> (AccountEntity):
        try:
            # await db.execute(text('BEGIN'))
            db.add(account)
            await db.commit()
            await db.refresh(account)
            return account
        except SQLAlchemyError as e:
            log.error(f'Error in %s.create_account: %s',
                      self.cls_name, e)
            await db.rollback()
            return None

    async def update_password(self, db: AsyncSession, update_password_params: UpdatePasswordDTO) -> (int):
        try:
            query = select(AccountEntity).where(
                AccountEntity.email == update_password_params.email)

            result = await db.execute(query)
            account = result.scalar_one_or_none()
            # 0: 無資料
            if not account:
                return 0

            # 1: 更新成功
            # await db.execute(text('BEGIN'))
            account.pass_hash = update_password_params.pass_hash
            account.pass_salt = update_password_params.pass_salt
            db.add(account)
            await db.commit()
            return 1
        except SQLAlchemyError as e:
            log.error(f'Error in {self.cls_name}.update_password: {e}')
            await db.rollback()
            return 0

    async def check_and_update_password(self,
                                        db: AsyncSession,
                                        update_password_params: UpdatePasswordDTO,
                                        validate_function: Callable) -> (int):
        try:
            query = select(AccountEntity).where(
                AccountEntity.email == update_password_params.email)

            result = await db.execute(query)
            account = result.scalar_one_or_none()
            # 0: 無資料
            if not account:
                return 0

            # TODO: compare password
            # 透過外部的 validate function 來比對密碼: -1: 驗證失敗
            if not validate_function(
                    pass_hash=account.pass_hash,
                    pw=update_password_params.origin_password,
                    pass_salt=account.pass_salt):
                return -1

            # 1: 更新成功
            # await db.execute(text('BEGIN'))
            account.pass_hash = update_password_params.pass_hash
            account.pass_salt = update_password_params.pass_salt
            db.add(account)
            await db.commit()
            return 1
        except SQLAlchemyError as e:
            log.error(f'Error in {self.cls_name}.update_password: {e}')
            await db.rollback()
            return 0
