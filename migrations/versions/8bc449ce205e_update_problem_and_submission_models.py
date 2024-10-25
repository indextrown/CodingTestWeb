"""Update Problem and Submission models

Revision ID: 8bc449ce205e
Revises: 43c471a3c7e0
Create Date: 2024-10-25 16:37:21.594273

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8bc449ce205e'
down_revision = '43c471a3c7e0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('problem', schema=None) as batch_op:
        batch_op.drop_column('memory_limit')
        batch_op.drop_column('example_output')
        batch_op.drop_column('input_format')
        batch_op.drop_column('example_input')
        batch_op.drop_column('time_limit')
        batch_op.drop_column('input_description')
        batch_op.drop_column('output_format')
        batch_op.drop_column('output_description')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('problem', schema=None) as batch_op:
        batch_op.add_column(sa.Column('output_description', sa.TEXT(), nullable=False))
        batch_op.add_column(sa.Column('output_format', sa.TEXT(), server_default=sa.text("('')"), nullable=False))
        batch_op.add_column(sa.Column('input_description', sa.TEXT(), nullable=False))
        batch_op.add_column(sa.Column('time_limit', sa.FLOAT(), nullable=False))
        batch_op.add_column(sa.Column('example_input', sa.TEXT(), nullable=False))
        batch_op.add_column(sa.Column('input_format', sa.TEXT(), server_default=sa.text("('')"), nullable=False))
        batch_op.add_column(sa.Column('example_output', sa.TEXT(), nullable=False))
        batch_op.add_column(sa.Column('memory_limit', sa.INTEGER(), nullable=False))

    # ### end Alembic commands ###