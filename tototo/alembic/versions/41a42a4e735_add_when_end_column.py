"""add when_end column

Revision ID: 41a42a4e735
Revises: 38091c1e589
Create Date: 2015-05-23 11:41:11.870067

"""

# revision identifiers, used by Alembic.
revision = '41a42a4e735'
down_revision = '38091c1e589'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('meetings', sa.Column('when_end', sa.DateTime(timezone=True), server_default=sa.func.now(),
                                        nullable=False))


def downgrade():
    op.drop_column('meetings', 'when_end')
