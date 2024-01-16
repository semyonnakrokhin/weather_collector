from dependency_injector import containers, providers

from apiclients.realisations import OpenweathermapByCityAPIClient
from config import Settings

# from config_1_7 import Settings
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
    application = Application()
    settings_dict = Settings().model_dump()
    application.config.from_dict(settings_dict)

    master_service = application.master.master_service_provider()
    c = 1
