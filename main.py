import os
from mangum import Mangum
from fastapi import FastAPI, Request, \
    Header, Path, Query, Body, Form, \
    File, UploadFile, status, \
    HTTPException, \
    Depends, \
    APIRouter
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.router.v1 import (
    auth,
)
from src.config import exception

STAGE = os.environ.get('STAGE')
root_path = '/' if not STAGE else f'/{STAGE}'
app = FastAPI(title='X-Career: Auth', root_path=root_path)


# 數據庫連接配置
DB_HOST = os.environ['DB_HOST']
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']

import asyncpg
async def execute_sql_file(filename):
    # 連接到 PostgreSQL 數據庫
    conn = await asyncpg.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    
    # 讀取 SQL 檔案
    with open(filename, 'r') as file:
        sql = file.read()

    # 執行 SQL
    await conn.execute(sql)

    # 關閉連接
    await conn.close()

@app.on_event("startup")
async def startup_event():
    # 在 Lambda 啟動時執行 SQL 檔案
    await execute_sql_file('src/infra/db/sql/init/auth_init.sql')



app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

router_v1 = APIRouter(prefix='/auth-service/api/v1')
router_v1.include_router(auth.router)

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
