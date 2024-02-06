import logging.config
import os
from pprint import pprint

from dependency_injector import containers, providers

from apiclients.realisations import OpenweathermapByCityAPIClient
from configurations.dotenv_file import DotenvSettings
from configurations.ini_file import IniConfigSettings
from configurations.merged_config import merge_dicts
from configurations.yaml_file import YamlLoggingSettings
from database.db import Database
from mappers.realisations import (
    JsonMapper,
    OpenweathermapWeatherMapper,
    TextfileMapper,
    WeatherDatabaseMapper,
)
from master import MasterService
from repositories.manager import DatabaseRepositoriesManager
from repositories.realisations import (
    JsonRepository,
    TextfileRepository,
    WeatherDatabaseRepository,
)
from storage_services.manager import StorageServiceManager
from storage_services.realisations import DatabaseService, FileService
from units_of_work.realisations import WeatherUnitOfWork


class Core(containers.DeclarativeContainer):
    config = providers.Configuration()

    logging_provider = providers.Resource(
        logging.config.dictConfig,
        config=config,
    )


class Mappers(containers.DeclarativeContainer):
    textfile_mapper_provider = providers.Singleton(TextfileMapper)

    json_mapper_provider = providers.Singleton(JsonMapper)

    weather_database_mapper_provider = providers.Singleton(WeatherDatabaseMapper)

    client_storage_mapper_provider = providers.Singleton(OpenweathermapWeatherMapper)


class Repositories(containers.DeclarativeContainer):
    config = providers.Configuration()

    mappers = providers.DependenciesContainer()

    text_repo_provider = providers.Singleton(
        TextfileRepository,
        filepath=config.text_repo.filepath,
        mapper=mappers.textfile_mapper_provider,
    )

    json_repo_provider = providers.Singleton(
        JsonRepository,
        filepath=config.json_repo.filepath,
        mapper=mappers.json_mapper_provider,
    )

    database_repositories_list_provider = providers.List(
        providers.Singleton(
            WeatherDatabaseRepository, mapper=mappers.weather_database_mapper_provider
        )
    )


class Database(containers.DeclarativeContainer):
    config = providers.Configuration()

    database_provider = providers.Singleton(Database, db_url=config.dsn)


class UnitsOfWork(containers.DeclarativeContainer):
    database = providers.DependenciesContainer()

    repositories = providers.DependenciesContainer()

    database_repositories_manager_provider = providers.Singleton(
        DatabaseRepositoriesManager,
        repository_instances=repositories.database_repositories_list_provider,
    )

    weather_uow_provider = providers.Singleton(
        WeatherUnitOfWork,
        database_repositories_manager=database_repositories_manager_provider,
        async_session_factory=database.database_provider.provided.get_session_factory,
    )


class StorageServices(containers.DeclarativeContainer):
    config = providers.Configuration()

    repositories = providers.DependenciesContainer()

    units_of_work = providers.DependenciesContainer()

    storage_services_list_provider = providers.List(
        providers.Singleton(
            DatabaseService,
            uow=units_of_work.weather_uow_provider,
            service_designation="db",
        ),
        providers.Singleton(
            FileService,
            repository=repositories.text_repo_provider,
            service_designation="text",
        ),
        providers.Singleton(
            FileService,
            repository=repositories.json_repo_provider,
            service_designation="json",
        ),
    )

    storage_services_manager_provider = providers.Factory(
        StorageServiceManager,
        all_storage_services=storage_services_list_provider,
        selected_storage_services=config.selected_storage_services,
    )


class ApiClients(containers.DeclarativeContainer):
    config = providers.Configuration()

    weather_client_provider = providers.Factory(
        OpenweathermapByCityAPIClient, api_key=config.weather_client.api_key
    )


class Master(containers.DeclarativeContainer):
    storage_services = providers.DependenciesContainer()

    api_clients = providers.DependenciesContainer()

    mappers = providers.DependenciesContainer()

    master_service_provider = providers.Factory(
        MasterService,
        weather_client=api_clients.weather_client_provider,
        client_storage_mapper=mappers.client_storage_mapper_provider,
        storage_services_manager=storage_services.storage_services_manager_provider,
    )


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()

    core = providers.Container(Core, config=config.logging)

    mappers = providers.Container(Mappers)

    repositories = providers.Container(
        Repositories, config=config.repositories, mappers=mappers
    )

    database = providers.Container(Database, config=config.database)

    units_of_work = providers.Container(
        UnitsOfWork, database=database, repositories=repositories
    )

    storage_services = providers.Container(
        StorageServices,
        config=config.storage_services,
        repositories=repositories,
        units_of_work=units_of_work,
    )

    api_clients = providers.Container(ApiClients, config=config.api_clients)

    master = providers.Container(
        Master,
        storage_services=storage_services,
        api_clients=api_clients,
        mappers=mappers,
    )


if __name__ == "__main__":
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

    dotenv_settings = DotenvSettings(
        _env_file=os.path.join(ROOT_DIR, ".env")
    ).model_dump()
    config_ini_settings = IniConfigSettings(
        ini_file=os.path.join(ROOT_DIR, "config.ini"), root_dir=ROOT_DIR
    )
    logging_yaml_settings = YamlLoggingSettings(
        yaml_file=os.path.join(ROOT_DIR, "logging.yaml")
    )
    settings_dict = merge_dicts(
        dotenv_settings, config_ini_settings, logging_yaml_settings
    )
    pprint(settings_dict)

    application = Application()
    application.config.from_dict(settings_dict)
    application.core.init_resources()

    master_service = application.master.master_service_provider()

    # Полезные вещи про логгер
    logger = logging.getLogger("my_app")

    effective_level = logger.getEffectiveLevel()
    # Выводим текущий уровень записей (level)
    print("Effective logging level:", effective_level)

    loggers = logging.Logger.manager.loggerDict

    # Выведите имена всех логгеров
    for name, logger in loggers.items():
        print(name)

    logger.debug("debug message", extra={"x": "hello"})
    logger.info("info message")
    logger.warning("warning message")
    logger.error("error message")
    logger.critical("critical message")
