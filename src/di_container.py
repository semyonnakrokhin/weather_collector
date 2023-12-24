from dependency_injector import containers, providers

from apiclients.realisations import OpenweathermapByCityAPIClient
from config import di_configuration_dict
from mappers.realisations import JsonMapper, OpenweathermapWeatherMapper, TextfileMapper
from master import MasterService
from repositories.realisations import (
    JsonRepository,
    TextfileRepository,
    WeatherUnitOfWork,
)
from storage_services.realisations import DatabaseService, FileService

# Temporary workaround, fix after figuring out framework dependency_injector
selected_storage_services = di_configuration_dict["services"]["storage_services"][
    "selected_storage_services"
]


class Mappers(containers.DeclarativeContainer):
    textfile_mapper = providers.Singleton(TextfileMapper)

    json_mapper = providers.Singleton(JsonMapper)

    client_storage_mapper = providers.Singleton(OpenweathermapWeatherMapper)


class Repositories(containers.DeclarativeContainer):
    config = providers.Configuration()

    mappers = providers.DependenciesContainer()

    text_repo = providers.Singleton(
        TextfileRepository,
        filepath=config.textfile_path,
        mapper=mappers.textfile_mapper,
    )

    json_repo = providers.Singleton(
        JsonRepository, filepath=config.jsonfile_path, mapper=mappers.json_mapper
    )

    weather_uow = providers.Singleton(WeatherUnitOfWork)


class Services(containers.DeclarativeContainer):
    config = providers.Configuration()

    repositories = providers.DependenciesContainer()

    service_factories = {
        "db": providers.Factory(DatabaseService, uow=repositories.weather_uow),
        "text": providers.Factory(FileService, repository=repositories.text_repo),
        "json": providers.Factory(FileService, repository=repositories.json_repo),
    }

    storage_services = providers.List(
        *[
            value
            for key, value in service_factories.items()
            if key in selected_storage_services
        ]
    )

    api_client_service = providers.Factory(
        OpenweathermapByCityAPIClient, api_key=config.api_client.api_key
    )


class Master(containers.DeclarativeContainer):
    services = providers.DependenciesContainer()

    mappers = providers.DependenciesContainer()

    master_service = providers.Factory(
        MasterService,
        api_client=services.api_client_service,
        client_storage_mapper=mappers.client_storage_mapper,
        storage_services=services.storage_services,
    )


class Application(containers.DeclarativeContainer):
    config = providers.Configuration()
    config.from_dict(di_configuration_dict)

    mappers = providers.Container(Mappers)

    repositories = providers.Container(
        Repositories, config=config.repositories, mappers=mappers
    )

    services = providers.Container(
        Services, config=config.services, repositories=repositories
    )

    master = providers.Container(Master, services=services, mappers=mappers)


if __name__ == "__main__":
    application = Application()
    application.wire(modules=[__name__])

    master_service = application.master()
    master_service.start()
