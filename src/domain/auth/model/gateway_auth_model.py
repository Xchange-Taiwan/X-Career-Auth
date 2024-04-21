import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, EmailStr, validator
from ....config.exception import ClientException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class SignupDTO(BaseModel):
    email: EmailStr
    password: str
    password2: str
    
    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password1' in values and v != values['password1']:
            raise ClientException(msg='passwords do not match')
        return v

    class Config:
        schema_extra = {
            'example': {
                'email': 'user@example.com',
                'password': 'secret',
                'password2': 'secret',
            },
        }


class SignupConfirmDTO(BaseModel):
    region: Optional[str]
    email: EmailStr
    code: str

    class Config:
        schema_extra = {
            'example': {
                'region': 'us-west-2',
                'email': 'user@example.com',
                'code': '106E7B',
            },
        }


class LoginDTO(BaseModel):
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            'example': {
                'email': 'user@example.com',
                'password': 'secret',
            },
        }


class SSOLoginDTO(BaseModel):
    code: str
    state: str
    sso_type: Optional[str]

    def to_dict(self):
        d = super().dict()
        d.pop('sso_type', None)
        return d


class ResetPasswordDTO(BaseModel):
    register_email: EmailStr
    password: str
    password2: str
    
    @validator('password2')
    def passwords_match(cls, v, values, **kwargs):
        if 'password1' in values and v != values['password1']:
            raise ClientException(msg='passwords do not match')
        return v
    
    class Config:
        schema_extra = {
        'example': {
            'register_email': 'user@example.com',
            'password': 'secret',
            'password2': 'secret',
        },
    }


class UpdatePasswordDTO(ResetPasswordDTO):
    origin_password: str

    class Config:
        schema_extra = {
        'example': {
            'register_email': 'user@example.com',
            'password': 'secret2',
            'password2': 'secret2',
            'origin_password': 'secret',
        },
    }


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
