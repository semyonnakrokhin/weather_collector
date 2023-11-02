"""unique constrain

Revision ID: 820349cbcb68
Revises: ba4b9401a4cf
Create Date: 2023-10-20 10:53:16.627154

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "820349cbcb68"
down_revision: Union[str, None] = "ba4b9401a4cf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("weather_table_city_key", "weather_table", type_="unique")
    op.drop_constraint("weather_table_timestamp_key", "weather_table", type_="unique")
    op.create_unique_constraint(
        "uq_timestamp_city", "weather_table", ["timestamp", "city"]
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("uq_timestamp_city", "weather_table", type_="unique")
    op.create_unique_constraint(
        "weather_table_timestamp_key", "weather_table", ["timestamp"]
    )
    op.create_unique_constraint("weather_table_city_key", "weather_table", ["city"])
    # ### end Alembic commands ###