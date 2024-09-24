"""empty message

Revision ID: 01b4f8b60d89
Revises: b71a40ff3f51
Create Date: 2024-09-25 00:17:47.840074

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '01b4f8b60d89'
down_revision = 'b71a40ff3f51'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_url', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('video_url', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('video_url')
        batch_op.drop_column('image_url')

    # ### end Alembic commands ###
