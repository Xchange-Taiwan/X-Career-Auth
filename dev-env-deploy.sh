#!/bin/bash

# TODO: EMAIL_SENDER 部署後需修改成 xchange 測試帳號

aws lambda update-function-configuration --function-name x-career-auth-dev-app --environment --profile xc "Variables={
SITE_TITLE=X-Career,
PROBE_CYCLE_SECS=3,
BATCH_LIMIT=20,
DB_URL=postgresql+asyncpg://postgres:postgres@x-career-db-test.cu7knbzuvltn.ap-northeast-1.rds.amazonaws.com:5432/postgres,
POOL_PRE_PING=1,
POOL_RECYCLE=300,
POOL_SIZE=10,
MAX_OVERFLOW=20,
AUTO_COMMIT=0,
AUTO_FLUSH=0,
EMAIL_SENDER=support@xchange.com,
EMAIL_VERIFY_CODE_TEMPLATE=None,
EMAIL_RESET_PASSWORD_TEMPLATE=None,
FRONTEND_SIGNUP_URL=http://localhost:8002/auth/signup?token=,
FRONTEND_RESET_PASSWORD_URL=http://localhost:8002/auth/reset_password?token=,
SES_CONNECT_TIMEOUT=10,
SES_READ_TIMEOUT=10,
SES_MAX_ATTEMPTS=3,
GOOGLE_CLIENT_ID=None,
GOOGLE_CLIENT_SECRET=None,
GOOGLE_REDIRECT_URI=None,
LINKEDIN_APP_ID=None,
LINKEDIN_APP_SECRET=None,
LINKEDIN_REDIRECT_URI=None,
DB_HOST=x-career-db-test.cu7knbzuvltn.ap-northeast-1.rds.amazonaws.com,
DB_NAME=postgres,
DB_USER=postgres,
DB_PASSWORD=postgres,
}"
