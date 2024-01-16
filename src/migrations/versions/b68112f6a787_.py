"""empty message

Revision ID: b68112f6a787
Revises: 
Create Date: 2024-01-14 00:13:10.543623

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b68112f6a787'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('weather_table',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('city', sa.String(), nullable=False),
    sa.Column('temperature', sa.Integer(), nullable=False),
    sa.Column('weather_type', sa.Enum('THUNDERSTORM', 'DRIZZLE', 'RAIN', 'SNOW', 'MIST', 'SMOKE', 'HAZE', 'DUST', 'FOG', 'SAND', 'ASH', 'SQUALL', 'TORNADO', 'CLEAR', 'CLOUDS', name='weathertypeopenweathermap'), nullable=False),
    sa.Column('sunrise', sa.Time(), nullable=False),
    sa.Column('sunset', sa.Time(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('timestamp', 'city', name='uq_timestamp_city')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('weather_table')
    # ### end Alembic commands ###
