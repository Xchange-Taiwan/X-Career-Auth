from fastapi import Header, Body
from ...domain.account.model.auth_model import *


def login_check_body(
    body: LoginDTO = Body(...)
) -> (LoginDTO):
    # TODO: verify the password characters
    return body
