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
from src.app.adapter import io_resource_manager
from src.router.v1 import (
    auth, oauth,
)
from src.config import exception

STAGE = os.environ.get('STAGE')
root_path = '/' if not STAGE else f'/{STAGE}'
app = FastAPI(title='X-Career: Auth', root_path=root_path)


@app.on_event('startup')
async def startup_event():
    await io_resource_manager.initial()
    asyncio.create_task(io_resource_manager.keeping_probe())


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
