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
from ...app.adapter import (
    _oauth_service,
    db_session,
    global_storage,
)
from ..res.response import *
from ...config.exception import *
from ...config.constant import AccountType
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


router = APIRouter(
    prefix='',
    tags=['OAuth'],
    responses={404: {'description': 'Not found'}},
)

@router.post('/signup/oauth/{auth_type}',
             responses=post_response('signup_oauth', auth.AccountOauthVO),
             status_code=status.HTTP_201_CREATED)
async def signup_oauth(
    auth_type: AccountType = Path(...),
    payload: auth.NewOauthAccountDTO = Body(...),
    db: AsyncSession = Depends(db_session),
    s3_client: Any = Depends(global_storage),
):
    if auth_type == AccountType.GOOGLE:
        res = await _oauth_service.signup_oauth_google(
            db, s3_client, payload
        )
    else:
        raise ServerException('Invalid oauth type')
    return post_success(data=res.dict())


@router.post('/login/oauth/{auth_type}',
             responses=post_response('login_oauth', auth.AccountOauthVO),
             status_code=status.HTTP_201_CREATED)
async def login_oauth(
    payload: gw.LoginOauthDTO = Body(...),
    db: AsyncSession = Depends(db_session),
    auth_type: AccountType = Path(...)
):
    if auth_type == AccountType.GOOGLE:
        res = await _oauth_service.login_oauth_google(db, payload)
    else:
        raise ServerException('Invalid oauth type')
    return post_success(data=res.dict())