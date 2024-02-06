import os
import sys
from pprint import pprint
from typing import Dict

parent_directory = os.path.join(os.getcwd(), os.pardir)
sys.path.append(parent_directory)

from configurations.dotenv_file import DotenvSettings  # noqa
from configurations.ini_file import IniConfigSettings  # noqa
from configurations.yaml_file import YamlLoggingSettings  # noqa


def merge_dicts(*dicts: Dict) -> Dict:
    merged = {}
    for d in dicts:
        for key, value in d.items():
            if (
                key in merged
                and isinstance(merged[key], dict)
                and isinstance(value, dict)
            ):
                merged[key] = merge_dicts(merged[key], value)
            else:
                merged[key] = value
    return merged


if __name__ == "__main__":
    ROOT_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)
    )

    dotenv_settings = DotenvSettings(
        _env_file=os.path.join(ROOT_DIR, ".env")
    ).model_dump()
    config_ini_settings = IniConfigSettings(
        ini_file=os.path.join(ROOT_DIR, "config.ini"), root_dir=ROOT_DIR
    )
    logging_yaml_settings = YamlLoggingSettings(
        yaml_file=os.path.join(ROOT_DIR, "logging.yaml")
    )

    settings = merge_dicts(dotenv_settings, config_ini_settings, logging_yaml_settings)
    pprint(settings)
