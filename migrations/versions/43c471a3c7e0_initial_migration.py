"""Initial migration

Revision ID: 43c471a3c7e0
Revises: cbdb9bc43820
Create Date: 2024-10-25 16:35:54.731573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '43c471a3c7e0'
down_revision = 'cbdb9bc43820'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('submission',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('problem_id', sa.Integer(), nullable=False),
    sa.Column('passed', sa.Boolean(), nullable=True),
    sa.Column('submitted_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['problem_id'], ['problem.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('submission')
    # ### end Alembic commands ###