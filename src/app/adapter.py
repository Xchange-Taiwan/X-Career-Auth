import aioboto3
from sqlalchemy.exc import SQLAlchemyError
from ..infra.resource.handler import *
from ..infra.resource.manager import IOResourceManager
from ..infra.db.sql.repo.auth_repository import AuthRepository
from ..infra.db.nosql.repo.dynamodb_auth_repository import DynamoDBAuthRepository
from ..infra.client.email import EmailClient
from ..infra.client.async_service_api_adapter import AsyncServiceApiAdapter
from ..infra.cache.mail_template_cache import MailTemplateCache
from ..domain.auth.service.auth_service import AuthService
from ..domain.auth.service.oauth_service import OauthService

###############################################
# session/resource/connection/connect pool
###############################################

session = aioboto3.Session()
io_resource_manager = IOResourceManager(resources={
    'sql': SQLResourceHandler(),
    'dynamodb': NoSQLResourceHandler(session),
    'ses': SESResourceHandler(session),
})

sql_rsc = io_resource_manager.get('sql')
dynamodb_rsc = io_resource_manager.get('dynamodb')
email_rec = io_resource_manager.get('ses')

################################################################
# connection manager for db, cache, message queue ... etc ?
################################################################

# dynamodb session
async def ddb_session():
    dynamodb_resource = await dynamodb_rsc.access()
    async with dynamodb_resource as ddb_resource:
        try:
            yield ddb_resource
        except Exception as e:
            raise


# session with "manual" commit/rollback
async def db_session():
    session_local = await sql_rsc.access()
    async with session_local() as session:
        try:
            yield session
        except Exception or SQLAlchemyError as e:
            raise
        finally:
            await session.close()  # Ensure session is closed


# session with "auto" commit/rollback
async def db_auto_session():
    session_local = await sql_rsc.access()
    async with session_local() as session:
        try:
            yield session
            await session.commit()  # Commit on success
        except Exception or SQLAlchemyError as e:
            await session.rollback()  # Roll back on exception
            raise
        finally:
            await session.close()  # Ensure session is closed


########################
# client/repo/adapter
########################
async def init_mail_template_cache() -> MailTemplateCache:
    async for session in db_session():
        return MailTemplateCache(db_session=session)


email_client = EmailClient(ses=email_rec, mail_template_cache_factory=init_mail_template_cache)
http_request = AsyncServiceApiAdapter()
auth_repo = AuthRepository()
ddb_auth_repo = DynamoDBAuthRepository()


##############################
# service/handler/manager
##############################

_auth_service = AuthService(
    auth_repo=ddb_auth_repo,
    email_client=email_client,
    http_request=http_request,
)
_oauth_service = OauthService(
    auth_repo=ddb_auth_repo,
    email_client=email_client,
    http_request=http_request,
)
