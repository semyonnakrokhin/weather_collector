import asyncio
import os
from typing import Dict

from dependency_injector import containers

from configurations.dotenv_file import DotenvSettings
from configurations.ini_file import IniConfigSettings
from configurations.merged_config import merge_dicts
from configurations.yaml_file import YamlLoggingSettings
from di_container import Application
from master import MasterService

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))


def get_config_dict() -> Dict:
    """
    Retrieves and merges configuration settings from various sources.

    This function collects configuration settings from environment variables,
    INI configuration files, and YAML logging configuration files. It then merges
    these settings into a single dictionary.
    """

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

    return settings_dict


def create_app_container(config_dict: Dict) -> containers.DeclarativeContainer:
    """This function initializes an instance of the Application class,
    which is a container provided by the Dependency Injector framework.
    It retrieves configuration settings using the get_config_dict() function,
    configures the application with these settings,
    and initializes its resources."""

    application = Application()
    application.config.from_dict(config_dict)
    application.core.init_resources()

    return application


def create_master_service(
    app_container: containers.DeclarativeContainer,
) -> MasterService:
    """Creates and configures the master service."""

    master_service = app_container.master.master_service_provider()

    return master_service


async def main(app_container: containers.DeclarativeContainer) -> None:
    master_service = create_master_service(app_container=app_container)
    await master_service.start()


if __name__ == "__main__":
    settings_dict = get_config_dict()
    application_container = create_app_container(config_dict=settings_dict)
    asyncio.run(main(app_container=application_container))
