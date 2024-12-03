import os


SITE_TITLE = os.getenv('SITE_TITLE', 'X-Career')
LOCAL_REGION = os.getenv('AWS_REGION', 'ap-northeast-1')

# probe cycle secs
PROBE_CYCLE_SECS = int(os.getenv('PROBE_CYCLE_SECS', 3))

# database conf
# TODO: connection conf..
BATCH_LIMIT = int(os.getenv('BATCH_LIMIT', '20'))
DB_URL = os.getenv('DB_URL', 'postgresql+asyncpg://user:password@localhost:5432/postgres')
POOL_PRE_PING = bool(int(os.getenv('POOL_PRE_PING', '1'))) # 檢查連線狀態
POOL_RECYCLE = int(os.getenv('POOL_RECYCLE', 300))  # 定期重置連線
POOL_SIZE = int(os.getenv('POOL_SIZE', 10))         # 連線池大小
MAX_OVERFLOW = int(os.getenv('MAX_OVERFLOW', 20))   # 超出連線池大小時，最大連線數
AUTO_COMMIT = bool(int(os.getenv('AUTO_COMMIT', '0')))  # 自動提交
AUTO_FLUSH = bool(int(os.getenv('AUTO_FLUSH', '0')))    # 自動刷新

# postgres 為多租戶設計的機制，透過 schema 來區分不同租戶的資料
PSQL_TENANT_NAMESPACES = os.getenv('PSQL_TENANT_NAMESPACES', 'x-career-dev,public') # public x-career-dev


# email conf
EMAIL_SENDER = os.getenv('EMAIL_SENDER', 'support@exchange.com')
EMAIL_VERIFY_CODE_TEMPLATE = os.getenv('EMAIL_VERIFY_CODE_TEMPLATE', None)
EMAIL_RESET_PASSWORD_TEMPLATE = os.getenv('EMAIL_RESET_PASSWORD_TEMPLATE', None)
FRONTEND_SIGNUP_URL = os.getenv('FRONTEND_SIGNUP_URL', 'http://localhost:8002/auth/signup?token=')
FRONTEND_RESET_PASSWORD_URL = os.getenv('FRONTEND_RESET_PASSWORD_URL', 'http://localhost:8002/auth/reset_password?token=')
SES_CONNECT_TIMEOUT = int(os.getenv('SES_CONNECT_TIMEOUT', 10))
SES_READ_TIMEOUT = int(os.getenv('SES_READ_TIMEOUT', 10))
SES_MAX_ATTEMPTS = int(os.getenv('SES_MAX_ATTEMPTS', 3))


# Google App conf
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', None)
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', None)
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', None)


# LinkedIn App conf
LINKEDIN_APP_ID = os.getenv('LINKEDIN_APP_ID', None)
LINKEDIN_APP_SECRET = os.getenv('LINKEDIN_APP_SECRET', None)
LINKEDIN_REDIRECT_URI = os.getenv('LINKEDIN_REDIRECT_URI', None)


# # FB App conf
# FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID', None)
# FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET', None)
# FACEBOOK_REDIRECT_URI = os.getenv('FACEBOOK_REDIRECT_URI', None)
