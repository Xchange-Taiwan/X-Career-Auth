from sqlalchemy.exc import SQLAlchemyError
from ..infra.resource.handler import *
from ..infra.resource.manager import io_resource_manager
from ..infra.db.sql.orm.auth_repository import AuthRepository
from ..infra.client.email import EmailClient
from ..infra.client.async_service_api_adapter import AsyncServiceApiAdapter
from ..domain.auth.service.auth_service import AuthService

###############################################
# session/resource/connection/connect pool
###############################################

email_rec = io_resource_manager.get('ses')
sql_rsc = io_resource_manager.get('sql')


################################################################
# connection manager for db, cache, message queue ... etc ?
################################################################

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

email_client = EmailClient(ses=email_rec)
http_request = AsyncServiceApiAdapter()
auth_repo = AuthRepository()


##############################
# service/handler/manager
##############################

_auth_service = AuthService(
    auth_repo=auth_repo,
    email_client=email_client,
    http_request=http_request,
)
