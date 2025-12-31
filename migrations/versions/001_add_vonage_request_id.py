"""Add vonage_request_id field for Vonage Verify API

Revision ID: 001_vonage_migration
Revises: 
Create Date: 2025-12-31

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_vonage_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add vonage_request_id column to users table
    op.add_column('users', sa.Column('vonage_request_id', sa.String(length=64), nullable=True))


def downgrade():
    # Remove vonage_request_id column from users table
    op.drop_column('users', 'vonage_request_id')
