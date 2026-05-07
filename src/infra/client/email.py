import os
import json
import asyncio
import aioboto3
from pydantic import EmailStr
from botocore.exceptions import ClientError
from ..resource.handler.email_resource import SESResourceHandler
from ...config.exception import *
from ...config.conf import (
    EMAIL_SENDER,
    SITE_TITLE,
    FRONTEND_HOSTNAME,
    FRONTEND_URL_PATH_RESET_PASSWORD,
    FRONTEND_TOKEN,
    FRONTEND_URL_PATH_EMAIL_VERIFIED,
)
from ...config.constant import MailTemplateType
from ...infra.db.sql.orm.mail_template_orm import MailTemplate
from ...infra.cache.mail_template_cache import MailTemplateCache
import logging

log = logging.getLogger(__name__)


class EmailClient:
    # TODO: Change the mail template to database then the X-Career-User can utilize it.
    def __init__(self, ses: SESResourceHandler, mail_template_cache_factory):
        self.ses = ses
        self._mail_template_cache_factory = mail_template_cache_factory
        self.template_cache: MailTemplateCache | None = None
        # Single-flight lock: under cold-start, requests can pile up before
        # the template is loaded; we want exactly one factory call, not N.
        self._init_lock = asyncio.Lock()

    async def init(self):
        # Idempotent and optional. load_template() self-heals on every call,
        # so a request that lands before warmup finishes still works.
        await self._ensure_loaded()

    async def _ensure_loaded(self) -> None:
        # Fast path: cache already populated.
        if self.template_cache is not None and self.template_cache._cached_mail_template:
            return
        async with self._init_lock:
            # Re-check inside the lock — another caller may have loaded it
            # while we were waiting.
            if self.template_cache is not None and self.template_cache._cached_mail_template:
                return
            # Build a fresh cache (factory primes it inside its own session
            # scope, so what we get back is already usable). Only publish
            # after success — render_email() never sees a half-init cache.
            self.template_cache = await self._mail_template_cache_factory()

    async def load_template(self):
        await self._ensure_loaded()

    async def send_content(self, recipient: EmailStr, subject: str, body: str) -> None:
        log.info(f'send email: {recipient}, subject: {subject}, body: {body}')
        try:
            email_rsc = await self.ses.access()
            print(email_rsc)
            async with email_rsc as email_client:
                response = await email_client.send_email(
                    Source=EMAIL_SENDER,
                    Destination={
                        'ToAddresses': [recipient],
                    },
                    Message={
                        'Subject': {'Data': f'{subject}'},
                        'Body': {
                            'Text': {'Data': f'{body}'},
                        },
                    }
                )

                log.info(f'Email sent. Message ID: {response.get("MessageId", None)}')

        except ClientError as e:
            log.error(f'SES ClientError sending email: {e}')
            raise ServerException(msg='email_send_content_error')

        except Exception as e:
            log.error(f'Error sending email: {e}')
            raise ServerException(msg='email_send_content_error')

    async def send_conform_code(self, email: EmailStr, confirm_code: str) -> None:
        await self.load_template()
        log.info(f'send email: {email}, code: {confirm_code}')
        try:
            html_template = self.template_cache.render_email({
                        "template_type": MailTemplateType.VERIFICATION_CODE.value,
                        "title": "Verification Code",
                        "confirm_code": confirm_code,
                    })
            email_rsc = await self.ses.access()
            async with email_rsc as email_client:
                response = await email_client.send_email(
                    Source=EMAIL_SENDER,
                    Destination={
                        'ToAddresses': [email],
                    },
                    Message={
                        'Subject': {'Data': f'{SITE_TITLE} - Verification Code: {confirm_code}'},
                        'Body': {
                            'Text': {'Data': f'Your Code is: {confirm_code}'},
                            'Html': {'Data': html_template},
                        },
                    }
                )
                # response = self.ses.send_templated_email(
                #     Source=EMAIL_SENDER,
                #     Destination={
                #         'ToAddresses': [email],
                #     },
                #     Template=EMAIL_VERIFY_CODE_TEMPLATE,
                #     TemplateData=f'{"verification_code":"{confirm_code}"}'
                # )
                log.info(f'Email sent. Message ID: {response.get("MessageId", None)}')

        except ClientError as e:
            log.error(f'Error sending email: {e}')
            raise ServerException(msg='email_send_conform_code_error')

        except Exception as e:
            log.error(f'Error sending email: {e}')
            raise ServerException(msg='email_send_conform_code_error')

    async def send_reset_password_comfirm_email(self, email: EmailStr, token: str) -> None:
        await self.load_template()
        reset_url = f"{FRONTEND_HOSTNAME.rstrip('/')}{FRONTEND_URL_PATH_RESET_PASSWORD}?{FRONTEND_TOKEN}={token}"
        log.info(f'send email: {email}, code: {token}')
        log.info(reset_url)
        try:
            html_template = self.template_cache.render_email({
                        "template_type": MailTemplateType.RESET_PASSWORD.value,
                        "title": "Password Reset",
                        "reset_url": reset_url,
                    })
            email_rsc = await self.ses.access()
            async with email_rsc as email_client:
                response = await email_client.send_email(
                    Source=EMAIL_SENDER,
                    Destination={
                        "ToAddresses": [email],
                    },
                    Message={
                        "Subject": {"Data": f"{SITE_TITLE} - Reset Password"},
                        "Body": {
                            "Text": {"Data": f"Reset Your Password"},
                            "Html": {"Data": html_template},
                        },
                    },
                )
                # response = self.ses.send_templated_email(
                #     Source=EMAIL_SENDER,
                #     Destination={
                #         'ToAddresses': [email],
                #     },
                #     Template=EMAIL_RESET_PASSWORD_TEMPLATE,
                #     TemplateData=f'{"reset_password_url":"{FRONTEND_HOSTNAME}{FRONTEND_URL_PATH_RESET_PASSWORD}?{FRONTEND_TOKEN}={token}"}'
                # )
                log.info(f'Email sent. Message ID: {response.get("MessageId", None)}')

        except ClientError as e:
            log.error(f'Error sending email: {e}') 
            raise ServerException(msg='email_send_reset_password_error')

        except Exception as e:
            log.error(f'Error sending email: {e}')
            raise ServerException(msg='email_send_reset_password_error')

    async def send_signup_confirm_email(self, email: EmailStr, token: str) -> None:
        await self.load_template()
        confirm_url = f"{FRONTEND_HOSTNAME.rstrip('/')}{FRONTEND_URL_PATH_EMAIL_VERIFIED}?{FRONTEND_TOKEN}={token}"
        log.info(f'send email: {email}, code: {token}')
        log.info(confirm_url)
        try:
            html_template = self.template_cache.render_email({
                        "template_type": MailTemplateType.SIGNUP.value,
                        "title": f"Welcome to {SITE_TITLE}!",
                        "site_title": SITE_TITLE,
                        "confirm_url": confirm_url,
                    })
            email_rsc = await self.ses.access()
            async with email_rsc as email_client:
                response = await email_client.send_email(
                    Source=EMAIL_SENDER,
                    Destination={
                        'ToAddresses': [email],
                    },
                    Message={
                        'Subject': {'Data': f'{SITE_TITLE} - Confirm Your Registration'},
                        'Body': {
                            'Text': {'Data': 'Confirm Your Email'},
                            'Html': {'Data': html_template},
                        },
                    }
                )
                log.info(f'Email sent. Message ID: {response.get("MessageId", None)}')

        except ClientError as e:
            log.error(f'Error sending email: {e}') 
            raise ServerException(msg='email_send_registration_link_error')

        except Exception as e:
            log.error(f'Error sending email: {e}')
            raise ServerException(msg='email_send_registration_link_error')
