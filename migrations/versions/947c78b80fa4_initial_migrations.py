"""initial migrations

Revision ID: 947c78b80fa4
Revises: 7dad980ca7aa
Create Date: 2023-08-31 16:23:55.884419

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '947c78b80fa4'
down_revision = '7dad980ca7aa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('register', schema=None) as batch_op:
        batch_op.drop_column('f_name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('register', schema=None) as batch_op:
        batch_op.add_column(sa.Column('f_name', sa.VARCHAR(length=50), nullable=True))

    # ### end Alembic commands ###
