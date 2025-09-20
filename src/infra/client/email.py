import os
import json
import aioboto3
from pydantic import EmailStr
from botocore.exceptions import ClientError
from ..resource.handler.email_resource import SESResourceHandler
from ...config.exception import *
from ...config.conf import *
from ...config.constant import MailTemplateType
from ...infra.db.sql.orm.mail_template_orm import MailTemplate
from ...domain.auth.service.mail_service import MailService
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class EmailClient:
    # TODO: Change the mail template to database then the X-Career-User can utilize it.
    def __init__(self, ses: SESResourceHandler, mail_service_factory):
        self.ses = ses
        self._mail_service_factory = mail_service_factory
        self.mail_service: MailService | None = None

    async def init(self):
        self.mail_service = await self._mail_service_factory()

    async def load_template(self):
        await self.mail_service.get_mail_template()

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
            html_template = self.mail_service.render_email({
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
        log.info(f'send email: {email}, code: {token}')
        log.info(f'{FRONTEND_RESET_PASSWORD_URL}{token}')
        try:
            html_template = self.mail_service.render_email({
                        "template_type": MailTemplateType.RESET_PASSWORD.value,
                        "title": "Password Reset",
                        "reset_url": f"{FRONTEND_RESET_PASSWORD_URL}{token}",
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
                #     TemplateData=f'{"reset_password_url":"{FRONTEND_RESET_PASSWORD_URL}","token":"{token}"}'
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
        log.info(f'send email: {email}, code: {token}')
        log.info(f'{FRONTEND_SIGNUP_URL}{token}')
        try:
            html_template = self.mail_service.render_email({
                        "template_type": MailTemplateType.SIGNUP.value,
                        "title": f"Welcome to {SITE_TITLE}!",
                        "site_title": SITE_TITLE,
                        "confirm_url": f"{FRONTEND_SIGNUP_URL}{token}", 
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
