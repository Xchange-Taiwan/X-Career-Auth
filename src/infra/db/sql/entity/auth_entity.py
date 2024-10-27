import time
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    ForeignKey,
    Boolean,
    Enum as SqlEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum
from .....config.constant import AccountType

Base = declarative_base()

'''
for XChange AccountEntity:
    aid
    email
    email2
    pass_hash -> *
    pass_salt -> *
    refresh_token
    user_id
    account_type
    is_active
    region

for OAuth AccountEntity(Google, LinkedIn, etc):
    aid
    email
    email2
    oauth_id -> *
    refresh_token
    user_id
    account_type
    is_active
    region
'''
class AccountEntity(Base):
    __tablename__ = 'accounts'

    aid = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    email2 = Column(String(255))
    pass_hash = Column(String(60))
    pass_salt = Column(String(60))
    oauth_id = Column(String(255))
    refresh_token = Column(String(255))
    user_id = Column(BigInteger, unique=True)
    account_type = Column(SqlEnum(AccountType, name='account_type'))  # 使用 Enum 类型
    is_active = Column(Boolean)
    region = Column(String(50))
    created_at = Column(BigInteger, default=lambda: int(time.time()))
    updated_at = Column(BigInteger, default=lambda: int(time.time()), onupdate=lambda: int(time.time()))

    def dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
