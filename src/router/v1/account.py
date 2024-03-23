from typing import List, Dict, Any
from pydantic import EmailStr
from fastapi import (
    APIRouter,
    Request, Depends,
    Cookie, Header, Path, Query, Body, Form
)
from ...domain.account.model.auth_model import *
from ..req.auth_validation import *
from ..res.response import *
from ...config.exception import *
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


router = APIRouter(
    prefix='/accounts',
    tags=['Account'],
    responses={404: {'description': 'Not found'}},
)


@router.post('/signup', status_code=201)
async def signup(
    body: SignupDTO = Body(...),
):
    # TODO: implement
    return res_success(data=None, msg='email_sent')


@router.post('/signup/confirm',
             responses=post_response('confirm_signup', SignupResponseVO),
             status_code=201)
async def confirm_signup(
    body: SignupConfirmDTO = Body(...),
):
    # TODO: implement
    return res_success(data=None)


@router.post('/login',
             responses=post_response('login', LoginResponseVO),
             status_code=201)
async def login(
    body: LoginDTO = Depends(login_check_body),
):
    # TODO: implement
    return res_success(data=None)


@router.post('/logout', status_code=201)
async def logout(
    user_id: int = Body(..., embed=True),
):
    # TODO: implement
    return res_success(data=None, msg='msg')


@router.put('/password/{user_id}/update')
async def update_password(
    user_id: int,
    update_password_dto: UpdatePasswordDTO = Body(...),
):
    # TODO: implement
    return res_success(msg='update success')


@router.get('/password/reset/email')
async def send_reset_password_comfirm_email(
    email: EmailStr,
):
    # TODO: implement
    return res_success(msg='msg')


@router.put('/password/reset')
async def reset_password(
    reset_passwrod_dto: ResetPasswordDTO = Body(...),
    verify_token: str = Query(...),
):
    # TODO: implement
    return res_success(msg='reset success')
