from typing import List, Optional
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from .....domain.auth.dao.i_auth_repository import IAuthRepository
from .....domain.auth.entity.auth_entity import AccountEntity
from .....domain.auth.model.auth_model import UpdatePasswordDTO
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class AuthRepository(IAuthRepository):
    def __init__(self):
        self.__cls_name = self.__class__.__name__
        
    async def find_account_by_email(self, db: AsyncSession, email: EmailStr, fields: List = ['*']) -> (Optional[AccountEntity]):
        try:
            if fields == ['*']:
                query = select(AccountEntity).where(AccountEntity.email == email)
            else:
                query = select(*[getattr(AccountEntity, field) for field in fields]).where(AccountEntity.email == email)
                
            result = await db.execute(query)
            account = result.scalar_one_or_none()
            return account
        except SQLAlchemyError as e:
            log.error(f'Error in %s.find_account_by_email: %s', self.__cls_name, e)
            return None

    async def create_account(self, db: AsyncSession, account: AccountEntity) -> (AccountEntity):
        try:
            db.add(account)
            await db.commit()
            await db.refresh(account)
            return account
        except SQLAlchemyError as e:
            await db.rollback()
            log.error(f'Error in %s.create_account: %s', self.__cls_name, e)
            return None

    async def update_password(self, db: AsyncSession, update_password_params: UpdatePasswordDTO) -> (bool):
        try:
            query = select(AccountEntity).where(AccountEntity.email == update_password_params.email)
            result = await db.execute(query)
            account = result.scalar_one_or_none()
            if account:
                account.pass_hash = update_password_params.pass_hash
                account.pass_salt = update_password_params.pass_salt
                db.add(account)
                await db.commit()
                return True
            else:
                return False
        except SQLAlchemyError as e:
            await db.rollback()
            log.error(f'Error in {self.__cls_name}.update_password: {e}')
            return False