from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.infra.db.sql.orm.mail_template_orm import MailTemplate
from src.config.constant import MailTemplateType
from src.config.exception import *
from jinja2 import Template, TemplateError, UndefinedError, StrictUndefined
from jinja2 import Template
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class MailTemplateCache:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self._cached_mail_template = None

    async def get_mail_template(self) -> str:
        if self._cached_mail_template is not None:
            return self._cached_mail_template

        try:
            stmt = select(MailTemplate).where(MailTemplate.id == "auth_template")
            result = await self.db_session.execute(stmt)
            template_obj = result.scalar_one_or_none()

            if not template_obj:
                raise ValueError("Mail template not found.")

            self._cached_mail_template = template_obj.content
            return self._cached_mail_template

        except Exception as e:
            log.error(f"Error getting mail template: {e}")
            raise ServerException(msg="get_mail_template_error")

    def render_email(self, variables: dict) -> str:
        if not self._cached_mail_template:
            raise RuntimeError("Template not loaded. Call get_mail_template() first.")

        try:
            # Use StrictUndefined to raise error if a variable is missing
            template = Template(self._cached_mail_template, undefined=StrictUndefined)
            return template.render(**variables)

        except UndefinedError as e:
            log.error(f"Missing variable in template: {e}")
            raise ServerException(msg="missing_email_variable")

        except TemplateError as e:
            log.error(f"Template rendering error: {e}")
            raise ServerException(msg="template_render_error")

        except Exception as e:
            log.error(f"Unexpected error during email rendering: {e}")
            raise ServerException(msg="unexpected_render_error")
