"""Add input_format and output_format to Problem model

Revision ID: cbdb9bc43820
Revises: 1eedc8595c16
Create Date: 2024-10-25 15:59:57.632951

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cbdb9bc43820'
down_revision = '1eedc8595c16'
branch_labels = None
depends_on = None


def upgrade():
    # 새 컬럼을 nullable=True로 추가
    op.add_column('problem', sa.Column('input_format', sa.Text(), nullable=True))
    op.add_column('problem', sa.Column('output_format', sa.Text(), nullable=True))
    
    # 기존 레코드에 대해 빈 문자열로 초기화
    op.execute("UPDATE problem SET input_format = '', output_format = ''")
    
    # 컬럼을 NOT NULL로 변경
    with op.batch_alter_table('problem') as batch_op:
        batch_op.alter_column('input_format', nullable=False, server_default='')
        batch_op.alter_column('output_format', nullable=False, server_default='')

def downgrade():
    op.drop_column('problem', 'output_format')
    op.drop_column('problem', 'input_format')
