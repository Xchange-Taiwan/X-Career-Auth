import os


SITE_TITLE = os.getenv('SITE_TITLE', 'X-Career')
LOCAL_REGION = os.environ['AWS_REGION']


# database conf
# TODO: connection conf..
BATCH_LIMIT = int(os.getenv('BATCH_LIMIT', '20'))
DB_URL = os.getenv('DB_URL', 'postgresql+asyncpg://myuser:mypassword@localhost:5432/postgres')


# email conf
EMAIL_SENDER = os.getenv('EMAIL_SENDER', 'user@example.com')
EMAIL_VERIFY_CODE_TEMPLATE = os.getenv('EMAIL_VERIFY_CODE_TEMPLATE', None)
EMAIL_RESET_PASSWORD_TEMPLATE = os.getenv('EMAIL_RESET_PASSWORD_TEMPLATE', None)
FRONTEND_RESET_PASSWORD_URL = os.getenv('FRONTEND_RESET_PASSWORD_URL', 'https://localhost:8002/auth/reset_password?token=')


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
