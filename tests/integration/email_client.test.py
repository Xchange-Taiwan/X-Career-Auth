import asyncio
import aioboto3
"""
先在 cmd 執行:
export PYTHONPATH=/Users/albert/Projects/official/XChange/X-Career-Auth

找到絕對路徑後 即可讀到 src. ... 開頭的檔案
"""
from src.infra.client.email import EmailClient
from src.infra.resource.handler.email_resource import SESResourceHandler



async def test_email_client():
    ses = SESResourceHandler(session=aioboto3.Session())
    email_client = EmailClient(ses)
    await email_client.send_content('testing_visitor@xchange.com.tw', 'test', 'test')


asyncio.run(test_email_client())
