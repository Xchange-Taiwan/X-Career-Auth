import asyncio
import aioboto3
from ._resource import ResourceHandler

import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class NoSQLResourceHandler(ResourceHandler):
    def __init__(self, session: aioboto3.Session):
        super().__init__()
        self.session = session

    async def initial(self):
        pass

    async def accessing(self, **kwargs):
        return self.session.resource('dynamodb')

    # Regular activation to maintain connections and connection pools
    async def probe(self):
        pass

    async def close(self):
        pass
