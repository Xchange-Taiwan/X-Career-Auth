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

    class Config:
        schema_extra = {
            'example': {
                'email': 'user@example.com',
                'password': 'secret',
                'password2': 'secret',
            },
        }


class SignupConfirmDTO(BaseModel):
    email: EmailStr
    confirm_code: str

    class Config:
        schema_extra = {
            'example': {
                'email': 'user@example.com',
                'confirm_code': '106E7B',
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

    def fine_dict(self):
        d = super().dict()
        d.pop('sso_type', None)
        return d


class ResetPasswordDTO(BaseModel):
    register_email: EmailStr
    password: str
    password2: str


class UpdatePasswordDTO(ResetPasswordDTO):
    origin_password: str


class AccountVO(BaseModel):
    user_id: int
    email: EmailStr
    token: str
    online: Optional[bool] = False
    created_at: int


class SignupResponseVO(BaseModel):
    account: AccountVO


class LoginResponseVO(SignupResponseVO):
    professional: Dict
