"""added author

Revision ID: 807237629cc9
Revises: c45a90f4bf48
Create Date: 2024-09-23 14:44:04.806150

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '807237629cc9'
down_revision = 'c45a90f4bf48'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('text', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('text', schema=None) as batch_op:
        batch_op.drop_column('author')

    # ### end Alembic commands ###
