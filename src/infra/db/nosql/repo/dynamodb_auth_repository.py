from typing import Any, List, Optional, Callable
from pydantic import EmailStr
from src.config.conf import DDB_TABLE_ACCOUNTS
from src.domain.auth.dao.i_auth_repository import IAuthRepository
from src.domain.auth.model.auth_model import UpdatePasswordDTO
from src.domain.auth.model.auth_entity import AccountEntity
import logging

log = logging.getLogger(__name__)


class DynamoDBAuthRepository(IAuthRepository):
    def __init__(self):
        self.cls_name = self.__class__.__name__


    async def find_account_by_email(
        self, db: Any, email: EmailStr, fields: List = ['*']
    ) -> Optional[AccountEntity]:
        try:
            table = await db.Table(DDB_TABLE_ACCOUNTS)
            response = await table.get_item(Key={'email': email})
            account_data = response.get('Item')
            if account_data:
                if fields == ['*']:
                    return AccountEntity(**account_data)
                else:
                    filtered_data = {
                        field: account_data[field]
                        for field in fields
                        if field in account_data
                    }
                    return AccountEntity(**filtered_data)
            return None
        except Exception as e:
            log.error('Error in find_account_by_email: %s, %s', email, e)
            return None


    async def find_account_by_oauth_id(
        self, db: Any, oauth_id: str, fields: List = ['*']
    ) -> Optional[AccountEntity]:
        # 別用這個 function, 外部 OAuth 登入 改用 find_account_by_email
        pass


    async def create_account(
        self, db: Any, account_entity: AccountEntity
    ) -> AccountEntity:
        account_data = {
            'email': account_entity.email,
            'region': account_entity.region,
            'aid': account_entity.aid,
            'email2': account_entity.email2,
            'pass_hash': account_entity.pass_hash,
            'pass_salt': account_entity.pass_salt,
            'oauth_id': account_entity.oauth_id,
            'refresh_token': account_entity.refresh_token,
            'user_id': account_entity.user_id,
            'account_type': (
                str(account_entity.account_type.value)
                if account_entity.account_type
                else None
            ),
            'is_active': account_entity.is_active,
            'created_at': account_entity.created_at,
            'updated_at': account_entity.updated_at,
        }

        try:
            table = await db.Table(DDB_TABLE_ACCOUNTS)
            await table.put_item(
                Item=account_data,
                ConditionExpression='attribute_not_exists(email)',
            )
        except Exception as e:
            log.error('Error in create_account: %s, %s', account_data, e)
            return None

        return account_entity


    async def update_password(
        self, db: Any, update_password_params: UpdatePasswordDTO
    ) -> int:
        try:
            account_data = {
                'email': update_password_params.email,
                'pass_hash': update_password_params.pass_hash,
                'pass_salt': update_password_params.pass_salt,
            }
            table = await db.Table(DDB_TABLE_ACCOUNTS)
            response = await table.update_item(
                Key={
                    'email': account_data['email'],  # 使用 email 作為主鍵
                },
                UpdateExpression='SET pass_hash = :hash, pass_salt = :salt',
                ExpressionAttributeValues={
                    ':hash': account_data['pass_hash'],
                    ':salt': account_data['pass_salt'],
                },
            )
            return 1 if response else 0
        except Exception as e:
            log.error('Error in update_password: %s, %s', account_data, e)
            return 0


    async def check_and_update_password(
        self,
        db: Any,
        update_password_params: UpdatePasswordDTO,
        validate_function: Callable,
    ) -> int:
        try:
            table = await db.Table(DDB_TABLE_ACCOUNTS)
            response = await table.get_item(
                Key={
                    'email': update_password_params.email,  # 使用 email 作為主鍵
                }
            )
            account = response.get('Item')

            # 0: 無資料
            if not account:
                return 0

            # 透過外部的 validate function 來比對密碼: -1: 驗證失敗
            if not validate_function(
                pass_hash=account['pass_hash'],
                pw=update_password_params.origin_password,
                pass_salt=account['pass_salt'],
            ):
                return -1

            # 更新密碼
            account_data = {
                'email': update_password_params.email,
                'pass_hash': update_password_params.pass_hash,
                'pass_salt': update_password_params.pass_salt,
            }
            await table.update_item(
                Key={
                    'email': account_data['email'],
                },
                UpdateExpression='SET pass_hash = :hash, pass_salt = :salt',
                ExpressionAttributeValues={
                    ':hash': account_data['pass_hash'],
                    ':salt': account_data['pass_salt'],
                },
            )
            return 1
        except Exception as e:
            log.error('Error in check_and_update_password: %s', e)
            return 0


    async def delete_account_by_email(
        self, db: Any, account_entity: AccountEntity
    ) -> int:
        try:
            account_data = {
                'email': account_entity.email,  # 使用 AccountEntity 中的 email
            }
            table = await db.Table(DDB_TABLE_ACCOUNTS)
            response = await table.delete_item(
                Key={
                    'email': account_data['email'],  # 使用 email 作為主鍵
                }
            )
            return 1 if response else 0

        except Exception as e:
            log.error('Error in delete_account_by_email: %s, %s', account_entity, e)
            return 0
