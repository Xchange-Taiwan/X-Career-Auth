from dotenv import load_dotenv
load_dotenv()

from src.config.logging_config import init_logging
log = init_logging()

import os, asyncio
from mangum import Mangum
from fastapi import FastAPI, Request, \
    Header, Path, Query, Body, Form, \
    File, UploadFile, status, \
    HTTPException, \
    Depends, \
    APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.app.adapter import io_resource_manager, email_client
from src.router.v1 import (
    auth, oauth, calendar,
)
from src.config import exception

STAGE = os.environ.get('STAGE')
root_path = '/' if not STAGE else f'/{STAGE}'
# API Gateway stage 在 URL 裡是 /{stage}/...；Swagger 內建若用絕對路徑 /openapi.json
# 瀏覽器會打到根網域而非 /{stage}/openapi.json（常為 403），故在 Lambda 須掛在 stage 底下。
if STAGE:
    app = FastAPI(
        title='X-Career: Auth',
        root_path=root_path,
        docs_url=f'/{STAGE}/docs',
        openapi_url=f'/{STAGE}/openapi.json',
    )
else:
    app = FastAPI(title='X-Career: Auth', root_path=root_path)


@app.on_event('startup')
async def startup_event():
    # Schedule resource setup in the background so the Lambda becomes ready to
    # accept traffic immediately. The DB pool is then initialized lazily by the
    # first request that calls SQLResourceHandler.accessing(), which already
    # builds the pool under a lock when self.engine is None. Previously this
    # blocked startup for several seconds on a cold start and BFF's httpx call
    # would time out before Auth was ready, surfacing as a 500.
    asyncio.create_task(_warmup_resources())
    asyncio.create_task(io_resource_manager.keeping_probe())


async def _warmup_resources():
    try:
        await io_resource_manager.initial()
        await email_client.init()
    except Exception as e:
        log.error('Resource warmup failed (will retry lazily): %s', e)


@app.on_event('shutdown')
async def shutdown_event():
    await io_resource_manager.close()


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

router_v1 = APIRouter(prefix='/auth-service/api/v1')
router_v1.include_router(auth.router)
router_v1.include_router(oauth.router)
router_v1.include_router(calendar.router)
app.include_router(router_v1)

exception.include_app(app)


@app.get('/auth-service/{term}')
async def info(term: str):
    if term != 'yolo':
        raise HTTPException(
            status_code=418, detail='Oops! Wrong phrase. Guess again?')
    return JSONResponse(content={'mention': 'You only live once.'})

# Mangum Handler, this is so important
handler = Mangum(app)
