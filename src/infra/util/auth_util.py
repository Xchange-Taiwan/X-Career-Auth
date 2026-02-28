import os
import json
import random
import time
from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Tuple
from snowflake import SnowflakeGenerator
import hashlib
from src.config.constant import AccountType
from ...config.exception import *
import logging

log = logging.getLogger(__name__)


'''SnowflakeGenerator group
'''
instances = 100
snowflake_generator_dict = {}
for i in range(instances):
    snowflake_generator_dict[i] = SnowflakeGenerator(i)


def gen_snowflake_id():
    millisecs = datetime.now().timestamp()
    i = int(millisecs * 100000) % instances
    gen = snowflake_generator_dict[i]
    num = next(gen)
    return int(num / 1000)


letters = '0123456789abcdefghijklmnopqrstuvwxyz'


def gen_random_string(length):
    # choose from all lowercase letter
    return ''.join(random.choice(letters) for i in range(length))


def gen_pass_salt():
    return gen_random_string(12)


def gen_password_hash(pw: str, pass_salt: str):
    password_data = str(pw + pass_salt).encode('utf-8')
    return hashlib.sha224(password_data).hexdigest()


# def gen_account_data(data: dict, account_type: AccountType) -> AccountEntity:
#     aid = gen_snowflake_id()
#     user_id = gen_snowflake_id()
#     ft_auth = XCAuth(
#         email=data['email'],
#         aid=aid,
#         user_id=user_id,
#     )

#     if account_type == AccountType.XC:
#         pass_salt = gen_pass_salt()
#         ft_auth.pass_salt = pass_salt
#         ft_auth.pass_hash = gen_password_hash(
#             pw=data['pass'], pass_salt=pass_salt)
#     else:
#         ft_auth.sso_id = data['sso_id']

#     account = AccountEntity(
#         aid=aid,
#         email=data['email'],
#         region=data['region'],
#         user_id=user_id,
#         account_type=account_type
#     )

#     return (ft_auth, account)


def match_password(pass_hash, pw, pass_salt):
    password_data = str(pw + pass_salt).encode('utf-8')
    return pass_hash == hashlib.sha224(password_data).hexdigest()


def filter_by_keys(data, ary):
    result = {}
    for field in ary:
        result[field] = data[field]

    return result
