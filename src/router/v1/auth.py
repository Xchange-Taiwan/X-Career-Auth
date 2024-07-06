from typing import List, Dict, Any
from pydantic import EmailStr
from fastapi import (
    APIRouter, status,
    Request, Depends,
    Cookie, Header, Path, Query, Body, Form
)
from sqlalchemy.ext.asyncio import AsyncSession
from ...domain.auth.model import (
    gateway_auth_model as gw,
    auth_model as auth,
)
from ...domain.message.model.email_model import *
from ...domain.auth.service.auth_service import AuthService
from ...infra.api.email import Email
from ...infra.db.sql.orm.auth_repository import AuthRepository
from ..res.response import *
from ...config.databse import get_db
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
    prefix='',
    tags=['Auth'],
    responses={404: {'description': 'Not found'}},
)


@router.post('/sendcode/email', status_code=status.HTTP_201_CREATED)
async def send_conform_code_by_email(
    payload: ConfirmCodeDTO = Body(...),
    db: AsyncSession = Depends(get_db),
):
    res = await _auth_service.\
        send_code_by_email(db=db, data=payload)
    return res_success(data=res)


@router.post('/signup',
             responses=post_response('signup', auth.AccountVO),
             status_code=201)
async def signup(
    payload: auth.NewAccountDTO = Body(...),
    db: AsyncSession = Depends(get_db),
):
    res = await _auth_service.signup(db, payload)
    return res_success(data=res.dict())


@router.post('/login',
             responses=post_response('login', auth.AccountVO),
             status_code=201)
async def login(
    payload: gw.LoginDTO = Body(...),
    db: AsyncSession = Depends(get_db),
):
    res = await _auth_service.login(db, payload)
    return res_success(data=res.dict())


@router.put('/password/update')
async def update_password(
    payload: gw.UpdatePasswordDTO = Body(...),
    db: AsyncSession = Depends(get_db),
):
    await _auth_service.update_password(db, payload)
    return res_success(msg='update success')

@router.get('/password/reset/email')
async def send_reset_password_confirm_email(
    email: EmailStr = Query(...),
    db: AsyncSession = Depends(get_db),
):
    verify_token = await _auth_service.send_reset_password_confirm_email(db, email)
    return res_success(msg='email sent', data={'token': verify_token})
