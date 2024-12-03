import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from ._resource import ResourceHandler
from ....config.conf import (
    DB_URL,
    POOL_PRE_PING,
    POOL_RECYCLE,
    POOL_SIZE,
    MAX_OVERFLOW,
    AUTO_COMMIT,
    AUTO_FLUSH,
    PSQL_TENANT_NAMESPACES,
)
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


connect_args = {
    'server_settings': {
        'search_path': PSQL_TENANT_NAMESPACES,
    }
}


class SQLResourceHandler(ResourceHandler):

    def __init__(self, ):
        super().__init__()
        self.max_timeout = POOL_RECYCLE

        self.lock = asyncio.Lock()
        self.engine = None
        self.session = None

    async def initial(self):
        try:
            async with self.lock:
                if self.engine is not None:
                    await self.engine.dispose()

                self.engine = create_async_engine(
                    DB_URL,
                    connect_args=connect_args,
                    pool_pre_ping=POOL_PRE_PING,
                    pool_size=POOL_SIZE,
                    max_overflow=MAX_OVERFLOW)
                log.info('DB[SQL] Connection pool established.')

                if self.session is not None:
                    await self.session().close()

                self.session = sessionmaker(
                    autocommit=AUTO_COMMIT,
                    autoflush=AUTO_FLUSH,
                    bind=self.engine,
                    class_=AsyncSession)

                async with self.session() as conn:
                    await conn.execute(text('SELECT 1'))
                    log.info('DB[SQL] Session established & available.')

        except Exception as e:
            log.error(e.__str__())
            async with self.lock:
                if self.engine is not None:
                    await self.engine.dispose()

                self.engine = create_async_engine(
                    DB_URL,
                    connect_args=connect_args,
                    pool_pre_ping=POOL_PRE_PING,
                    pool_size=POOL_SIZE,
                    max_overflow=MAX_OVERFLOW)
                log.info('DB[SQL] Connection pool established.')

                if self.session is not None:
                    await self.session().close()

                self.session = sessionmaker(
                    autocommit=AUTO_COMMIT,
                    autoflush=AUTO_FLUSH,
                    bind=self.engine,
                    class_=AsyncSession)

                async with self.session() as conn:
                    await conn.execute(text('SELECT 1'))
                    log.info('DB[SQL] Session established & available.')

    async def accessing(self, **kwargs):
        if self.engine is None or self.session is None:
            await self.initial()

        # 在同一次 request 中，使用同一個 session
        return self.session()

    # Regular activation to maintain connections and connection pools

    async def probe(self):
        try:
            async with self.session() as conn:
                await conn.execute(text('SELECT 1'))
                log.info('DB[SQL] Session is available. (probe)')

        except Exception as e:
            log.error(f'DB[SQL] Client Error: {e.__str__()}')
            await self.initial()

    async def close(self):
        try:
            async with self.lock:
                if self.session is not None:
                    await self.session().close()
                if self.engine is not None:
                    await self.engine.dispose()

        except Exception as e:
            log.error(f'DB[SQL] Client Error: {e.__str__()}')
            await self.initial()
