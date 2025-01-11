import os
import json
import aioboto3
from pydantic import EmailStr
from botocore.exceptions import ClientError
from ..resource.handler.email_resource import SESResourceHandler
from ...config.exception import *
from ...config.conf import *
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class EmailClient:
    def __init__(self, ses: SESResourceHandler):
        self.ses = ses

    async def send_content(self, recipient: EmailStr, subject: str, body: str) -> None:
        log.info(f'send email: {recipient}, subject: {subject}, body: {body}')
        try:
            email_rsc = await self.ses.access()
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
        log.info(f'send email: {email}, code: {confirm_code}')
        try:
            html_template = f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Verification Code</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f4f4f4;
                            color: #333;
                            line-height: 1.6;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 20px auto;
                            padding: 20px;
                            background: #fff;
                            border: 1px solid #ddd;
                            border-radius: 5px;
                            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        }}
                        .verification-code {{
                            font-size: 24px;
                            color: #007bff;
                            font-weight: bold;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Your Verification Code</h2>
                        <p>You are performing an important operation. Please enter the following verification code in the form to complete the process:</p>
                        <p class="verification-code">{confirm_code}</p>
                        <p>Please note that this verification code will expire in 5 minutes.</p>
                    </div>
                </body>
                </html>
            '''
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
        log.info(f'send email: {email}, code: {token}')
        log.info(f'{FRONTEND_RESET_PASSWORD_URL}{token}')
        try:
            html_template = f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Password Reset</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333; line-height: 1.6; }}
                        .container {{ max-width: 600px; margin: 20px auto; padding: 20px; background: #fff; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }}
                        .button {{ display: inline-block; padding: 10px 20px; margin-top: 20px; background-color: #007bff; color: #fff; text-decoration: none; border-radius: 5px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Password Reset Request</h2>
                        <p>You recently requested to reset your password for your account. Click the button below to reset it.</p>
                        <a href="{FRONTEND_RESET_PASSWORD_URL}{token}" class="button">Reset Your Password</a>
                        <p>If you did not request a password reset, please ignore this email or contact support if you have questions.</p>
                        <p>Thank you!</p>
                    </div>
                </body>
                </html>
            '''
            
            email_rsc = await self.ses.access()
            async with email_rsc as email_client:
                response = await email_client.send_email(
                    Source=EMAIL_SENDER,
                    Destination={
                        'ToAddresses': [email],
                    },
                    Message={
                        'Subject': {'Data': f'{SITE_TITLE} - Reset Password'},
                        'Body': {
                            'Text': {'Data': f'Reset Your Password'},
                            'Html': {'Data': html_template},
                        },
                    }
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
        log.info(f'send email: {email}, code: {token}')
        log.info(f'{FRONTEND_SIGNUP_URL}{token}')
        try:
            html_template = f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Welcome to {SITE_TITLE}!</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333; line-height: 1.6; }}
                        .container {{ max-width: 600px; margin: 20px auto; padding: 20px; background: #fff; border: 1px solid #ddd; border-radius: 5px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); }}
                        .button {{ display: inline-block; padding: 10px 20px; margin-top: 20px; background-color: #28a745; color: #fff; text-decoration: none; border-radius: 5px; }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>Welcome to {SITE_TITLE}!</h2>
                        <p>Thank you for registering with us! Please confirm your email to complete your registration.</p>
                        <a href="{FRONTEND_SIGNUP_URL}{token}" class="button">Confirm Your Email</a>
                        <p>If you did not register for an account, please ignore this email or contact support if you have questions.</p>
                        <p>Welcome aboard!</p>
                    </div>
                </body>
                </html>
            '''
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
