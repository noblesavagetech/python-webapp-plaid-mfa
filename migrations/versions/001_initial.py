"""Initial migration - create users table with Vonage support

Revision ID: 001_initial
Revises: 
Create Date: 2025-12-31

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table with all fields including Vonage support
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('email_verified', sa.Boolean(), nullable=True),
        sa.Column('verification_code', sa.String(length=6), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('mfa_enabled', sa.Boolean(), nullable=True),
        sa.Column('vonage_request_id', sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )


def downgrade():
    op.drop_table('users')
