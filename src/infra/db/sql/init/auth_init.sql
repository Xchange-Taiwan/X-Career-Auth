-- Create unique index with oauth_id and email
CREATE UNIQUE INDEX uidx_accounts_oauth_id ON accounts (oauth_id);
CREATE UNIQUE INDEX uidx_accounts_email ON accounts (email);

-- 创建 ENUM 类型，仅当不存在时
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'account_type') THEN
        CREATE TYPE ACCOUNT_TYPE AS ENUM('XC', 'GOOGLE', 'LINKEDIN');
    END IF;
END
$$;

-- user_id 自動遞增
CREATE SEQUENCE IF NOT EXISTS user_id_seq;

CREATE TABLE IF NOT EXISTS accounts (
    aid BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL, -- Email addresses are typically VARCHAR with a length constraint
    email2 VARCHAR(255),                -- Same for the secondary email address
    pass_hash VARCHAR(60),              -- Password hashes often have a fixed length (e.g., bcrypt is 60 characters)
    pass_salt VARCHAR(60),              -- Assuming the salt is a fixed-length string (e.g., bcrypt salts are often 29 characters)
    oauth_id VARCHAR(255),              -- OAuth IDs are usually strings but can have a variable length
    refresh_token VARCHAR(255),         -- Refresh tokens are usually strings but can have a variable length
    user_id BIGINT UNIQUE DEFAULT nextval('user_id_seq'),       -- Integer is fine for user IDs, keeping the UNIQUE constraint
    account_type ACCOUNT_TYPE,          -- Assuming 'account_type' is an ENUM or a custom type
    is_active BOOLEAN DEFAULT TRUE,     -- BOOLEAN is a more appropriate type for true/false values
    region VARCHAR(50),                 -- Regions are typically short strings, so VARCHAR(50) should suffice
    created_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW()),
    updated_at BIGINT DEFAULT EXTRACT(EPOCH FROM NOW())
);

-- 创建唯一索引，仅当 oauth_id 不为空时，避免空字符串造成索引偏斜 (避免對空字串或 NULL 建立索引)
CREATE UNIQUE INDEX uidx_accounts_oauth_id_email ON accounts (oauth_id, email) WHERE oauth_id <> '' and oauth_id <> NULL;
CREATE UNIQUE INDEX uidx_accounts_email ON accounts (email);
