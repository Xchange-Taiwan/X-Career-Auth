#!/bin/bash

# 取得 AWS 帳號別名，默認為 "default"
AWS_PROFILE="default"

# 解析命令行选项
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -a|--account) AWS_PROFILE="$2"; REGION=$(aws configure get region --profile "$2"); shift ;; # 指定 AWS 帳號；重新取得該帳號 region
        *) echo "未知选项: $1"; exit 1 ;;  # 处理未知选项
    esac
    shift
done


# TODO: EMAIL_SENDER 部署後需修改成 xchange 測試帳號

aws lambda update-function-configuration --function-name x-career-auth-dev-app --environment --profile $AWS_PROFILE "Variables={
SITE_TITLE=X-Career,
PROBE_CYCLE_SECS=3,
DYNAMODB_TABLE_ACCOUNTS=dev_x_career_auth_accounts,
BATCH_LIMIT=20,
DB_URL=postgresql+asyncpg://postgres:postgres@x-career-db-test.cu7knbzuvltn.ap-northeast-1.rds.amazonaws.com:5432/postgres,
POOL_PRE_PING=1,
POOL_RECYCLE=300,
POOL_SIZE=10,
MAX_OVERFLOW=20,
AUTO_COMMIT=0,
AUTO_FLUSH=0,
PSQL_TENANT_NAMESPACES='x-career-dev,public',
EMAIL_SENDER=testing_visitor@xchange.com.tw,
EMAIL_VERIFY_CODE_TEMPLATE=None,
EMAIL_RESET_PASSWORD_TEMPLATE=None,
FRONTEND_SIGNUP_URL=https://xtalent.vercel.app/auth/emailVerified?token=,
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
