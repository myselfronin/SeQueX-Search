"""empty message

Revision ID: 4ad6437ff6e1
Revises: 7b235e0c0de9
Create Date: 2024-01-27 10:41:16.443807

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ad6437ff6e1'
down_revision = '7b235e0c0de9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('papers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('semantic_topics', sa.ARRAY(sa.String()), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('papers', schema=None) as batch_op:
        batch_op.drop_column('semantic_topics')

    # ### end Alembic commands ###
