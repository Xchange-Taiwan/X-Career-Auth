import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from ....config.exception import ClientException
import logging

log = logging.getLogger(__name__)


class SignupDTO(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ClientException(msg='passwords do not match')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'email': 'user@example.com',
                'password': 'secret',
                'confirm_password': 'secret',
            }
        }
    )


class SignupConfirmDTO(BaseModel):
    region: Optional[str] = None
    email: EmailStr
    code: str

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'region': 'us-west-2',
                'email': 'user@example.com',
                'code': '106E7B',
            }
        }
    )


class LoginOauthDTO(BaseModel):
    email: EmailStr
    oauth_id: str
    # access_token: str

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'email': 'user@example.com',
                'oauth_id': 'oauth_id',
                # 'access_token': 'access_token'
            }
        }
    )

class LoginDTO(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'email': 'user@example.com',
                'password': 'secret',
            }
        }
    )


class SSOLoginDTO(BaseModel):
    code: str
    state: str
    sso_type: Optional[str] = None

    def to_dict(self):
        d = super().model_dump()
        d.pop('sso_type', None)
        return d


class ResetPasswordDTO(BaseModel):
    register_email: EmailStr
    password: str
    confirm_password: str

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ClientException(msg='passwords do not match')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            'example': {
                'register_email': 'user@example.com',
                'password': 'secret',
                'confirm_password': 'secret',
            }
        }
    )

class UpdatePasswordDTO(ResetPasswordDTO):
    origin_password: Optional[str] = None

    model_config=ConfigDict(
        json_schema_extra={
            'example': {
                'register_email': 'user@example.com',
                'password': 'secret2',
                'confirm_password': 'secret2',
                'origin_password': 'secret',
            }
        }
    )

class BaseAuthDTO(BaseModel):
    # registration region
    region: str
    user_id: int


class AuthVO(BaseAuthDTO):
    email: EmailStr
    token: str
    online: Optional[bool] = False
    created_at: int


class SignupResponseVO(BaseModel):
    auth: AuthVO


class LoginResponseVO(SignupResponseVO):
    # TODO: define user VO
    user: Dict
