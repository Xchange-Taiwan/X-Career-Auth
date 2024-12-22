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
from ...app.adapter import _auth_service, db_conn
from ..res.response import *
from ...config.exception import *
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


router = APIRouter(
    prefix='',
    tags=['Auth'],
    responses={404: {'description': 'Not found'}},
)


@router.post('/sendcode/email', status_code=status.HTTP_201_CREATED)
async def send_conform_code_by_email(
    payload: ConfirmCodeDTO = Body(...),
    db_conn: AsyncSession = Depends(db_conn),
):
    res = await _auth_service.send_code_by_email(conn=db_conn, data=payload)
    return post_success(data=res)


@router.post('/signup/email', status_code=status.HTTP_201_CREATED)
async def send_signup_confirm_email(
    payload: SendEmailDTO = Body(...),
    db_conn: AsyncSession = Depends(db_conn),
):
    res = await _auth_service.send_link_by_email(conn=db_conn, data=payload)
    return post_success(data=res)


@router.post('/signup',
             responses=post_response('signup', auth.AccountVO),
             status_code=status.HTTP_201_CREATED)
async def signup(
    payload: auth.NewAccountDTO = Body(...),
    db_conn: AsyncSession = Depends(db_conn),
):
    res = await _auth_service.signup(db_conn, payload)
    return post_success(data=res.dict())


@router.post('/login',
             responses=post_response('login', auth.AccountVO),
             status_code=status.HTTP_201_CREATED)
async def login(
    payload: gw.LoginDTO = Body(...),
    db_conn: AsyncSession = Depends(db_conn),
):
    res = await _auth_service.login(db_conn, payload)
    return post_success(data=res.dict())


@router.put('/password/update')
async def update_password(
    payload: gw.UpdatePasswordDTO = Body(...),
    db_conn: AsyncSession = Depends(db_conn),
):
    await _auth_service.update_password(db_conn, payload)
    return res_success(msg='update success')


@router.get('/password/reset/email')
async def send_reset_password_confirm_email(
    email: EmailStr = Query(...),
    db_conn: AsyncSession = Depends(db_conn),
):
    verify_token = await _auth_service.send_reset_password_confirm_email(db_conn, email)
    return res_success(msg='email sent', data={'token': verify_token})
