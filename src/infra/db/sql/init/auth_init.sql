-- user_id 自動遞增
CREATE SEQUENCE IF NOT EXISTS user_id_seq;

-- accounts 表：欄位/型別/約束對齊 ORM Account（src/infra/db/sql/orm/auth_orm.py）
CREATE TABLE IF NOT EXISTS accounts (
    aid BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,      -- DynamoDB partition key，對應唯一非空
    email2 VARCHAR(255),
    pass_hash VARCHAR(60),                   -- e.g. bcrypt 60 chars
    pass_salt VARCHAR(60),
    oauth_id VARCHAR(255),                   -- 一般帳號為空字串，OAuth 帳號才有值
    refresh_token VARCHAR(255),
    user_id BIGINT UNIQUE DEFAULT nextval('user_id_seq'),
    account_type VARCHAR(50) NOT NULL,       -- AccountType enum 僅在程式層驗證
    is_active BOOLEAN DEFAULT TRUE,
    region VARCHAR(50),
    created_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
    updated_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW())
);

-- 註：email 唯一性由上方欄位層 UNIQUE 約束（accounts_email_key）保證，
-- 不再額外建立重複的 email 索引。

-- oauth_id 唯一索引：僅對「非空且非 NULL」的 oauth_id 建立，
-- 避免一般帳號 oauth_id='' 互相衝突（對應 ORM 註解：避免對空字串或 NULL 建立索引）
CREATE UNIQUE INDEX IF NOT EXISTS uidx_accounts_oauth_id
    ON accounts (oauth_id)
    WHERE oauth_id IS NOT NULL AND oauth_id <> '';
