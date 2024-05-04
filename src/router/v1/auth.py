from typing import List, Dict, Any
from pydantic import EmailStr
from fastapi import (
    APIRouter, status,
    Request, Depends,
    Cookie, Header, Path, Query, Body, Form
)
from ...domain.auth.model import (
    gateway_auth_model as gw,
    auth_model as auth,
)
from ...domain.message.model.email_model import *
from ...domain.auth.service.auth_service import AuthService
from ...infra.api.email import Email
from ...infra.db.sql.auth_repository import AuthRepository
from ..res.response import *
from ...config.exception import *
import logging as log

log.basicConfig(filemode='w', level=log.INFO)

auth_repo = AuthRepository()
email = Email()
_auth_service = AuthService(
    auth_repo=auth_repo,
    email=email,
)

router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
    responses={404: {'description': 'Not found'}},
)


@router.post('/sendcode/email', status_code=status.HTTP_201_CREATED)
async def send_conform_code_by_email(
    payload: ConfirmCodeDTO = Body(...),
):
    res = await _auth_service.\
        send_code_by_email(data=payload, exist=False)
    return res_success(data=res)


@router.post('/signup',
             responses=post_response('signup', auth.AccountVO),
             status_code=201)
async def signup(
    payload: auth.NewAccountDTO = Body(...),
):
    res = await _auth_service.signup(payload)
    return res_success(data=res)


@router.post('/login',
             responses=post_response('login', auth.AccountVO),
             status_code=201)
async def login(
    payload: gw.LoginDTO = Body(...),
):
    res = await _auth_service.login(payload)
    return res_success(data=res)


@router.put('/password/update')
async def update_password(
    payload: gw.UpdatePasswordDTO = Body(...),
):
    await _auth_service.update_password(payload)
    return res_success(msg='update success')

@router.get('/password/reset/email')
async def send_reset_password_confirm_email(
    email: EmailStr = Body(...),
):
    verify_token = await auth_service.send_reset_password_confirm_email(email)
    return res_success(msg='password modified', data={'token': verify_token})
