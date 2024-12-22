from sqlalchemy.exc import SQLAlchemyError
from ..infra.resource.handler import *
from ..infra.resource.manager import io_resource_manager
from ..infra.db.sql.orm.auth_repository import AuthRepository
from ..infra.client.email import EmailClient
from ..domain.auth.service.auth_service import AuthService

###############################################
# session/resource/connection/connect pool
###############################################

email_rec = io_resource_manager.get('ses')
sql_rsc = io_resource_manager.get('sql')


################################################################
# connection manager for db, cache, message queue ... etc ?
################################################################

async def db_conn():
    async with sql_rsc.access() as conn:
        try:
            yield conn
        except Exception or SQLAlchemyError as e:
            await conn.rollback()  # Roll back on exception
            raise
        finally:
            await conn.close()  # Ensure session is closed


########################
# client/repo/adapter
########################

email_client = EmailClient(ses=email_rec)
auth_repo = AuthRepository()


##############################
# service/handler/manager
##############################

_auth_service = AuthService(
    auth_repo=auth_repo,
    email_client=email_client,
)
