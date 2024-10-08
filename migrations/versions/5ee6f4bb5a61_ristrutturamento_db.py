"""Ristrutturamento db

Revision ID: 5ee6f4bb5a61
Revises: 807237629cc9
Create Date: 2024-10-07 13:19:08.275071

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5ee6f4bb5a61'
down_revision = '807237629cc9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('quote',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('content', sa.String(length=255), nullable=True),
    sa.Column('author', sa.String(length=50), nullable=True),
    sa.Column('year', sa.Date(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('content')
    )
    with op.batch_alter_table('text', schema=None) as batch_op:
        batch_op.drop_index('content')

    op.drop_table('text')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('text',
    sa.Column('id', mysql.INTEGER(display_width=11), autoincrement=True, nullable=False),
    sa.Column('content', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('category_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
    sa.Column('author', mysql.VARCHAR(length=50), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['category.id'], name='text_ibfk_1'),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_general_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    with op.batch_alter_table('text', schema=None) as batch_op:
        batch_op.create_index('content', ['content'], unique=True)

    op.drop_table('quote')
    # ### end Alembic commands ###
