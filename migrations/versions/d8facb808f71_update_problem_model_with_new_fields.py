"""Update Problem model with new fields

Revision ID: d8facb808f71
Revises: 8bc449ce205e
Create Date: 2024-10-25 16:52:24.529931

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8facb808f71'
down_revision = '8bc449ce205e'
branch_labels = None
depends_on = None


def upgrade():
    # 임시 테이블 생성
    op.create_table('problem_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('difficulty', sa.String(length=20), nullable=False),
        sa.Column('test_cases', sa.Text(), nullable=False),
        sa.Column('submissions', sa.Integer(), nullable=True),
        sa.Column('correct_submissions', sa.Integer(), nullable=True),
        sa.Column('time_limit', sa.Float(), nullable=False),
        sa.Column('memory_limit', sa.Integer(), nullable=False),
        sa.Column('input_description', sa.Text(), nullable=False),
        sa.Column('output_description', sa.Text(), nullable=False),
        sa.Column('input_format', sa.Text(), nullable=False),
        sa.Column('output_format', sa.Text(), nullable=False),
        sa.Column('example_input', sa.Text(), nullable=False),
        sa.Column('example_output', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # 데이터 복사
    op.execute('''
        INSERT INTO problem_new (id, title, description, difficulty, test_cases, submissions, correct_submissions,
                                 time_limit, memory_limit, input_description, output_description,
                                 input_format, output_format, example_input, example_output)
        SELECT id, title, description, difficulty, test_cases, submissions, correct_submissions,
               1.0, 128, '', '', '', '', '', ''
        FROM problem
    ''')

    # 기존 테이블 삭제
    op.drop_table('problem')

    # 새 테이블 이름 변경
    op.rename_table('problem_new', 'problem')


def downgrade():
    # 여기에 downgrade 로직을 추가하세요
    pass
