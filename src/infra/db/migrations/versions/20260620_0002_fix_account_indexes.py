"""Replace legacy account indexes with the intended partial OAuth index.

Revision ID: 20260620_0002
Revises: 20260620_0001
Create Date: 2026-06-20
"""
import os
from typing import Sequence, Union

from alembic import context, op
from sqlalchemy import inspect, text


revision: str = '20260620_0002'
down_revision: Union[str, None] = '20260620_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _schema() -> str:
    x_args = context.get_x_argument(as_dictionary=True)
    return x_args.get('schema') or os.getenv('DB_SCHEMA', 'public').strip()


def _quoted_schema(bind) -> str:
    return bind.dialect.identifier_preparer.quote_schema(_schema())


def _indexes(bind):
    inspector = inspect(bind)
    if not inspector.has_table('accounts', schema=_schema()):
        return {}
    return {
        index['name']: index
        for index in inspector.get_indexes('accounts', schema=_schema())
    }


def upgrade() -> None:
    bind = op.get_bind()
    indexes = _indexes(bind)
    if not indexes and not inspect(bind).has_table('accounts', schema=_schema()):
        return

    duplicate_count = bind.execute(text(
        f'''
        SELECT count(*)
        FROM (
            SELECT oauth_id
            FROM {_quoted_schema(bind)}.accounts
            WHERE oauth_id IS NOT NULL AND oauth_id <> ''
            GROUP BY oauth_id
            HAVING count(*) > 1
        ) duplicates
        '''
    )).scalar_one()
    if duplicate_count:
        raise RuntimeError(
            f'cannot create unique oauth_id index: '
            f'{duplicate_count} duplicate oauth_id groups found'
        )

    for legacy_index in (
        'uidx_accounts_oauth_id_email',
        'uidx_accounts_email',
    ):
        if legacy_index in indexes:
            op.drop_index(
                legacy_index,
                table_name='accounts',
                schema=_schema(),
            )

    if 'uidx_accounts_oauth_id' not in _indexes(bind):
        op.create_index(
            'uidx_accounts_oauth_id',
            'accounts',
            ['oauth_id'],
            unique=True,
            schema=_schema(),
            postgresql_where=text(
                "oauth_id IS NOT NULL AND oauth_id <> ''"
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    indexes = _indexes(bind)
    if not indexes and not inspect(bind).has_table('accounts', schema=_schema()):
        return

    if 'uidx_accounts_oauth_id' in indexes:
        op.drop_index(
            'uidx_accounts_oauth_id',
            table_name='accounts',
            schema=_schema(),
        )

    indexes = _indexes(bind)
    if 'uidx_accounts_email' not in indexes:
        op.create_index(
            'uidx_accounts_email',
            'accounts',
            ['email'],
            unique=True,
            schema=_schema(),
        )

    if 'uidx_accounts_oauth_id_email' not in indexes:
        op.create_index(
            'uidx_accounts_oauth_id_email',
            'accounts',
            ['oauth_id', 'email'],
            unique=True,
            schema=_schema(),
            postgresql_where=text(
                "oauth_id <> '' AND oauth_id <> NULL"
            ),
        )
