import boto3

client = boto3.client(
    "dynamodb",
    region_name="ap-northeast-1",
    endpoint_url="http://localhost:4566",
    aws_access_key_id="test",
    aws_secret_access_key="test",
)

def test_dynamodb_table_exists(localstack_ready):
    response = client.list_tables()
    tables = response["TableNames"]
    assert "dev_x_career_auth_accounts" in tables, f"Table not found. Existing tables:{tables}"
