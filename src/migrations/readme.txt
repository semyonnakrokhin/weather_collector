alembic init src/migrations

в alembic.ini:
    prepend_sys_path = . src
    sqlalchemy.url = дефолтный dsn

в src/migrations/env.py:
    config.set_main_option("sqlalchemy.url", свой dsn из конфига + "?async_fallback=True") - заменили дефолтный dsn из alembic.ini
    target_metadata = Base.metadata
    from models.entities import WeatherORMModel  подгрузили орм-ные модели

alembic revision --autogenerate
    Долго была ошибка с тем что не создавалась бд alembic_version из-за того, что semyon не имел доступа к схеме public
    Помогло:
    ALTER DATABASE weather_db OWNER TO semyon;

alembic upgrade head

--------------------------
Далее рабоатюь эти команды
alembic revision --autogenerate
(Если в файле миграции в функции upgrade чего то недостает, смотри в env.py функцию run_migrations_online
alembic upgrade head