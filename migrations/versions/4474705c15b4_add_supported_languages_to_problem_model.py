"""Add supported_languages to Problem model

Revision ID: 4474705c15b4
Revises: d8facb808f71
Create Date: 2024-10-25 17:41:40.722638

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4474705c15b4'
down_revision = 'd8facb808f71'
branch_labels = None
depends_on = None


def upgrade():
    # Problem 테이블 수정
    with op.batch_alter_table('problem') as batch_op:
        batch_op.add_column(sa.Column('supported_languages', sa.String(length=100), nullable=True))
    
    # 기존 데이터에 대한 기본값 설정
    op.execute("UPDATE problem SET supported_languages = 'python,c,cpp,java,swift'")
    
    # NOT NULL 제약 조건 추가
    with op.batch_alter_table('problem') as batch_op:
        batch_op.alter_column('supported_languages', nullable=False)

    # Submission 테이블 수정
    with op.batch_alter_table('submission') as batch_op:
        batch_op.add_column(sa.Column('language', sa.String(length=100), nullable=True))
    
    # 기존 Submission 데이터에 대한 기본값 설정
    op.execute("UPDATE submission SET language = 'python'")
    
    # NOT NULL 제약 조건 추가
    with op.batch_alter_table('submission') as batch_op:
        batch_op.alter_column('language', nullable=False)

def downgrade():
    with op.batch_alter_table('problem') as batch_op:
        batch_op.drop_column('supported_languages')
    
    with op.batch_alter_table('submission') as batch_op:
        batch_op.drop_column('language')