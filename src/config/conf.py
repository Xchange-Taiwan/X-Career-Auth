import os

LOCAL_REGION = os.getenv('AWS_REGION', 'ap-northeast-1')

# probe cycle secs
PROBE_CYCLE_SECS = int(os.getenv('PROBE_CYCLE_SECS', 3))

# database conf
# dynamodb
DDB_TABLE_ACCOUNTS = os.getenv('DYNAMODB_TABLE_ACCOUNTS', 'dev_x_career_auth_accounts')

# postgres
# TODO: connection conf..
BATCH_LIMIT = int(os.getenv('BATCH_LIMIT', '20'))
DB_URL = os.getenv(
    'DB_URL', 'postgresql+asyncpg://kao:password@localhost:5432/postgres'
)
POOL_PRE_PING = bool(int(os.getenv('POOL_PRE_PING', '1')))  # 檢查連線狀態
POOL_RECYCLE = int(os.getenv('POOL_RECYCLE', 300))  # 定期重置連線
POOL_SIZE = int(os.getenv('POOL_SIZE', 10))         # 連線池大小
MAX_OVERFLOW = int(os.getenv('MAX_OVERFLOW', 20))   # 超出連線池大小時，最大連線數
AUTO_COMMIT = bool(int(os.getenv('AUTO_COMMIT', '0')))  # 自動提交
AUTO_FLUSH = bool(int(os.getenv('AUTO_FLUSH', '0')))    # 自動刷新

# postgres 為多租戶設計的機制，透過 schema 來區分不同租戶的資料
PSQL_TENANT_NAMESPACES = os.getenv(
    'PSQL_TENANT_NAMESPACES', 'x-career-dev,public')  # public x-career-dev


# email conf
SITE_TITLE = os.getenv('SITE_TITLE', 'X-Career')
EMAIL_SENDER = os.getenv('EMAIL_SENDER', 'testing_visitor@xchange.com.tw')
# 前端連結：{FRONTEND_HOSTNAME}{FRONTEND_URL_PATH_*}?{FRONTEND_TOKEN}={token}
FRONTEND_HOSTNAME = os.getenv('FRONTEND_HOSTNAME', 'http://localhost:8002')
FRONTEND_URL_PATH_EMAIL_VERIFIED = os.getenv(
    'FRONTEND_URL_PATH_EMAIL_VERIFIED', '/auth/email-verified')
FRONTEND_URL_PATH_RESET_PASSWORD = os.getenv(
    'FRONTEND_URL_PATH_RESET_PASSWORD', '/auth/password-reset')
FRONTEND_TOKEN = os.getenv('FRONTEND_TOKEN', 'token')
SES_CONNECT_TIMEOUT = int(os.getenv('SES_CONNECT_TIMEOUT', 10))
SES_READ_TIMEOUT = int(os.getenv('SES_READ_TIMEOUT', 10))
SES_MAX_ATTEMPTS = int(os.getenv('SES_MAX_ATTEMPTS', 3))
