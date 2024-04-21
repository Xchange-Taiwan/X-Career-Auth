from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

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

    aid = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    email2 = Column(String(100), nullable=True)
    pass_hash = Column(String(100), nullable=True)
    pass_salt = Column(String(100), nullable=True)
    oauth_id = Column(String(100), nullable=True)
    # TODO: save refresh_token in Redis?
    refresh_token = Column(String(1000), nullable=True)
    user_id = Column(Integer, unique=True)
    account_type = Column(String(20))
    is_active = Column(Boolean, default=True)
    region = Column(String(20))
