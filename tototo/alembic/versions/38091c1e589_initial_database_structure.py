"""Initial database structure

Revision ID: 38091c1e589
Revises: 
Create Date: 2015-01-29 14:21:32.784786

"""

# revision identifiers, used by Alembic.
revision = '38091c1e589'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto;')
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=32), nullable=True),
        sa.Column('email', sa.String(length=256), nullable=False),
        sa.Column('mail_subscribe', sa.Boolean(), nullable=True),
        sa.Column('hashed_password', sa.String(length=60), nullable=False),
        sa.Column('registered', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_table(
        'meetings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=32), nullable=False),
        sa.Column('where', sa.String(length=128), nullable=False),
        sa.Column('when', sa.DateTime(timezone=True), nullable=False),
        sa.Column('available', sa.Boolean(), nullable=True),
        sa.Column('quota', sa.Integer(), nullable=True),
        sa.Column('registered', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'registrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('meeting_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=16), nullable=True),
        sa.Column('memo', sa.String(length=512), nullable=True),
        sa.Column('registered', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('registrations')
    op.drop_table('meetings')
    op.drop_table('users')
    op.execute('DROP EXTENSION IF EXISTS pgcrypto;')
