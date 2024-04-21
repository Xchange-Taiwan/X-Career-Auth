from typing import Any
from pydantic import EmailStr
from ....infra.api.email import Email
from ....config.exception import *
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class EmailService:
    def __init__(self, email: Email):
        self.email = email
        self.__cls_name = self.__class__.__name__
