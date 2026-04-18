# X-Career-Auth

Authentication service for the X-Talent platform. Handles email/password credentials and email verification. Deployed as an AWS Lambda function via the Serverless Framework.

## Prerequisites

- Python 3.9
- PostgreSQL (local or remote)
- AWS credentials configured (for DynamoDB and SES, even locally)

## Local Development

### 1. Set up environment

```bash
cp .env.example .env
```

Edit `.env` and fill in the required values (see [Environment Variables](#environment-variables) below).

### 2. Create virtual environment and install dependencies

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the server

```bash
uvicorn main:app --host 0.0.0.0 --port 8008 --reload
```

API docs are available at **http://localhost:8008/docs**

## Environment Variables

Copy `.env.example` to `.env` and fill in the values below.

| Variable | Default | Description |
|---|---|---|
| `STAGE` | — | Deployment stage (`dev` / `prod`) |
| `THE_REGION` | `ap-northeast-1` | AWS region |
| `ACCOUNT_ID` | — | AWS account ID (12 digits) |
| `DB_URL` | `postgresql+asyncpg://kao:password@localhost:5432/postgres` | PostgreSQL connection string |
| `PSQL_TENANT_NAMESPACES` | `x-career-dev,public` | Database schemas (comma-separated) |
| `DYNAMODB_TABLE_ACCOUNTS` | `dev_x_career_auth_accounts` | DynamoDB table name |
| `SITE_TITLE` | `X-Career` | Site title used in email subjects |
| `FRONTEND_HOSTNAME` | `http://localhost:8002` | Frontend base URL |
| `FRONTEND_URL_PATH_EMAIL_VERIFIED` | `/auth/email-verified` | Frontend path for email verification redirect |
| `FRONTEND_URL_PATH_RESET_PASSWORD` | `/auth/password-reset` | Frontend path for password reset redirect |
| `FRONTEND_TOKEN` | — | Token used to validate frontend requests |
| `EMAIL_SENDER` | — | SES sender email address |

### Minimal local setup

For basic local testing without email or OAuth, set at minimum:

```env
STAGE=dev
THE_REGION=ap-northeast-1
DB_URL=postgresql+asyncpg://<user>:<password>@localhost:5432/<dbname>
PSQL_TENANT_NAMESPACES=public
DYNAMODB_TABLE_ACCOUNTS=dev_x_career_auth_accounts
FRONTEND_HOSTNAME=http://localhost:3000
```

> **Note:** AWS SES (email sending) and DynamoDB require valid AWS credentials in the environment (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`). If you skip these, the startup probe will fail but basic auth endpoints may still respond.

## API Routes

All routes are prefixed with `/auth-service/api/v1`.

| Prefix | Description |
|---|---|
| `/auth-service/api/v1/auth` | Email/password registration, login, token refresh |
| `/auth-service/api/v1/oauth` | Google and LinkedIn OAuth flows |

## Deploy to AWS

```bash
./deploy.sh -e dev -r ap-northeast-1
```

The script substitutes environment variables from `.env` into `serverless.yml` then runs `sh deploy.sh -e dev -r ap-northeast-1`.
