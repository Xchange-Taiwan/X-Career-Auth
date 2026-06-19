import time
from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

"""
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
"""

class Account(Base):
    __tablename__ = "accounts"

    aid = Column(BigInteger, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    email2 = Column(String(255))
    pass_hash = Column(String(60))
    pass_salt = Column(String(60))
    oauth_id = Column(String(255))  # 避免對空字串或 NULL 建立索引
    refresh_token = Column(String(255))
    user_id = Column(BigInteger, unique=True)
    account_type = Column(String(50), nullable=False)
    is_active = Column(Boolean)
    region = Column(String(50))
    created_at = Column(BigInteger, default=lambda: int(time.time()))
    updated_at = Column(
        BigInteger, default=lambda: int(time.time()), onupdate=lambda: int(time.time())
    )
    def dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
