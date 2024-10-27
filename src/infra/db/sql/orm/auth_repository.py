from typing import List, Optional
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from ..entity.auth_entity import AccountEntity 
from ....resource.handler.sql_resource import SQLResourceHandler
from .....domain.auth.dao.i_auth_repository import IAuthRepository
from .....domain.auth.model.auth_model import UpdatePasswordDTO
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class AuthRepository(IAuthRepository):

    def __init__(self, db: SQLResourceHandler):
        self.db = db
        self.__cls_name = self.__class__.__name__
        
    async def find_account_by_email(self, email: EmailStr, fields: List = ['*']) -> (Optional[AccountEntity]):
        conn: AsyncSession = None
        try:
            if fields == ['*']:
                query = select(AccountEntity).where(AccountEntity.email == email)
            else:
                query = select(*[getattr(AccountEntity, field) for field in fields]).where(AccountEntity.email == email)
                
            conn = await self.db.access()
            result = await conn.execute(query)
            account = result.scalar_one_or_none()
            return account
        except SQLAlchemyError as e:
            log.error(f'Error in %s.find_account_by_email: %s', self.__cls_name, e)
            if conn:
                await conn.rollback()
            return None

    async def create_account(self, account: AccountEntity) -> (AccountEntity):
        conn: AsyncSession = None
        try:
            conn = await self.db.access()
            conn.add(account)
            await conn.commit()
            await conn.refresh(account)
            return account
        except SQLAlchemyError as e:
            log.error(f'Error in %s.create_account: %s', self.__cls_name, e)
            if conn:
                await conn.rollback()
            return None

    async def update_password(self, update_password_params: UpdatePasswordDTO) -> (bool):
        conn: AsyncSession = None
        try:
            query = select(AccountEntity).where(AccountEntity.email == update_password_params.email)
            
            conn = await self.db.access()
            result = await conn.execute(query)
            account = result.scalar_one_or_none()
            if account:
                account.pass_hash = update_password_params.pass_hash
                account.pass_salt = update_password_params.pass_salt
                conn.add(account)
                await conn.commit()
                return True
            else:
                return False
        except SQLAlchemyError as e:
            log.error(f'Error in {self.__cls_name}.update_password: {e}')
            if conn:
                await conn.rollback()
            return False
