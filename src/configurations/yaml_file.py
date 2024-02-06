import os
from pprint import pprint
from typing import Dict

import yaml


class YamlSettings(Dict):
    def __new__(cls, yaml_file, *args, **kwargs):
        instance = super().__new__(cls, *args, **kwargs)
        instance.yaml_file = yaml_file
        return instance

    def __init__(self, *args, **kwargs):
        super().__init__(self.parse_logging_yaml())

    def parse_logging_yaml(self) -> Dict:
        with open(self.yaml_file, "r") as file:
            logging_config = yaml.safe_load(file)
        return logging_config


class YamlLoggingSettings(YamlSettings):
    def __init__(self, yaml_file: str, *args, **kwargs):
        super().__init__(yaml_file, *args, **kwargs)
        self.clear()
        self.update({"logging": self.parse_logging_yaml()})


if __name__ == "__main__":
    ROOT_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir)
    )
    logging_filepath = os.path.join(ROOT_DIR, "logging.yaml")
    logging_yaml_settings = YamlLoggingSettings(yaml_file=logging_filepath)

    pprint(logging_yaml_settings)
