from typing import List, Optional, Callable
from pydantic import EmailStr
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
        self.__cls_name = self.__class__.__name__

    async def find_account_by_email(self, conn: AsyncSession, email: EmailStr, fields: List = ['*']) -> (Optional[AccountEntity]):
        try:
            if fields == ['*']:
                query = select(AccountEntity).where(
                    AccountEntity.email == email)
            else:
                query = select(*[getattr(AccountEntity, field)
                                 for field in fields]).where(AccountEntity.email == email)

            result = await conn.execute(query)
            account = result.scalar_one_or_none()
            return account
        except SQLAlchemyError as e:
            log.error(f'Error in %s.find_account_by_email: %s',
                      self.__cls_name, e)
            await conn.rollback()
            return None

    async def create_account(self, conn: AsyncSession, account: AccountEntity) -> (AccountEntity):
        try:
            conn.add(account)
            await conn.commit()
            await conn.refresh(account)
            return account
        except SQLAlchemyError as e:
            log.error(f'Error in %s.create_account: %s',
                      self.__cls_name, e)
            await conn.rollback()
            return None

    async def update_password(self, conn: AsyncSession, update_password_params: UpdatePasswordDTO) -> (int):
        try:
            query = select(AccountEntity).where(
                AccountEntity.email == update_password_params.email)

            result = await conn.execute(query)
            account = result.scalar_one_or_none()
            # 0: 無資料
            if not account:
                return 0

            # 1: 更新成功
            account.pass_hash = update_password_params.pass_hash
            account.pass_salt = update_password_params.pass_salt
            conn.add(account)
            await conn.commit()
            return 1
        except SQLAlchemyError as e:
            log.error(f'Error in {self.__cls_name}.update_password: {e}')
            await conn.rollback()
            return 0

    async def check_and_update_password(self,
                                        conn: AsyncSession,
                                        update_password_params: UpdatePasswordDTO,
                                        validate_function: Callable) -> (int):
        try:
            query = select(AccountEntity).where(
                AccountEntity.email == update_password_params.email)

            result = await conn.execute(query)
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
            account.pass_hash = update_password_params.pass_hash
            account.pass_salt = update_password_params.pass_salt
            conn.add(account)
            await conn.commit()
            return 1
        except SQLAlchemyError as e:
            log.error(f'Error in {self.__cls_name}.update_password: {e}')
            await conn.rollback()
            return 0
